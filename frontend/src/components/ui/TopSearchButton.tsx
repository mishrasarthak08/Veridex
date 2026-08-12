"use client";
import React from "react";
import { Search } from "lucide-react";

export function TopSearchButton() {
  return (
    <button 
      className="flex items-center gap-2 text-sm text-white/40 hover:text-white/80 bg-white/5 border border-white/10 hover:border-white/20 px-3 py-1.5 rounded-md transition-colors"
      onClick={() => {
        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true }));
      }}
    >
      <Search size={14} />
      <span className="font-mono">Search or jump to...</span>
      <kbd className="ml-4 font-sans text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/50">⌘K</kbd>
    </button>
  );
}
