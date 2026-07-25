import React from "react";
import { AlertOctagon, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ title = "Something went wrong", message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full py-16 px-4 text-center border border-[#E54D2E]/20 rounded-2xl bg-[#E54D2E]/5">
      <div className="w-16 h-16 rounded-full bg-[#E54D2E]/10 flex items-center justify-center text-[#E54D2E] mb-6">
        <AlertOctagon size={32} strokeWidth={1.5} />
      </div>
      <h3 className="text-[#F6F4EF] font-display font-semibold text-lg mb-2">{title}</h3>
      <p className="text-[#E54D2E]/80 font-mono text-sm max-w-sm mb-8 leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors font-mono text-xs"
        >
          <RefreshCw size={14} />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
}
