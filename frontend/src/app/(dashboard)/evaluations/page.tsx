"use client";

import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { Activity, ShieldCheck, Scale, History, Download } from "lucide-react";

const evalData = [
  { run: "Run 1", hallucination: 0.12, latency: 1.2, tokens: 1200 },
  { run: "Run 2", hallucination: 0.08, latency: 1.1, tokens: 1100 },
  { run: "Run 3", hallucination: 0.05, latency: 0.9, tokens: 900 },
  { run: "Run 4", hallucination: 0.02, latency: 0.8, tokens: 850 },
  { run: "Run 5", hallucination: 0.01, latency: 0.75, tokens: 800 },
  { run: "Run 6", hallucination: 0.00, latency: 0.7, tokens: 750 },
];

export default function EvaluationsPage() {
  return (
    <div className="w-full h-full bg-[#050608] flex flex-col p-8 overflow-y-auto">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-display font-bold text-[#F6F4EF] flex items-center gap-3">
            <Scale className="text-[#E54D2E]" />
            Agent Evaluations
          </h1>
          <p className="text-white/50 font-mono mt-2 text-sm">
            LLM-as-a-Judge correctness, hallucination rates, and performance tracking.
          </p>
        </div>
        <button 
          onClick={() => {
            const csvContent = "data:text/csv;charset=utf-8," 
              + "Run,Hallucination Rate,Latency (s),Token Usage\n"
              + evalData.map(e => `${e.run},${e.hallucination},${e.latency},${e.tokens}`).join("\n");
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "agent_evaluations.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-md hover:bg-white/10 text-white/80 transition-colors text-sm"
        >
          <Download size={16} />
          Export CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-[#141820] border border-[#E54D2E]/30 p-6 rounded-xl shadow-lg shadow-[#E54D2E]/5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Hallucination Rate</h2>
            <ShieldCheck className="text-[#E54D2E]" size={20} />
          </div>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="run" hide />
                <Tooltip contentStyle={{ backgroundColor: "#141820", borderColor: "#ffffff10" }} />
                <Line type="monotone" dataKey="hallucination" stroke="#E54D2E" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-sm font-mono text-green-400">↓ 92% improvement</div>
        </div>

        <div className="bg-[#141820] border border-[#4C9FE8]/30 p-6 rounded-xl shadow-lg shadow-[#4C9FE8]/5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Latency (s)</h2>
            <Activity className="text-[#4C9FE8]" size={20} />
          </div>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="run" hide />
                <Tooltip contentStyle={{ backgroundColor: "#141820", borderColor: "#ffffff10" }} />
                <Line type="monotone" dataKey="latency" stroke="#4C9FE8" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-sm font-mono text-green-400">↓ 41% improvement</div>
        </div>

        <div className="bg-[#141820] border border-[#2FAE86]/30 p-6 rounded-xl shadow-lg shadow-[#2FAE86]/5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Token Usage</h2>
            <History className="text-[#2FAE86]" size={20} />
          </div>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={evalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="run" hide />
                <Tooltip contentStyle={{ backgroundColor: "#141820", borderColor: "#ffffff10" }} cursor={{fill: '#ffffff05'}} />
                <Bar dataKey="tokens" fill="#2FAE86" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-sm font-mono text-green-400">↓ 37% improvement</div>
        </div>
      </div>

      <div className="bg-[#141820] border border-white/10 rounded-xl p-6 flex-1">
        <h3 className="text-lg font-bold text-white mb-4">Latest Evaluation Run: Eval-79</h3>
        <div className="space-y-4">
          <div className="bg-white/5 border border-white/10 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-sm text-[#4C9FE8]">Task: Data Extraction</span>
              <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs font-mono uppercase">Pass</span>
            </div>
            <p className="text-sm text-white/70">The agent successfully navigated the internal wiki and extracted the JSON schema without introducing fabricated fields.</p>
          </div>
          <div className="bg-white/5 border border-white/10 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-sm text-[#4C9FE8]">Task: Customer Routing</span>
              <span className="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs font-mono uppercase">Fail</span>
            </div>
            <p className="text-sm text-white/70">The agent hallucinated a billing department email address that does not exist in the vector database.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
