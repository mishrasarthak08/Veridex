"use client";

import React, { useState, useEffect } from "react";
import { Plug, Plus, Code, MessageSquare, Database, RefreshCw, Trash2, X } from "lucide-react";
import { ConnectorsService, KnowledgeService } from "@/client";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";

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
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newConnectorName, setNewConnectorName] = useState("");
  const [newConnectorType, setNewConnectorType] = useState("github");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { user } = useAuth();

  const fetchConnectors = async () => {
    setIsLoading(true);
    try {
      const res = await ConnectorsService.listConnectorsApiV1ConnectorsGet();
      setConnectors(res.data || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load connectors");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchConnectors();
    }
  }, [user]);

  const handleSync = async (id: string, type: string, config: any) => {
    setIsSyncing(id);
    try {
      await KnowledgeService.triggerSyncApiV1KnowledgeSyncPost({
        connector_type: type,
        config: config
      });
      toast.success(`Sync triggered successfully for ${type}!`);
    } catch (err: any) {
      toast.error(`Failed to trigger sync: ${err.message}`);
    } finally {
      setIsSyncing(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this connector?")) return;
    
    try {
      await ConnectorsService.deleteConnectorApiV1ConnectorsConnectorIdDelete(id);
      toast.success("Connector deleted");
      setConnectors(connectors.filter(c => c.id !== id));
    } catch (err: any) {
      toast.error(`Error deleting connector: ${err.message}`);
    }
  };

  const handleAddConnector = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await ConnectorsService.createConnectorApiV1ConnectorsPost({
        name: newConnectorName,
        source_type: newConnectorType,
        config_data: {},
        is_active: true
      });
      
      setConnectors([...connectors, res.data]);
      toast.success("Connector created successfully");
      setIsModalOpen(false);
      setNewConnectorName("");
    } catch (err: any) {
      toast.error(`Error: ${err.message}`);
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
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF] overflow-y-auto">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <Plug size={16} className="text-[#4C9FE8]" />
          Data Connectors
        </h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] border border-[#4C9FE8]/20 hover:bg-[#4C9FE8]/20 transition-colors rounded-md text-xs font-medium"
        >
          <Plus size={14} />
          New Connector
        </button>
      </header>

      <main className="flex-1 p-8 max-w-6xl mx-auto w-full">
        <div className="mb-8">
          <h2 className="text-xl font-display font-bold text-white mb-2">Connected Sources</h2>
          <p className="text-sm text-white/40">Manage data integrations providing context to the Graph RAG engine.</p>
        </div>

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
                <div key={c.id} className="rounded-xl border border-white/5 bg-white/[0.02] p-5 hover:border-white/10 transition-colors group flex flex-col h-48 relative overflow-hidden shadow-xl shadow-black/20">
                  <div className="absolute top-0 left-0 w-full h-1 transition-colors" style={{ backgroundColor: isError ? "#E54D2E" : "#2FAE86" }} />
                  
                  <div className="flex items-start justify-between mb-auto">
                    <div className={`p-3 rounded-lg shadow-inner ${isError ? 'bg-[#E54D2E]/10 text-[#E54D2E]' : 'bg-white/5 text-white/80'}`}>
                      <Icon size={24} />
                    </div>
                    <div className="flex gap-2">
                      <div className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                        isError 
                          ? 'border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E]' 
                          : 'border-[#2FAE86]/20 bg-[#2FAE86]/10 text-[#2FAE86]'
                      }`}>
                        {c.is_active ? 'Active' : 'Inactive'}
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-display font-bold text-[#F6F4EF] truncate">{c.name}</h3>
                      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleSync(c.id, c.source_type, c.config_data)}
                          disabled={syncing}
                          className="p-1.5 rounded-md text-white/40 hover:text-[#4C9FE8] hover:bg-white/5 transition-colors"
                          title="Sync Now"
                        >
                          <RefreshCw size={14} className={syncing ? "animate-spin text-[#4C9FE8]" : ""} />
                        </button>
                        <button 
                          onClick={() => handleDelete(c.id)}
                          className="p-1.5 rounded-md text-white/40 hover:text-[#E54D2E] hover:bg-white/5 transition-colors"
                          title="Delete Connector"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-white/40">
                      Type: <span className="capitalize text-white/60">{c.source_type}</span>
                    </div>
                  </div>
                </div>
              );
            })}
            
            <div 
              onClick={() => setIsModalOpen(true)}
              className="rounded-xl border border-white/5 border-dashed bg-transparent p-5 hover:border-white/20 hover:bg-white/[0.01] transition-all flex flex-col items-center justify-center h-48 cursor-pointer text-white/40 hover:text-[#4C9FE8] group"
            >
              <div className="p-4 rounded-full bg-white/5 group-hover:bg-[#4C9FE8]/10 mb-4 transition-colors">
                <Plus size={24} />
              </div>
              <span className="text-sm font-medium">Add New Source</span>
            </div>
          </div>
        )}
      </main>

      {/* Add Connector Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#12161b] border border-white/10 rounded-xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
              <h3 className="font-display font-bold text-white flex items-center gap-2">
                <Plug size={18} className="text-[#4C9FE8]"/> 
                New Connector
              </h3>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-white/40 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>
            
            <form onSubmit={handleAddConnector} className="p-6 flex flex-col gap-4">
              <label className="flex flex-col gap-1.5">
                <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">Connector Name</span>
                <input
                  type="text"
                  required
                  value={newConnectorName}
                  onChange={(e) => setNewConnectorName(e.target.value)}
                  className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors"
                  placeholder="e.g. Engineering Slack"
                />
              </label>
              
              <label className="flex flex-col gap-1.5">
                <span className="text-xs text-white/60 uppercase tracking-wider font-semibold">Source Type</span>
                <select
                  value={newConnectorType}
                  onChange={(e) => setNewConnectorType(e.target.value)}
                  className="w-full bg-[#0B0E12] border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8] transition-colors appearance-none"
                >
                  <option value="github">GitHub</option>
                  <option value="slack">Slack</option>
                  <option value="notion">Notion</option>
                  <option value="jira">Jira</option>
                  <option value="filesystem">Local Filesystem</option>
                </select>
              </label>

              <div className="pt-4 flex gap-3 justify-end border-t border-white/5 mt-2">
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
                  className="px-4 py-2 rounded-lg text-sm font-bold bg-[#4C9FE8] text-white hover:bg-[#3b8fd9] transition-colors disabled:opacity-50"
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
