import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, ChevronDown, ChevronRight, CheckCircle2, Loader2, AlertCircle } from "lucide-react";

export type Trace = {
  id: string;
  message: string;
  time: Date;
  type: "info" | "tool" | "system" | "success" | "error";
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  traces: Trace[];
  isGenerating: boolean;
};

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [showTraces, setShowTraces] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 w-full ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? "bg-[#4C9FE8]/20 text-[#4C9FE8]" : "bg-[#2FAE86]/20 text-[#2FAE86]"}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Bubble */}
      <div className={`flex flex-col max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <div className={`px-5 py-3.5 rounded-2xl ${isUser ? "bg-[#4C9FE8] text-black rounded-tr-sm" : "bg-[#141820] border border-white/10 text-[#F6F4EF] rounded-tl-sm"}`}>
          <div className={`text-sm ${isUser ? "" : "prose prose-invert prose-p:leading-relaxed prose-pre:bg-black/50"}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
          
          {message.isGenerating && (
            <div className="flex items-center gap-2 mt-2 text-white/50 text-xs font-mono">
              <Loader2 size={12} className="animate-spin" />
              <span>Agent is thinking...</span>
            </div>
          )}
        </div>

        {/* Traces Collapsible (only for assistant) */}
        {!isUser && message.traces.length > 0 && (
          <div className="mt-2 w-full max-w-sm">
            <button
              onClick={() => setShowTraces(!showTraces)}
              className="flex items-center gap-1.5 text-xs font-mono text-white/40 hover:text-white/70 transition-colors"
            >
              {showTraces ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              View Reasoning Traces ({message.traces.length})
            </button>
            
            <AnimatePresence>
              {showTraces && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden mt-2"
                >
                  <div className="p-3 bg-black/40 border border-white/5 rounded-lg space-y-2">
                    {message.traces.map((trace, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-[11px] font-mono">
                        <span className="text-white/30 shrink-0 mt-0.5">
                          {trace.time.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
                        </span>
                        <span className={
                          trace.type === "system" ? "text-[#F5A623]" :
                          trace.type === "success" ? "text-[#2FAE86]" :
                          trace.type === "error" ? "text-[#E54D2E]" :
                          "text-white/60"
                        }>
                          {trace.message}
                        </span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  );
}
