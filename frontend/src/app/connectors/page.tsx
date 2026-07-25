"use client";

import React, { useState, useEffect } from "react";
import { Plug, Plus, Code, MessageSquare, Database, RefreshCw, Trash2, X } from "lucide-react";
import { triggerSync } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";

interface Connector {
  id: string;
  name: string;
  source_type: string;
  config_data: any;
  is_active: boolean;
}

export default function ConnectorsPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [isSyncing, setIsSyncing] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newConnectorName, setNewConnectorName] = useState("");
  const [newConnectorType, setNewConnectorType] = useState("github");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { token } = useAuth();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

  const fetchConnectors = async () => {
    setIsLoading(true);
    setError("");
    try {
      const res = await fetch(`${apiUrl}/connectors/`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (!res.ok) throw new Error("Failed to fetch connectors");
      const data = await res.json();
      setConnectors(data.data || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchConnectors();
    }
  }, [token]);

  const handleSync = async (id: string, type: string, config: any) => {
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

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this connector?")) return;
    
    try {
      const res = await fetch(`${apiUrl}/connectors/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      if (!res.ok) throw new Error("Failed to delete connector");
      
      setConnectors(connectors.filter(c => c.id !== id));
    } catch (err: any) {
      alert(`Error deleting connector: ${err.message}`);
    }
  };

  const handleAddConnector = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await fetch(`${apiUrl}/connectors/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newConnectorName,
          source_type: newConnectorType,
          config_data: {},
          is_active: true
        })
      });
      
      if (!res.ok) throw new Error("Failed to create connector");
      
      const data = await res.json();
      setConnectors([...connectors, data.data]);
      setIsModalOpen(false);
      setNewConnectorName("");
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getIconForType = (type: string) => {
    switch (type) {
      case "github": return Code;
      case "slack": return MessageSquare;
      default: return Database;
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF]">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <Plug size={16} className="text-[#4C9FE8]" />
          Data Connectors
        </h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] border border-[#4C9FE8]/20 hover:bg-[#4C9FE8]/20 transition-colors rounded-full text-xs font-mono"
        >
          <Plus size={14} />
          New Connector
        </button>
      </header>

      <main className="flex-1 p-8 max-w-5xl mx-auto w-full">
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-white mb-2">Connected Sources</h2>
          <p className="text-sm text-white/40 font-mono">Manage integrations providing context to the orchestration engine.</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg border border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E]">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center items-center h-48">
            <RefreshCw size={24} className="animate-spin text-[#4C9FE8]" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {connectors.map((c) => {
              const Icon = getIconForType(c.source_type);
              const isError = !c.is_active;
              const syncing = isSyncing === c.id;
              
              return (
                <div key={c.id} className="rounded-xl border border-white/5 bg-white/[0.02] p-5 hover:border-white/10 transition-colors group flex flex-col h-48 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1" style={{ backgroundColor: isError ? "#E54D2E" : "#2FAE86" }} />
                  
                  <div className="flex items-start justify-between mb-auto">
                    <div className={`p-3 rounded-lg bg-white/5 ${isError ? 'text-[#E54D2E]' : 'text-white/80'}`}>
                      <Icon size={24} />
                    </div>
                    <div className="flex gap-2">
                      <div className={`px-2 py-1 rounded font-mono text-[10px] border ${
                        isError 
                          ? 'border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E]' 
                          : 'border-[#2FAE86]/20 bg-[#2FAE86]/10 text-[#2FAE86]'
                      }`}>
                        {c.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-display font-bold text-[#F6F4EF]">{c.name}</h3>
                      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleSync(c.id, c.source_type, c.config_data)}
                          disabled={syncing}
                          className="text-white/40 hover:text-[#4C9FE8] transition-colors"
                          title="Sync Now"
                        >
                          <RefreshCw size={14} className={syncing ? "animate-spin text-[#4C9FE8]" : ""} />
                        </button>
                        <button 
                          onClick={() => handleDelete(c.id)}
                          className="text-white/40 hover:text-[#E54D2E] transition-colors"
                          title="Delete Connector"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] font-mono text-white/40">
                      <div className={`w-1.5 h-1.5 rounded-full ${isError ? 'bg-[#E54D2E]' : 'bg-[#2FAE86]'}`} />
                      Type: {c.source_type}
                    </div>
                  </div>
                </div>
              );
            })}
            
            <div 
              onClick={() => setIsModalOpen(true)}
              className="rounded-xl border border-white/5 border-dashed bg-transparent p-5 hover:border-white/20 transition-colors flex flex-col items-center justify-center h-48 cursor-pointer text-white/40 hover:text-white/80"
            >
              <Plus size={32} className="mb-4" />
              <span className="font-mono text-sm">Add New Source</span>
            </div>
          </div>
        )}
      </main>

      {/* Add Connector Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[#0B0E12] border border-white/10 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-white/40 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>
            
            <h3 className="text-xl font-display font-bold mb-6">Add New Connector</h3>
            
            <form onSubmit={handleAddConnector} className="space-y-4">
              <div>
                <label className="block text-sm text-white/60 mb-1">Connector Name</label>
                <input
                  type="text"
                  required
                  value={newConnectorName}
                  onChange={(e) => setNewConnectorName(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-[#4C9FE8]/50"
                  placeholder="e.g. Engineering Slack"
                />
              </div>
              
              <div>
                <label className="block text-sm text-white/60 mb-1">Source Type</label>
                <select
                  value={newConnectorType}
                  onChange={(e) => setNewConnectorType(e.target.value)}
                  className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-[#4C9FE8]/50"
                >
                  <option value="github">GitHub</option>
                  <option value="slack">Slack</option>
                  <option value="notion">Notion</option>
                  <option value="jira">Jira</option>
                  <option value="filesystem">Local Filesystem</option>
                </select>
              </div>

              <div className="pt-4 flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-lg text-sm font-bold bg-[#4C9FE8] text-black hover:bg-[#4C9FE8]/90 transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Creating..." : "Create Connector"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
