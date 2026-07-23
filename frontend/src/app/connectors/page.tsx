"use client";

import React, { useState } from "react";
import { Plug, Plus, Code, MessageSquare, Database, RefreshCw } from "lucide-react";
import { triggerSync } from "../../lib/api";

export default function ConnectorsPage() {
  const [isSyncing, setIsSyncing] = useState<number | null>(null);

  const connectors = [
    { id: 1, name: "GitHub Repository", icon: Code, status: "active", lastSync: "10 mins ago", type: "github", config: { repository_full_name: "test/repo" } },
    { id: 2, name: "Slack Workspace", icon: MessageSquare, status: "error", lastSync: "2 hours ago", type: "slack", config: {} },
    { id: 3, name: "Filesystem (Local)", icon: Database, status: "active", lastSync: "Just now", type: "filesystem", config: { directory_path: "./docs" } },
  ];

  const handleSync = async (id: number, type: string, config: any) => {
    setIsSyncing(id);
    try {
      await triggerSync(type, config);
      alert(`Sync triggered successfully for ${type}!`);
    } catch (err: any) {
      alert(`Failed to trigger sync: ${err.message}`);
    } finally {
      setIsSyncing(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF]">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <Plug size={16} className="text-[#4C9FE8]" />
          Data Connectors
        </h1>
        <button className="flex items-center gap-2 px-4 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] border border-[#4C9FE8]/20 hover:bg-[#4C9FE8]/20 transition-colors rounded-full text-xs font-mono">
          <Plus size={14} />
          New Connector
        </button>
      </header>

      <main className="flex-1 p-8 max-w-5xl mx-auto w-full">
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-white mb-2">Connected Sources</h2>
          <p className="text-sm text-white/40 font-mono">Manage integrations providing context to the orchestration engine.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {connectors.map((c) => {
            const Icon = c.icon;
            const isError = c.status === "error";
            const syncing = isSyncing === c.id;
            
            return (
              <div key={c.id} className="rounded-xl border border-white/5 bg-white/[0.02] p-5 hover:border-white/10 transition-colors group flex flex-col h-48 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1" style={{ backgroundColor: isError ? "#E54D2E" : "#2FAE86" }} />
                
                <div className="flex items-start justify-between mb-auto">
                  <div className={`p-3 rounded-lg bg-white/5 ${isError ? 'text-[#E54D2E]' : 'text-white/80'}`}>
                    <Icon size={24} />
                  </div>
                  <div className={`px-2 py-1 rounded font-mono text-[10px] border ${
                    isError 
                      ? 'border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E]' 
                      : 'border-[#2FAE86]/20 bg-[#2FAE86]/10 text-[#2FAE86]'
                  }`}>
                    {c.status.toUpperCase()}
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-display font-bold text-[#F6F4EF]">{c.name}</h3>
                    <button 
                      onClick={() => handleSync(c.id, c.type, c.config)}
                      disabled={syncing}
                      className="text-white/40 hover:text-[#4C9FE8] transition-colors"
                    >
                      <RefreshCw size={14} className={syncing ? "animate-spin text-[#4C9FE8]" : ""} />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 text-[11px] font-mono text-white/40">
                    <div className={`w-1.5 h-1.5 rounded-full ${isError ? 'bg-[#E54D2E]' : 'bg-[#2FAE86]'}`} />
                    Last sync: {c.lastSync}
                  </div>
                </div>
              </div>
            );
          })}
          
          <div className="rounded-xl border border-white/5 border-dashed bg-transparent p-5 hover:border-white/20 transition-colors flex flex-col items-center justify-center h-48 cursor-pointer text-white/40 hover:text-white/80">
            <Plus size={32} className="mb-4" />
            <span className="font-mono text-sm">Add New Source</span>
          </div>
        </div>
      </main>
    </div>
  );
}
