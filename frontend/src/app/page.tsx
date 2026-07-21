"use client";

import React from "react";
import { StatusPill } from "../components/ui/StatusPill";
import { NodeCard } from "../components/ui/NodeCard";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30">
      
      {/* Top Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-2 text-sm">
          <span className="font-display font-bold tracking-widest text-[#F6F4EF]">VERIDEX</span>
          <span className="font-mono text-xs text-[#F6F4EF]/50">acme-corp / support-ops</span>
        </div>
        <div className="flex items-center gap-2">
          <StatusPill status="running" /> {/* Showing raw text instead of counts to match pill standard, but pdf has 7 running */}
          <div className="flex gap-2 font-mono text-[11px]">
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#F5A623]/20 bg-[#F5A623]/10 text-[#F5A623]">
              <div className="w-1.5 h-1.5 rounded-full bg-[#F5A623]" />
              <span>7 running</span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#E0483D]/20 bg-[#E0483D]/10 text-[#E0483D]">
              <div className="w-1.5 h-1.5 rounded-full bg-[#E0483D]" />
              <span>1 blocked</span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-zinc-500/20 bg-zinc-500/10 text-zinc-500">
              <div className="w-1.5 h-1.5 rounded-full bg-zinc-500" />
              <span>12 queued</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Console Area */}
      <main className="p-6 max-w-6xl mx-auto space-y-6">
        
        {/* Run Container */}
        <div className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden">
          
          {/* Run Header */}
          <div className="px-6 py-4 flex items-center justify-between border-b border-white/5">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs text-[#F6F4EF]/70">run #a91f-plan</span>
              <span className="font-mono text-xs text-[#F6F4EF]">&middot;</span>
              <span className="font-mono text-xs text-[#F6F4EF]">"reconcile weekly billing exceptions"</span>
            </div>
            <span className="font-mono text-xs text-[#F6F4EF]/50">t+00:42</span>
          </div>

          {/* DAG Canvas (Static Mockup matching PDF) */}
          <div className="relative h-[320px] p-6 overflow-hidden">
            
            {/* Mocked nodes purely for visual structural reference matching PDF */}
            <div className="absolute top-1/2 left-12 -translate-y-1/2 flex flex-col items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-[#4C9FE8]" />
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">plan</span>
            </div>

            {/* Trace lines (simplified CSS approximations of SVG splines) */}
            <div className="absolute top-1/2 left-[64px] w-24 h-px bg-[#4C9FE8]/30" />
            
            <div className="absolute top-1/2 left-32 -translate-y-1/2 flex flex-col items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-[#2FAE86]" />
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">split</span>
            </div>

            {/* Branches from split */}
            <svg className="absolute top-0 left-[144px] w-48 h-full pointer-events-none" style={{ zIndex: 0 }}>
               <path d="M 0 160 C 40 160, 40 80, 80 80" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" />
               <path d="M 0 160 C 40 160, 40 240, 80 240" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" />
               <path d="M 0 160 L 80 160" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" />
            </svg>

            <div className="absolute top-[72px] left-56 -translate-y-1/2 flex flex-col items-center gap-2">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">fetch.invoices</span>
              <div className="w-4 h-4 rounded-full border-2 border-[#2FAE86]" />
            </div>

            <div className="absolute top-[160px] left-56 -translate-y-1/2 flex flex-col items-center gap-2">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">fetch.usage_logs</span>
              <div className="w-4 h-4 rounded-full border-2 border-[#F5A623]" />
            </div>

            <div className="absolute top-[248px] left-56 -translate-y-1/2 flex flex-col items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-[#E0483D]" />
              <span className="font-mono text-[11px] text-[#E0483D]">policy.export_scope</span>
            </div>

            <svg className="absolute top-0 left-[240px] w-32 h-full pointer-events-none" style={{ zIndex: 0 }}>
               <path d="M 0 80 C 40 80, 40 120, 80 120" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" />
               <path d="M 0 160 C 40 160, 40 120, 80 120" fill="transparent" stroke="#F5A623" strokeWidth="2" strokeDasharray="4 4" />
               <path d="M 0 248 C 40 248, 40 280, 80 280" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" />
               <path d="M 80 120 L 160 120" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" />
            </svg>

            <div className="absolute top-[120px] left-[330px] -translate-y-1/2 flex flex-col items-center gap-2">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">reconcile</span>
              <div className="w-5 h-5 rounded-full border-2 border-[#F5A623] flex items-center justify-center">
                 <div className="w-1.5 h-1.5 bg-[#F5A623] rounded-full" />
              </div>
            </div>

            <div className="absolute top-[120px] left-[450px] -translate-y-1/2 flex flex-col items-center gap-2">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">draft_summary</span>
              <div className="w-4 h-4 rounded-full border-2 border-zinc-600" />
            </div>

            <div className="absolute top-[280px] left-[330px] -translate-y-1/2 flex flex-col items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-zinc-600" />
              <span className="font-mono text-[11px] text-[#F6F4EF]/50">await policy</span>
            </div>

            {/* Blocked Alert Banner at bottom of DAG */}
            <div className="absolute bottom-6 left-6 right-6 px-4 py-3 bg-[#1A1210] border border-[#E0483D]/20 rounded-lg flex items-center justify-between">
               <span className="font-mono text-[11px] text-[#E0483D]">policy.export_scope blocked run at step 3 — awaiting workspace admin approval</span>
               <button className="font-mono text-[11px] text-[#F5A623] hover:text-[#F5A623]/80 transition-colors">Review &rarr;</button>
            </div>
          </div>
        </div>

        {/* Selected Node Detail Panel */}
        <div className="rounded-xl border border-white/5 bg-white/[0.02] p-6 space-y-6">
          <header>
            <h3 className="font-mono text-[10px] tracking-widest text-[#F6F4EF]/50 uppercase mb-4">Selected Node &middot; Reconcile</h3>
            <div className="flex flex-col gap-1">
              <div className="font-mono text-sm text-[#F6F4EF]">worker.reconcile_exceptions</div>
              <div className="font-mono text-[11px] text-[#F6F4EF]/50">gemini-2.5-pro &middot; started t+00:31</div>
            </div>
          </header>

          <div className="h-px bg-white/5 w-full" />

          <section>
            <h4 className="font-mono text-[10px] tracking-widest text-[#F6F4EF]/50 uppercase mb-4">Inputs Resolved</h4>
            <div className="font-mono text-[11px] space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-[#F6F4EF]/70 w-32">invoices.q3</span>
                <span className="text-[#2FAE86]">&#10003; 214 rows</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[#F6F4EF]/70 w-32">usage_logs.q3</span>
                <span className="text-[#F5A623]">&#8987; streaming</span>
              </div>
            </div>
          </section>

          <div className="h-px bg-white/5 w-full" />

          <section>
            <h4 className="font-mono text-[10px] tracking-widest text-[#F6F4EF]/50 uppercase mb-4">Trace</h4>
            <div className="font-mono text-[11px] text-[#F6F4EF]/50 space-y-2">
              <div className="flex items-start gap-4">
                <span className="w-16 shrink-0">t+00:31</span>
                <span>step started</span>
              </div>
              <div className="flex items-start gap-4">
                <span className="w-16 shrink-0">t+00:33</span>
                <span className="text-[#4C9FE8]">+ tool_call: qdrant.search</span>
              </div>
              <div className="flex items-start gap-4">
                <span className="w-16 shrink-0">t+00:38</span>
                <span className="text-[#4C9FE8]">+ tool_call: neo4j.match</span>
              </div>
              <div className="flex items-start gap-4">
                <span className="w-16 shrink-0">t+00:41</span>
                <span>awaiting stream close</span>
              </div>
            </div>
          </section>
        </div>

        <p className="font-body text-[12px] text-[#F6F4EF]/40 mt-8 leading-relaxed max-w-3xl">
          Reading order, deliberately: status counts first (top right), then the shape of the run, then one node's detail on demand. Nothing here is invented — qdrant.search and neo4j.match are literal calls this stack already makes; the console just makes them visible as they happen.
        </p>

      </main>
    </div>
  );
}
