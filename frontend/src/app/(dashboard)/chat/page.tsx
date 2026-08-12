"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageBubble, Message } from "@/components/chat/MessageBubble";
import { submitGoal, getTimelineUrl, fetchChatHistory, saveChatMessage, fetchChatThreads } from "@/lib/api";
import { ExecutionTimeline } from "@/components/agents/ExecutionTimeline";
import { useAuth } from "@/context/AuthContext";
import { MessageSquarePlus, MessageSquare, Menu, X, Clock } from "lucide-react";

interface Thread {
  thread_id: string;
  last_updated: string;
}

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string>("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTimelineOpen, setIsTimelineOpen] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize and load threads
  useEffect(() => {
    async function loadThreads() {
      if (user) {
        try {
          const fetchedThreads = await fetchChatThreads();
          setThreads(fetchedThreads);
          
          if (fetchedThreads.length > 0) {
            setActiveThreadId(fetchedThreads[0].thread_id);
          } else {
            handleNewChat();
          }
        } catch (e) {
          console.error("Failed to load threads", e);
          handleNewChat();
        }
      }
    }
    loadThreads();
  }, [user]);

  const [abortController, setAbortController] = useState<AbortController | null>(null);

  // Load history when active thread changes
  useEffect(() => {
    async function loadHistory() {
      if (user && activeThreadId) {
        setMessages([]); // Clear while loading
        try {
          const history = await fetchChatHistory(activeThreadId);
          if (history && history.length > 0) {
            setMessages(history);
          } else {
            setMessages([
              {
                id: "welcome",
                role: "assistant",
                content: "Hello! I am Veridex. I can help you search the knowledge base or execute complex agentic workflows. What would you like to do?",
                traces: [],
                isGenerating: false,
              }
            ]);
          }
        } catch (e) {
          console.error("Failed to load history", e);
        }
      }
    }
    loadHistory();
  }, [user, activeThreadId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewChat = () => {
    const newId = `thread-${Date.now()}`;
    setActiveThreadId(newId);
    setThreads(prev => [{ thread_id: newId, last_updated: new Date().toISOString() }, ...prev]);
  };

  const handleStop = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsGenerating(false);
      setMessages((prev) => {
        const newMsgs = [...prev];
        const last = newMsgs[newMsgs.length - 1];
        if (last && last.isGenerating) {
          last.isGenerating = false;
        }
        return newMsgs;
      });
    }
  };

  const handleSend = async (content: string) => {
    if (!activeThreadId) return;

    const userMsgId = Date.now().toString();
    const assistantMsgId = (Date.now() + 1).toString();
    
    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: "user", content, traces: [], isGenerating: false },
      { id: assistantMsgId, role: "assistant", content: "", traces: [], isGenerating: true }
    ]);
    
    setIsGenerating(true);
    const controller = new AbortController();
    setAbortController(controller);

    try {
      const token = localStorage.getItem("token");
      const { API_URL } = await import("@/lib/api");
      const response = await fetch(`${API_URL}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          thread_id: activeThreadId,
          role: "user",
          content: content,
          traces: []
        }),
        signal: controller.signal
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const payload = JSON.parse(line.slice(6));
              const timestamp = new Date();
              
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                if (lastIdx >= 0 && newMessages[lastIdx].id === assistantMsgId) {
                  const currentMsg = { ...newMessages[lastIdx] };
                  
                  if (payload.event === "task_started") {
                    currentMsg.traces = [...currentMsg.traces, { id: Math.random().toString(), time: timestamp, message: `Task started: ${payload.task_id}`, type: "info" }];
                  } else if (payload.event === "task_completed") {
                    if (payload.result) {
                      assistantContent += payload.result;
                      currentMsg.content = assistantContent;
                    } else {
                       currentMsg.traces = [...currentMsg.traces, { id: Math.random().toString(), time: timestamp, message: `Task completed: ${payload.task_id}`, type: "success" }];
                    }
                  } else if (payload.event === "task_failed") {
                    currentMsg.traces = [...currentMsg.traces, { id: Math.random().toString(), time: timestamp, message: `Task failed: ${payload.error}`, type: "error" }];
                  }
                  
                  newMessages[lastIdx] = currentMsg;
                }
                return newMessages;
              });
            } catch(e) {}
          }
        }
      }
      
      setMessages((prev) => {
        const newMsgs = [...prev];
        const last = newMsgs[newMsgs.length - 1];
        if (last && last.id === assistantMsgId) last.isGenerating = false;
        return newMsgs;
      });
      setIsGenerating(false);
      setAbortController(null);
      
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log("Fetch aborted");
      } else {
        console.error(err);
        setMessages((prev) => {
          const newMsgs = [...prev];
          const last = newMsgs[newMsgs.length - 1];
          last.isGenerating = false;
          last.content = "I'm sorry, I encountered an error while trying to process your request.";
          last.traces.push({ id: "error", time: new Date(), message: "Failed to fetch stream", type: "error" });
          return newMsgs;
        });
      }
      setIsGenerating(false);
      setAbortController(null);
    }
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + date.toLocaleDateString();
  };

  return (
    <div className="flex h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30 overflow-hidden">
      
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 ease-in-out shrink-0 border-r border-white/5 bg-[#0B0E12]/80 flex flex-col overflow-hidden`}>
        <div className="p-4">
          <button 
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 bg-[#4C9FE8]/10 hover:bg-[#4C9FE8]/20 text-[#4C9FE8] border border-[#4C9FE8]/20 transition-colors py-2 rounded-lg font-mono text-xs"
          >
            <MessageSquarePlus size={16} />
            New Chat
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
          {threads.map((thread) => (
            <button
              key={thread.thread_id}
              onClick={() => setActiveThreadId(thread.thread_id)}
              className={`w-full text-left px-3 py-3 rounded-lg flex flex-col gap-1 transition-colors ${
                activeThreadId === thread.thread_id ? 'bg-white/10' : 'hover:bg-white/5'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare size={14} className={activeThreadId === thread.thread_id ? 'text-[#4C9FE8]' : 'text-white/40'} />
                <span className="text-sm font-medium truncate text-white/80">
                  {thread.thread_id.startsWith('thread-') ? 'New Conversation' : thread.thread_id.substring(0, 8) + '...'}
                </span>
              </div>
              <div className="flex items-center gap-1 text-[10px] text-white/40 font-mono ml-5">
                <Clock size={10} />
                {formatDate(thread.last_updated)}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="px-6 py-4 flex items-center gap-4 border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="text-white/60 hover:text-white transition-colors"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <span className="font-display font-bold tracking-widest text-[#F6F4EF] text-sm flex-1">
            VERIDEX CHAT
          </span>
          <button 
            onClick={() => setIsTimelineOpen(!isTimelineOpen)}
            className={`flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-lg transition-colors border ${isTimelineOpen ? 'bg-[#4C9FE8]/10 text-[#4C9FE8] border-[#4C9FE8]/20' : 'bg-white/5 text-white/60 border-white/10 hover:bg-white/10 hover:text-white'}`}
          >
            <Clock size={14} />
            TIMELINE
          </button>
        </header>
        
        <main className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-3xl mx-auto flex flex-col gap-8">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        </main>

        <footer className="px-6 py-6 bg-gradient-to-t from-[#0B0E12] to-transparent sticky bottom-0 z-10 shrink-0">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={handleSend} disabled={isGenerating} />
            <div className="text-center mt-3 font-mono text-[10px] text-white/30">
              AI can make mistakes. Verify critical information.
            </div>
          </div>
        </footer>
      </div>

      {/* Right Sidebar - Execution Timeline */}
      <div className={`${isTimelineOpen ? 'w-80' : 'w-0'} transition-all duration-300 ease-in-out shrink-0 border-l border-white/5 bg-[#0B0E12]/80 flex flex-col overflow-hidden`}>
        <div className="p-4 h-full">
          <ExecutionTimeline />
        </div>
      </div>
    </div>
  );
}
