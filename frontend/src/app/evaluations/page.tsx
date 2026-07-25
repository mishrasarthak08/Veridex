"use client";

import React, { useState, useEffect } from "react";
import { Activity, Play, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { runEvaluations, fetchEvaluations } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";

interface EvalResult {
  id: string;
  query: string;
  response: string;
  dataset_name?: string;
  scores?: {
    relevance: number;
    toxicity: number;
    hallucination: number;
  };
  metrics?: {
    accuracy: number;
    hallucination_rate: number;
  };
  average_score?: number;
  overall_passed?: boolean;
  created_at?: string;
  timestamp?: string;
}

export default function EvaluationsPage() {
  const { user } = useAuth();
  const [evals, setEvals] = useState<EvalResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    async function load() {
      if (user) {
        try {
          const result = await fetchEvaluations();
          if (result && result.data) {
            setEvals(result.data);
          }
        } catch (e) {
          console.error("Failed to load evals", e);
        }
      }
    }
    load();
  }, [user]);

  const handleRunEvals = async () => {
    setIsRunning(true);
    try {
      const result = await runEvaluations();
      if (result && result.data) {
        setEvals(prev => [result.data, ...prev]);
      }
    } catch (err) {
      console.error("Eval failed", err);
      // Instead of mocking, we want real errors to surface now that the backend is live.
      setIsRunning(false);
      return;
    }
    setIsRunning(false);
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF]">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF] flex items-center gap-2">
          <Activity size={16} className="text-[#4C9FE8]" />
          LLM-as-a-Judge Evaluations
        </h1>
        <button 
          onClick={handleRunEvals}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] border border-[#4C9FE8]/20 hover:bg-[#4C9FE8]/20 transition-colors rounded-full text-xs font-mono disabled:opacity-50"
        >
          {isRunning ? (
            <div className="animate-spin w-3 h-3 border-2 border-[#4C9FE8] border-t-transparent rounded-full" />
          ) : (
            <Play size={14} />
          )}
          Run Pipeline
        </button>
      </header>

      <main className="flex-1 p-8 max-w-5xl mx-auto w-full flex flex-col gap-8">
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
            <div className="text-white/40 font-mono text-xs mb-1">Average Relevance</div>
            <div className="text-2xl font-display font-bold text-[#2FAE86]">94%</div>
          </div>
          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
            <div className="text-white/40 font-mono text-xs mb-1">Toxicity Incidents</div>
            <div className="text-2xl font-display font-bold text-[#2FAE86]">0</div>
          </div>
          <div className="rounded-xl border border-white/5 bg-white/[0.02] p-5">
            <div className="text-white/40 font-mono text-xs mb-1">Hallucination Rate</div>
            <div className="text-2xl font-display font-bold text-[#E54D2E]">12%</div>
          </div>
        </div>

        <div className="flex-1 rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden flex flex-col shadow-2xl shadow-black/50">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.01]">
            <h3 className="font-mono text-xs text-white/60">Evaluation Runs</h3>
          </div>
          
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 text-[10px] uppercase font-mono text-white/40 bg-white/[0.02]">
                  <th className="px-6 py-3 font-normal">Status</th>
                  <th className="px-6 py-3 font-normal">Query</th>
                  <th className="px-6 py-3 font-normal">Relevance</th>
                  <th className="px-6 py-3 font-normal">Hallucination</th>
                  <th className="px-6 py-3 font-normal">Timestamp</th>
                </tr>
              </thead>
              <tbody className="text-xs font-mono text-white/80 divide-y divide-white/5">
                {evals.map((ev) => (
                  <tr key={ev.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4">
                      {ev.overall_passed ? (
                        <div className="flex items-center gap-1.5 text-[#2FAE86] bg-[#2FAE86]/10 px-2 py-1 rounded w-max">
                          <CheckCircle2 size={14} /> Passed
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-[#E54D2E] bg-[#E54D2E]/10 px-2 py-1 rounded w-max">
                          <XCircle size={14} /> Failed
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 font-body truncate max-w-xs" title={ev.query}>
                      {ev.query}
                    </td>
                    <td className="px-6 py-4 font-mono">
                      {ev.scores?.relevance !== undefined ? (ev.scores.relevance * 100).toFixed(0) + '%' : '-'}
                    </td>
                    <td className="px-6 py-4 font-mono">
                      {ev.scores?.hallucination !== undefined ? (
                        ev.scores.hallucination > 0.5 ? (
                          <span className="text-[#E54D2E] flex items-center gap-1">
                            <AlertTriangle size={12} /> {(ev.scores.hallucination * 100).toFixed(0)}%
                          </span>
                        ) : (
                          <span className="text-[#2FAE86]">{(ev.scores.hallucination * 100).toFixed(0)}%</span>
                        )
                      ) : '-'}
                    </td>
                    <td className="px-6 py-4 text-white/40 font-mono">
                      {ev.timestamp || ev.created_at ? new Date((ev.timestamp || ev.created_at) as string).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
