"use client";

import React, { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "@xterm/addon-fit";
import "xterm/css/xterm.css";
import { useWebSocket } from "@/context/WebSocketContext";

export function XtermTerminal() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const { traces } = useWebSocket();
  const renderedTraces = useRef(new Set<string>());

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new Terminal({
      theme: {
        background: '#050608',
        foreground: '#F6F4EF',
        cursor: '#4C9FE8',
        selectionBackground: 'rgba(76, 159, 232, 0.3)',
      },
      fontFamily: 'var(--font-jetbrains-mono), monospace',
      fontSize: 12,
      cursorBlink: true,
      disableStdin: true,
    });
    
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();
    
    term.writeln("\x1b[1;36m[VERIDEX COGNITIVE OS]\x1b[0m Terminal initialized.");
    term.writeln("\x1b[1;30m--------------------------------------------------\x1b[0m");

    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    const handleResize = () => fitAddon.fit();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      term.dispose();
    };
  }, []);

  // Sync traces to terminal
  useEffect(() => {
    if (!xtermRef.current) return;
    const term = xtermRef.current;

    // We only want to print *new* traces that we haven't printed yet
    traces.forEach((trace, idx) => {
      const traceId = trace.time.toISOString() + "-" + idx;
      if (!renderedTraces.current.has(traceId)) {
        renderedTraces.current.add(traceId);
        const timeStr = trace.time.toLocaleTimeString([], { hour12: false });
        
        let color = "\x1b[37m"; // white
        if (trace.type === 'system') color = "\x1b[33m"; // yellow
        if (trace.type === 'success') color = "\x1b[32m"; // green
        if (trace.type === 'error') color = "\x1b[31m"; // red

        term.writeln(`\x1b[90m[${timeStr}]\x1b[0m ${color}${trace.message}\x1b[0m`);
      }
    });
  }, [traces]);

  return <div ref={terminalRef} className="w-full h-full p-4" />;
}
