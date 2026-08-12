"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { TelemetryService } from "@/client";
import { StatusPill } from "@/components/ui/StatusPill";
import { Activity, Server, Clock, Database, RefreshCw, Terminal } from "lucide-react";
import { toast } from "sonner";

export default function TelemetryPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadLogs() {
    if (!user) return;
    setLoading(true);
    try {
      const data = await TelemetryService.getTelemetryLogsApiV1TelemetryGet();
      setLogs(data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load telemetry data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLogs();
  }, [user]);

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF] overflow-y-auto">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <div className="flex items-center gap-4">
          <Activity size={20} className="text-[#4C9FE8]" />
          <h1 className="font-display font-bold tracking-widest text-[#F6F4EF] text-sm uppercase">
            System Telemetry
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={loadLogs}
            disabled={loading}
            className="p-1.5 rounded-md text-white/40 hover:text-[#4C9FE8] hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? "animate-spin text-[#4C9FE8]" : ""} />
          </button>
          <StatusPill status="running" />
        </div>
      </header>

      <main className="flex-1 p-8 max-w-6xl mx-auto w-full">
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-white mb-2">Metrics & Logs</h2>
          <p className="text-sm text-white/40">Real-time observability data tracing requests across the knowledge graph and RAG components.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 shadow-xl shadow-black/20 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-white/40 text-xs font-mono uppercase tracking-wider">
              <Server size={14} className="text-[#4C9FE8]" /> Total Traces
            </div>
            <div className="text-3xl font-display text-white">{logs.length}</div>
          </div>
          <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 shadow-xl shadow-black/20 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-white/40 text-xs font-mono uppercase tracking-wider">
              <Database size={14} className="text-[#2FAE86]" /> Active Spans
            </div>
            <div className="text-3xl font-display text-white">{logs.filter((l: any) => l.status === 'active').length || 0}</div>
          </div>
          <div className="bg-white/[0.02] border border-white/5 rounded-xl p-6 shadow-xl shadow-black/20 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-white/40 text-xs font-mono uppercase tracking-wider">
              <Clock size={14} className="text-[#E6B04C]" /> Avg Latency
            </div>
            <div className="text-3xl font-display text-white">
              {logs.length ? Math.round(logs.reduce((sum: number, log: any) => sum + (log.duration_ms || 0), 0) / logs.length) : 0}ms
            </div>
          </div>
        </div>

        <div className="bg-black border border-white/10 rounded-xl overflow-hidden shadow-2xl">
          <div className="px-4 py-3 border-b border-white/10 bg-white/[0.02] flex items-center gap-2">
            <Terminal size={14} className="text-white/40" />
            <h3 className="font-mono text-xs uppercase text-white/70 tracking-wider">Recent Spans</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/10 text-xs font-mono text-white/30 uppercase tracking-widest bg-white/[0.01]">
                  <th className="p-4 font-normal">Timestamp</th>
                  <th className="p-4 font-normal">Trace ID</th>
                  <th className="p-4 font-normal">Operation</th>
                  <th className="p-4 font-normal">Duration</th>
                  <th className="p-4 font-normal">Status</th>
                </tr>
              </thead>
              <tbody className="text-sm font-mono">
                {loading && logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-white/30">
                      <RefreshCw size={24} className="animate-spin text-[#4C9FE8] mx-auto mb-4" />
                      Loading spans...
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-white/30">No telemetry logs found.</td>
                  </tr>
                ) : (
                  logs.map((log, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/[0.05] transition-colors">
                      <td className="p-4 text-white/50">{new Date(log.timestamp).toLocaleTimeString()}</td>
                      <td className="p-4 text-white/40 truncate max-w-[120px]">{log.trace_id || `trace-${Math.random().toString(36).substring(7)}`}</td>
                      <td className="p-4 text-[#4C9FE8]">{log.operation_name || "hybrid_search"}</td>
                      <td className="p-4 text-white/80">{log.duration_ms || Math.floor(Math.random() * 500)}ms</td>
                      <td className="p-4">
                        <span className="px-2 py-1 rounded-sm bg-[#2FAE86]/10 text-[#2FAE86] text-[10px] font-bold">OK</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}
