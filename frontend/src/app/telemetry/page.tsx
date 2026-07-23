"use client";

import React, { useState, useEffect } from "react";
import { Activity, ServerCrash, RefreshCw } from "lucide-react";
import { fetchTelemetry } from "../../lib/api";

export default function TelemetryPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchTelemetry();
      setLogs(data || []);
    } catch (err: any) {
      setError(err.message || "Failed to load telemetry");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalCost = logs.reduce((acc, log) => acc + (log.cost_usd || 0), 0);
  const totalTokens = logs.reduce((acc, log) => acc + (log.prompt_tokens || 0) + (log.completion_tokens || 0), 0);

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF]">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <Activity size={16} className="text-[#4C9FE8]" />
          AI Telemetry & Evaluation
        </h1>
        <button 
          onClick={loadData}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] border border-[#4C9FE8]/20 hover:bg-[#4C9FE8]/20 transition-colors rounded-full text-xs font-mono disabled:opacity-50"
        >
          <RefreshCw size={14} className={isLoading ? "animate-spin" : ""} />
          Refresh
        </button>
      </header>

      <main className="flex-1 p-8 max-w-5xl mx-auto w-full flex flex-col">
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
           <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
             <div className="text-white/40 font-mono text-xs mb-1">Total API Cost</div>
             <div className="text-2xl font-display font-bold text-[#F5A623]">
               ${totalCost.toFixed(4)}
             </div>
           </div>
           <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
             <div className="text-white/40 font-mono text-xs mb-1">Total Tokens Processed</div>
             <div className="text-2xl font-display font-bold text-[#2FAE86]">
               {totalTokens.toLocaleString()}
             </div>
           </div>
           <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
             <div className="text-white/40 font-mono text-xs mb-1">Total Requests</div>
             <div className="text-2xl font-display font-bold text-[#4C9FE8]">
               {logs.length}
             </div>
           </div>
        </div>

        <div className="flex-1 rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden flex flex-col shadow-2xl shadow-black/50">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.01]">
            <h3 className="font-mono text-xs text-white/60">AILog Entries (PostgreSQL)</h3>
          </div>
          
          <div className="flex-1 overflow-auto p-0">
            {isLoading ? (
              <div className="h-full flex items-center justify-center text-white/20 font-mono text-sm">
                Fetching logs...
              </div>
            ) : error ? (
              <div className="h-full flex flex-col items-center justify-center text-[#E54D2E]/80 font-mono text-sm gap-3">
                <ServerCrash size={24} />
                {error}
                <span className="text-[10px] text-white/40">(Hint: Check auth token or backend status)</span>
              </div>
            ) : logs.length === 0 ? (
              <div className="h-full flex items-center justify-center text-white/20 font-mono text-sm">
                No telemetry logs found.
              </div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5 text-[10px] uppercase font-mono text-white/40 bg-white/[0.02]">
                    <th className="px-6 py-3 font-normal">Timestamp</th>
                    <th className="px-6 py-3 font-normal">Model</th>
                    <th className="px-6 py-3 font-normal">Tokens (P/C)</th>
                    <th className="px-6 py-3 font-normal">Cost</th>
                    <th className="px-6 py-3 font-normal">Latency</th>
                  </tr>
                </thead>
                <tbody className="text-xs font-mono text-white/80 divide-y divide-white/5">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4 text-white/40">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-[#4C9FE8]">{log.model}</td>
                      <td className="px-6 py-4">
                        {log.prompt_tokens} / {log.completion_tokens}
                      </td>
                      <td className="px-6 py-4 text-[#F5A623]">
                        ${(log.cost_usd || 0).toFixed(4)}
                      </td>
                      <td className="px-6 py-4">
                        {(log.latency_ms || 0).toFixed(0)}ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
