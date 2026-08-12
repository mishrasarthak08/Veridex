import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Bot, User, ChevronDown, ChevronRight, CheckCircle2, Loader2, AlertCircle, Copy, Check } from "lucide-react";
import { GenUIChart } from "./GenUIChart";

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

const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
  const match = /language-(\w+)/.exec(className || '');
  const [copied, setCopied] = useState(false);

  // Intercept 'chart' language for GenUI 
  if (match && match[1] === 'chart') {
    try {
      const data = JSON.parse(String(children).replace(/\n$/, ''));
      return <GenUIChart data={data} />;
    } catch (e) {
      return <div className="text-red-500 text-xs">Failed to parse GenUI Chart Data</div>;
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!inline && match) {
    return (
      <div className="relative group rounded-md overflow-hidden my-4 border border-white/10">
        <div className="flex items-center justify-between px-4 py-1.5 bg-[#0B0E12] border-b border-white/5">
          <span className="text-xs font-mono text-white/50">{match[1]}</span>
          <button 
            onClick={handleCopy}
            className="text-white/40 hover:text-white transition-colors p-1 rounded-md hover:bg-white/10"
          >
            {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
          </button>
        </div>
        <SyntaxHighlighter
          style={vscDarkPlus as any}
          language={match[1]}
          PreTag="div"
          customStyle={{ margin: 0, borderRadius: 0, background: '#0B0E12' }}
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      </div>
    );
  }
  return (
    <code className="bg-black/30 rounded px-1.5 py-0.5 text-sm font-mono text-[#4C9FE8]" {...props}>
      {children}
    </code>
  );
};

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
          <div className={`text-sm ${isUser ? "" : "prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-transparent prose-pre:p-0 prose-pre:m-0"}`}>
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                code: CodeBlock as any
              }}
            >
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
              aria-expanded={showTraces}
              aria-controls={`traces-panel-${message.id}`}
              className="flex items-center gap-1.5 text-xs font-mono text-white/40 hover:text-white/70 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4C9FE8]/50 rounded px-1"
            >
              {showTraces ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              View Reasoning Traces ({message.traces.length})
            </button>
            
            <AnimatePresence>
              {showTraces && (
                <motion.div
                  id={`traces-panel-${message.id}`}
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden mt-2"
                >
                  <div className="p-3 bg-black/40 border border-white/5 rounded-lg space-y-2">
                    {message.traces.map((trace, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-[11px] font-mono">
                        <span className="text-white/30 shrink-0 mt-0.5">
                          {new Date(trace.time).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
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
