"use client";

import React, { useState } from "react";
import { ShieldAlert, Zap, ServerOff, Play, RefreshCw, AlertTriangle } from "lucide-react";
import { runChaosTest } from "../../lib/api";

export default function ResiliencePage() {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<{time: string, message: string, type: string}[]>([]);

  const handleRunChaos = async () => {
    setIsRunning(true);
    setLogs([
      { time: new Date().toLocaleTimeString(), message: "Initializing Chaos Engineering Suite...", type: "system" }
    ]);
    
    try {
      await runChaosTest();
      
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const es = new EventSource(`${API_BASE_URL}/resilience/chaos/stream`);
      
      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          appendLog(data.message, data.type);
          if (data.message.includes("Chaos test complete")) {
            setIsRunning(false);
            es.close();
          }
        } catch (err) {
          console.error(err);
        }
      };

      es.onerror = () => {
        es.close();
        setIsRunning(false);
      };

    } catch (err) {
      appendLog("Failed to initiate chaos test.", "error");
      setIsRunning(false);
    }
  };

  const appendLog = (msg: string, type: string) => {
    setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), message: msg, type }]);
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF]">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <ShieldAlert size={16} className="text-[#E54D2E]" />
          Resilience & Chaos Engineering
        </h1>
        <button 
          onClick={handleRunChaos}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-1.5 bg-[#E54D2E]/10 text-[#E54D2E] border border-[#E54D2E]/20 hover:bg-[#E54D2E]/20 transition-colors rounded-full text-xs font-mono disabled:opacity-50"
        >
          {isRunning ? (
            <RefreshCw size={14} className="animate-spin" />
          ) : (
            <Zap size={14} />
          )}
          Trigger Chaos
        </button>
      </header>

      <main className="flex-1 p-8 max-w-5xl mx-auto w-full flex flex-col gap-8">
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="rounded-xl border border-[#E54D2E]/20 bg-[#E54D2E]/5 p-5 relative overflow-hidden group hover:border-[#E54D2E]/40 transition-colors cursor-pointer">
            <div className="text-[#E54D2E] mb-2"><ServerOff size={24} /></div>
            <div className="font-display font-bold text-white mb-1">Kill Worker Node</div>
            <div className="text-[10px] font-mono text-white/50">Simulates sudden instance termination</div>
          </div>
          
          <div className="rounded-xl border border-[#F5A623]/20 bg-[#F5A623]/5 p-5 relative overflow-hidden group hover:border-[#F5A623]/40 transition-colors cursor-pointer">
            <div className="text-[#F5A623] mb-2"><AlertTriangle size={24} /></div>
            <div className="font-display font-bold text-white mb-1">Network Partition</div>
            <div className="text-[10px] font-mono text-white/50">Simulates split-brain scenario</div>
          </div>
          
          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5 relative overflow-hidden group hover:border-white/10 transition-colors cursor-pointer">
            <div className="text-white/40 mb-2"><Zap size={24} /></div>
            <div className="font-display font-bold text-white mb-1">Istio Faults</div>
            <div className="text-[10px] font-mono text-white/50">Inject 500s or HTTP delays</div>
          </div>
          
          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5 relative overflow-hidden group hover:border-white/10 transition-colors cursor-pointer">
            <div className="text-white/40 mb-2"><RefreshCw size={24} /></div>
            <div className="font-display font-bold text-white mb-1">DB Failover</div>
            <div className="text-[10px] font-mono text-white/50">Force primary DB switch</div>
          </div>
        </div>

        <div className="flex-1 rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden flex flex-col shadow-2xl shadow-black/50">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.01]">
            <h3 className="font-mono text-xs text-white/60">Chaos Test Execution Logs</h3>
          </div>
          
          <div className="flex-1 overflow-auto p-6 font-mono text-sm space-y-2">
            {logs.length === 0 ? (
              <div className="h-full flex items-center justify-center text-white/20">
                Ready to unleash chaos.
              </div>
            ) : (
              logs.map((log, idx) => (
                <div key={idx} className="flex items-start gap-4">
                  <span className="text-white/30 shrink-0 text-xs mt-0.5">{log.time}</span>
                  <span className={
                    log.type === 'system' ? 'text-white/60' :
                    log.type === 'warning' ? 'text-[#F5A623]' :
                    log.type === 'error' ? 'text-[#E54D2E]' :
                    log.type === 'success' ? 'text-[#2FAE86] font-bold' :
                    'text-[#4C9FE8]'
                  }>
                    {log.message}
                  </span>
                </div>
              ))
            )}
            {isRunning && (
              <div className="flex items-center gap-2 text-white/40 mt-4">
                <span className="animate-pulse">_</span>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
