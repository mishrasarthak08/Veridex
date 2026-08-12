"use client";

import React, { useState } from "react";
import { ShieldAlert, ServerCrash, Network, Loader2 } from "lucide-react";
import { API_URL, getToken } from "@/lib/api";
import { toast } from "sonner";
import axios from "axios";

export default function ResiliencePage() {
  const [injecting, setInjecting] = useState<string | null>(null);

  const handleInject = async (mode: string) => {
    setInjecting(mode);
    try {
      const res = await fetch(`${API_URL}/api/v1/resilience/chaos`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(getToken() ? { "Authorization": `Bearer ${getToken()}` } : {})
        },
        body: JSON.stringify({
          mode: mode,
          probability: 0.5,
          duration_ms: 5000
        })
      });
      
      if (!res.ok) throw new Error("Chaos injection failed");
      
      toast.warning(`Chaos injected: ${mode}`);
    } catch (err) {
      console.error(err);
      toast.error("Failed to connect to chaos engineering API");
    } finally {
      setInjecting(null);
    }
  };

  const [isCrashing, setIsCrashing] = useState(false);
  const handleSwarmCrash = async () => {
    setIsCrashing(true);
    try {
      const projectId = "proj_123";
      await axios.post(`http://localhost:8000/api/v1/projects/${projectId}/chaos`);
      toast.success("Chaos Swarm Deployed!", {
        description: "Agent crash simulated. Open Terminal to view recovery logs."
      });
    } catch (error) {
      console.error(error);
      toast.error("Failed to trigger chaos swarm");
    } finally {
      setIsCrashing(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30 overflow-hidden">
      <div className="flex-1 flex flex-col min-w-0">
        <header className="px-6 py-4 flex items-center gap-4 border-b border-red-500/10 backdrop-blur-sm bg-red-950/10 sticky top-0 z-10 shrink-0">
          <ShieldAlert size={20} className="text-red-500" />
          <h1 className="font-display font-bold tracking-widest text-red-500 text-sm uppercase">
            Chaos Engineering Control Panel
          </h1>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            
            <div className="bg-red-950/20 border border-red-500/20 rounded-lg p-6 space-y-4">
              <h2 className="text-xl font-display text-red-400">Fault Injection</h2>
              <p className="text-red-400/60 text-sm font-mono">
                Use these controls to inject synthetic failures into the backend microservices.
                Verify that the UI degrades gracefully.
              </p>

              <div className="grid grid-cols-2 gap-4 mt-8">
                <button 
                  onClick={() => handleInject("latency")}
                  disabled={injecting !== null}
                  className="bg-[#0B0E12] border border-red-500/30 hover:border-red-500 rounded-lg p-4 flex flex-col items-start gap-2 transition-colors disabled:opacity-50"
                >
                  <div className="flex items-center gap-2 text-red-400">
                    <Network size={18} />
                    <span className="font-mono text-sm uppercase">Simulate Latency</span>
                  </div>
                  <span className="text-xs text-white/40">Injects 5000ms delay into Vector DB queries</span>
                  {injecting === "latency" && <Loader2 size={14} className="animate-spin text-red-500 mt-2" />}
                </button>

                <button 
                  onClick={() => handleInject("503_error")}
                  disabled={injecting !== null}
                  className="bg-[#0B0E12] border border-red-500/30 hover:border-red-500 rounded-lg p-4 flex flex-col items-start gap-2 transition-colors disabled:opacity-50"
                >
                  <div className="flex items-center gap-2 text-red-400">
                    <ServerCrash size={18} />
                    <span className="font-mono text-sm uppercase">Simulate 503 Outage</span>
                  </div>
                  <span className="text-xs text-white/40">Returns 50% 503 errors on LLM generation</span>
                  {injecting === "503_error" && <Loader2 size={14} className="animate-spin text-red-500 mt-2" />}
                </button>

                <button 
                  onClick={handleSwarmCrash}
                  disabled={isCrashing}
                  className="bg-[#0B0E12] border border-orange-500/30 hover:border-orange-500 rounded-lg p-4 flex flex-col items-start gap-2 transition-colors disabled:opacity-50 col-span-2"
                >
                  <div className="flex items-center gap-2 text-orange-400">
                    <ShieldAlert size={18} />
                    <span className="font-mono text-sm uppercase">Trigger Swarm Agent Crash (OOM)</span>
                  </div>
                  <span className="text-xs text-white/40">Deploys a swarm but intentionally crashes the Researcher Agent. Watch the terminal for the Recovery Agent taking over.</span>
                  {isCrashing && <Loader2 size={14} className="animate-spin text-orange-500 mt-2" />}
                </button>
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
