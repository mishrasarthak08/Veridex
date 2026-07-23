"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatInput } from "../../components/chat/ChatInput";
import { MessageBubble, Message } from "../../components/chat/MessageBubble";
import { submitGoal, getTimelineUrl } from "../../lib/api";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am Veridex. I can help you search the knowledge base or execute complex agentic workflows. What would you like to do?",
      traces: [],
      isGenerating: false,
    }
  ]);
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Setup SSE Listener
  useEffect(() => {
    const es = new EventSource(getTimelineUrl());
    
    es.addEventListener("timeline_update", (e) => {
      try {
        const payload = JSON.parse(e.data);
        const timestamp = new Date();
        
        setMessages((prev) => {
          // Find the last assistant message that is currently generating
          const newMessages = [...prev];
          const lastMsgIdx = newMessages.length - 1;
          
          if (lastMsgIdx >= 0 && newMessages[lastMsgIdx].role === "assistant" && newMessages[lastMsgIdx].isGenerating) {
            const currentMsg = { ...newMessages[lastMsgIdx] };
            const newTraces = [...currentMsg.traces];
            
            if (payload.event === "task_started") {
              newTraces.push({ id: Math.random().toString(), time: timestamp, message: `Task started: ${payload.task_id}`, type: "info" });
            } else if (payload.event === "task_completed") {
              newTraces.push({ id: Math.random().toString(), time: timestamp, message: `Task completed: ${payload.task_id}`, type: "info" });
              if (payload.result) {
                // If there is a final result, append it to the content and stop generating!
                currentMsg.content += payload.result;
                currentMsg.isGenerating = false;
                setIsGenerating(false);
                newTraces.push({ id: Math.random().toString(), time: timestamp, message: "Task successful", type: "success" });
              }
            } else if (payload.event === "dag_created" && payload.dag) {
               newTraces.push({ id: Math.random().toString(), time: timestamp, message: `Orchestrator planned ${payload.dag.length} tasks`, type: "system" });
            }
            
            currentMsg.traces = newTraces;
            newMessages[lastMsgIdx] = currentMsg;
          }
          
          return newMessages;
        });
      } catch (err) {
        console.error("Error parsing SSE:", err);
      }
    });

    return () => es.close();
  }, []);

  const handleSend = async (content: string) => {
    const userMsgId = Date.now().toString();
    const assistantMsgId = (Date.now() + 1).toString();
    
    // 1. Add User Message
    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: "user", content, traces: [], isGenerating: false }
    ]);
    
    // 2. Add empty Assistant Message (Generating state)
    setMessages((prev) => [
      ...prev,
      { id: assistantMsgId, role: "assistant", content: "", traces: [], isGenerating: true }
    ]);
    
    setIsGenerating(true);

    try {
      await submitGoal(content);
      // We rely on the SSE events to populate the assistant message and mark it complete!
    } catch (err) {
      console.error(err);
      // Fallback on error
      setIsGenerating(false);
      setMessages((prev) => {
        const newMsgs = [...prev];
        const last = newMsgs[newMsgs.length - 1];
        last.isGenerating = false;
        last.content = "I'm sorry, I encountered an error while trying to process your request.";
        last.traces.push({ id: "error", time: new Date(), message: "Failed to submit goal", type: "error" });
        return newMsgs;
      });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <div className="flex items-center gap-4 text-sm">
          <span className="font-display font-bold tracking-widest text-[#F6F4EF]">VERIDEX CHAT</span>
        </div>
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
  );
}
