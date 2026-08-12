"use client";

import React, { useState } from "react";
import { BrainCircuit, Search, Database, HardDrive, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

const mockMemories = [
  { id: "mem-001", type: "Semantic", content: "User prefers dark mode and Glassmorphism.", similarity: 0.98, timestamp: "2026-07-31T10:00:00Z" },
  { id: "mem-002", type: "Episodic", content: "Agent completed the 'Singularity' deployment successfully.", similarity: 0.85, timestamp: "2026-07-31T17:23:00Z" },
  { id: "mem-003", type: "Episodic", content: "Failed to connect to Datadog API.", similarity: 0.42, timestamp: "2026-07-31T14:12:00Z" },
  { id: "mem-004", type: "Semantic", content: "The platform uses Next.js and FastAPI.", similarity: 0.95, timestamp: "2026-07-30T09:00:00Z" },
];

export default function MemoryPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredMemories = mockMemories.filter(m => m.content.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="w-full h-full bg-[#050608] flex flex-col p-8 overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-[#F6F4EF] flex items-center gap-3">
          <BrainCircuit className="text-[#4C9FE8]" />
          Agent Memory (Vector Store)
        </h1>
        <p className="text-white/50 font-mono mt-2 text-sm">
          Manage and inspect the Episodic and Semantic memory embeddings of the agent swarm.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-[#141820] border border-[#2FAE86]/30 p-6 rounded-xl shadow-lg shadow-[#2FAE86]/5">
          <div className="flex items-center gap-3 mb-2">
            <Database className="text-[#2FAE86]" size={20} />
            <h2 className="text-lg font-bold text-white">Semantic Memory</h2>
          </div>
          <p className="text-sm text-white/50 mb-4">Long-term facts, preferences, and knowledge.</p>
          <div className="text-3xl font-mono text-white">1,204 <span className="text-sm text-white/30">vectors</span></div>
        </div>

        <div className="bg-[#141820] border border-[#4C9FE8]/30 p-6 rounded-xl shadow-lg shadow-[#4C9FE8]/5">
          <div className="flex items-center gap-3 mb-2">
            <HardDrive className="text-[#4C9FE8]" size={20} />
            <h2 className="text-lg font-bold text-white">Episodic Memory</h2>
          </div>
          <p className="text-sm text-white/50 mb-4">Short-term event logs and past actions.</p>
          <div className="text-3xl font-mono text-white">8,432 <span className="text-sm text-white/30">vectors</span></div>
        </div>
      </div>

      <div className="bg-[#141820] border border-white/10 rounded-xl overflow-hidden flex-1 flex flex-col">
        <div className="p-4 border-b border-white/5 flex gap-4 bg-black/20 items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" size={16} />
            <input 
              className="pl-9 bg-white/5 border border-white/10 rounded-md w-full py-2 px-3 text-sm text-white focus:outline-none focus:border-[#4C9FE8]/50" 
              placeholder="Search vector database..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" className="ml-auto border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300">
            <Trash2 size={16} className="mr-2" />
            Prune Old Memories
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10">
                <th className="py-3 px-4 text-xs font-mono text-white/40 uppercase">ID</th>
                <th className="py-3 px-4 text-xs font-mono text-white/40 uppercase">Type</th>
                <th className="py-3 px-4 text-xs font-mono text-white/40 uppercase">Memory Content</th>
                <th className="py-3 px-4 text-xs font-mono text-white/40 uppercase">Relevance</th>
                <th className="py-3 px-4 text-xs font-mono text-white/40 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filteredMemories.map(m => (
                <tr key={m.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-4 text-xs font-mono text-white/50">{m.id}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-mono uppercase ${m.type === 'Semantic' ? 'bg-[#2FAE86]/20 text-[#2FAE86]' : 'bg-[#4C9FE8]/20 text-[#4C9FE8]'}`}>
                      {m.type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-white/80">{m.content}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${m.similarity > 0.8 ? 'bg-[#2FAE86]' : m.similarity > 0.6 ? 'bg-yellow-400' : 'bg-red-400'}`} 
                          style={{ width: `${m.similarity * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-white/50">{m.similarity.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-xs font-mono text-white/40">{new Date(m.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredMemories.length === 0 && (
            <div className="text-center py-12 text-white/30 text-sm">
              No memories found in vector space.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
