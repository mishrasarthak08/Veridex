"use client";

import React from "react";
import { XtermTerminal } from "@/components/terminal/XtermTerminal";
import { Terminal as TerminalIcon } from "lucide-react";

export default function TerminalPage() {
  return (
    <div className="w-full h-full bg-[#050608] flex flex-col relative">
      <div className="absolute top-0 w-full h-12 bg-[#0B0E12] border-b border-white/10 flex items-center px-4 z-10 shadow-md">
        <TerminalIcon size={16} className="text-[#4C9FE8] mr-2" />
        <span className="text-sm font-mono text-white/80">root@veridex-os ~ Developer Command Center</span>
      </div>
      <div className="flex-1 mt-12 overflow-hidden bg-[#050608]">
        <XtermTerminal />
      </div>
    </div>
  );
}
