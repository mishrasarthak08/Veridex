import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "inherit";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || disabled) return;
    
    onSend(input);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative">
      <div className="absolute -inset-1 bg-gradient-to-r from-[#4C9FE8]/20 to-[#2FAE86]/20 rounded-2xl blur-xl opacity-50 pointer-events-none" />
      <form 
        onSubmit={handleSubmit}
        className="relative flex items-end gap-3 bg-[#141820] border border-white/10 rounded-2xl p-2 shadow-2xl transition-colors focus-within:border-white/20"
      >
        <div className="pl-3 pb-2 text-white/30">
          <Sparkles size={20} />
        </div>
        
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask Veridex anything..."
          className="flex-1 max-h-[200px] min-h-[40px] bg-transparent resize-none outline-none py-2 text-[#F6F4EF] placeholder:text-white/20 font-body text-[15px] scrollbar-hide"
          rows={1}
        />
        
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="shrink-0 w-10 h-10 rounded-xl bg-[#4C9FE8] text-black flex items-center justify-center hover:bg-[#4C9FE8]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <Send size={18} className="mr-0.5" />
        </button>
      </form>
    </div>
  );
}
