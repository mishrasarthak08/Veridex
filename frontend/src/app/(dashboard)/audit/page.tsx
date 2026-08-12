"use client";

import React, { useState, useEffect } from "react";
import { List, Search, Clock, User, ShieldAlert, FileJson } from "lucide-react";
import { OpenAPI } from "@/services/api";

export default function AuditLogPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<any | null>(null);

  useEffect(() => {
    fetch(OpenAPI.BASE + "/api/v1/governance/audit-log?limit=100", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "X-Tenant-ID": localStorage.getItem("activeTenant") || "default_tenant"
      }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setLogs(data);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF] overflow-hidden">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <List size={16} className="text-[#2FAE86]" />
          Audit Log Explorer
        </h1>
      </header>

      <main className="flex-1 flex overflow-hidden">
        {/* Table View */}
        <div className={`flex-1 overflow-y-auto p-6 transition-all ${selectedLog ? 'pr-96' : ''}`}>
          <div className="rounded-xl border border-white/5 bg-white/[0.02] shadow-2xl shadow-black/50 overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.02] sticky top-0">
                <tr className="border-b border-white/5 text-white/50">
                  <th className="py-3 px-4 font-medium"><Clock size={14} className="inline mr-2"/>Time</th>
                  <th className="py-3 px-4 font-medium"><User size={14} className="inline mr-2"/>Actor</th>
                  <th className="py-3 px-4 font-medium">Action</th>
                  <th className="py-3 px-4 font-medium">Resource</th>
                  <th className="py-3 px-4 font-medium">Decision</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={5} className="py-8 text-center text-white/40">Loading audit events...</td></tr>
                )}
                {!loading && logs.length === 0 && (
                  <tr><td colSpan={5} className="py-8 text-center text-white/40">No events recorded.</td></tr>
                )}
                {logs.map((log: any, idx) => (
                  <tr 
                    key={idx} 
                    onClick={() => setSelectedLog(log)}
                    className={`border-b border-white/5 cursor-pointer transition-colors ${selectedLog === log ? 'bg-white/10' : 'hover:bg-white/5'}`}
                  >
                    <td className="py-3 px-4 text-white/70 font-mono text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="py-3 px-4 text-[#4C9FE8]">{log.actor?.substring(0, 8)}...</td>
                    <td className="py-3 px-4 font-mono text-xs">{log.action}</td>
                    <td className="py-3 px-4 text-white/80">{log.resource}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider font-bold ${
                        log.decision === 'ALLOW' ? 'bg-[#2FAE86]/20 text-[#2FAE86]' : 'bg-[#E64C4C]/20 text-[#E64C4C]'
                      }`}>
                        {log.decision}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail Drawer */}
        {selectedLog && (
          <aside className="w-96 border-l border-white/5 bg-[#0B0E12] absolute right-0 top-[61px] bottom-0 overflow-y-auto p-6 shadow-2xl z-20">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-display font-bold text-white flex items-center gap-2">
                <FileJson size={16} className="text-[#4C9FE8]" />
                Event Details
              </h3>
              <button onClick={() => setSelectedLog(null)} className="text-white/40 hover:text-white">✕</button>
            </div>
            
            <div className="bg-[#050608] rounded-lg border border-white/10 p-4 overflow-x-auto">
              <pre className="text-xs font-mono text-[#F6F4EF]/80">
                {JSON.stringify(selectedLog, null, 2)}
              </pre>
            </div>
            
            <div className="mt-6">
              <h4 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-2">Policy Resolution</h4>
              <p className="text-sm text-white/80">
                Rule triggered: <span className="font-mono text-[#EAB308]">{selectedLog.policy_id}</span>
              </p>
              {selectedLog.details?.policy_reason && (
                <p className="text-sm text-white/50 mt-2 italic">"{selectedLog.details.policy_reason}"</p>
              )}
            </div>
          </aside>
        )}
      </main>
    </div>
  );
}
