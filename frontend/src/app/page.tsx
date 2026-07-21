"use client";

import React from "react";
import { motion, Variants } from "framer-motion";
import { StatusPill } from "../components/ui/StatusPill";

// Stagger variants for the DAG nodes
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 10, scale: 0.95 },
  show: { opacity: 1, y: 0, scale: 1, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30">
      
      {/* Top Header */}
      <motion.header 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10"
      >
        <div className="flex items-center gap-2 text-sm">
          <span className="font-display font-bold tracking-widest text-[#F6F4EF]">VERIDEX</span>
          <span className="font-mono text-xs text-[#F6F4EF]/50">acme-corp / support-ops</span>
        </div>
        <div className="flex items-center gap-2">
          <StatusPill status="running" />
          <div className="flex gap-2 font-mono text-[11px]">
            <motion.div whileHover={{ scale: 1.05 }} className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#F5A623]/20 bg-[#F5A623]/10 text-[#F5A623] cursor-default transition-colors hover:bg-[#F5A623]/20">
              <div className="w-1.5 h-1.5 rounded-full bg-[#F5A623]" />
              <span>7 running</span>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#E0483D]/20 bg-[#E0483D]/10 text-[#E0483D] cursor-default transition-colors hover:bg-[#E0483D]/20">
              <div className="w-1.5 h-1.5 rounded-full bg-[#E0483D]" />
              <span>1 blocked</span>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-zinc-500/20 bg-zinc-500/10 text-zinc-500 cursor-default transition-colors hover:bg-zinc-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-zinc-500" />
              <span>12 queued</span>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Main Console Area */}
      <main className="p-6 max-w-6xl mx-auto space-y-6">
        
        {/* Run Container */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden hover:border-white/10 transition-colors shadow-2xl shadow-black/50"
        >
          {/* Run Header */}
          <div className="px-6 py-4 flex items-center justify-between border-b border-white/5 bg-white/[0.01]">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs text-[#F6F4EF]/70">run #a91f-plan</span>
              <span className="font-mono text-xs text-[#F6F4EF]">&middot;</span>
              <span className="font-mono text-xs text-[#F6F4EF]">"reconcile weekly billing exceptions"</span>
            </div>
            <span className="font-mono text-xs text-[#F6F4EF]/50">t+00:42</span>
          </div>

          {/* DAG Canvas (Static Mockup with Animations) */}
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="relative h-[320px] p-6 overflow-hidden"
          >
            
            {/* Trace lines */}
            <motion.div 
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.8, ease: "easeOut", delay: 0.3 }}
              style={{ originX: 0 }}
              className="absolute top-1/2 left-[64px] w-24 h-px bg-[#4C9FE8]/30" 
            />
            
            <svg className="absolute top-0 left-[144px] w-48 h-full pointer-events-none" style={{ zIndex: 0 }}>
               <motion.path 
                 initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: 0.4 }}
                 d="M 0 160 C 40 160, 40 80, 80 80" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" 
               />
               <motion.path 
                 initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: 0.5 }}
                 d="M 0 160 C 40 160, 40 240, 80 240" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" 
               />
               <motion.path 
                 initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: 0.6 }}
                 d="M 0 160 L 80 160" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" 
               />
            </svg>

            <svg className="absolute top-0 left-[240px] w-32 h-full pointer-events-none" style={{ zIndex: 0 }}>
               <motion.path 
                 initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: 0.7 }}
                 d="M 0 80 C 40 80, 40 120, 80 120" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" 
               />
               {/* Animated flowing trace line */}
               <motion.path 
                 initial={{ pathLength: 0, strokeDashoffset: 0 }} 
                 animate={{ pathLength: 1, strokeDashoffset: -20 }} 
                 transition={{ 
                   pathLength: { duration: 0.8, delay: 0.8 },
                   strokeDashoffset: { duration: 1, repeat: Infinity, ease: "linear" } 
                 }}
                 d="M 0 160 C 40 160, 40 120, 80 120" fill="transparent" stroke="#F5A623" strokeWidth="2" strokeDasharray="4 4" 
               />
               <motion.path 
                 initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: 0.9 }}
                 d="M 0 248 C 40 248, 40 280, 80 280" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" 
               />
               <motion.path 
                 initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: 1.0 }}
                 d="M 80 120 L 160 120" fill="transparent" stroke="rgba(246, 244, 239, 0.2)" strokeWidth="1" 
               />
            </svg>

            {/* Nodes */}
            <motion.div variants={itemVariants} className="absolute top-1/2 left-12 -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <div className="w-4 h-4 rounded-full border-2 border-[#4C9FE8] group-hover:scale-125 group-hover:shadow-[0_0_12px_rgba(76,159,232,0.4)] transition-all" />
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">plan</span>
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-1/2 left-32 -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <div className="w-4 h-4 rounded-full border-2 border-[#2FAE86] group-hover:scale-125 group-hover:shadow-[0_0_12px_rgba(47,174,134,0.4)] transition-all" />
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">split</span>
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-[72px] left-56 -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">fetch.invoices</span>
              <div className="w-4 h-4 rounded-full border-2 border-[#2FAE86] group-hover:scale-125 group-hover:shadow-[0_0_12px_rgba(47,174,134,0.4)] transition-all" />
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-[160px] left-56 -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">fetch.usage_logs</span>
              <div className="w-4 h-4 rounded-full border-2 border-[#F5A623] group-hover:scale-125 group-hover:shadow-[0_0_12px_rgba(245,166,35,0.4)] transition-all" />
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-[248px] left-56 -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <div className="w-4 h-4 rounded-full border-2 border-[#E0483D] group-hover:scale-125 group-hover:shadow-[0_0_12px_rgba(224,72,61,0.4)] transition-all" />
              <span className="font-mono text-[11px] text-[#E0483D] group-hover:text-[#E0483D]/80 transition-colors">policy.export_scope</span>
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-[120px] left-[330px] -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">reconcile</span>
              <div className="w-5 h-5 rounded-full border-2 border-[#F5A623] flex items-center justify-center group-hover:scale-110 group-hover:shadow-[0_0_16px_rgba(245,166,35,0.4)] transition-all">
                 <motion.div 
                   animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }} 
                   transition={{ duration: 2, repeat: Infinity }}
                   className="w-1.5 h-1.5 bg-[#F5A623] rounded-full" 
                 />
              </div>
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-[120px] left-[450px] -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">draft_summary</span>
              <div className="w-4 h-4 rounded-full border-2 border-zinc-600 group-hover:scale-125 transition-all" />
            </motion.div>

            <motion.div variants={itemVariants} className="absolute top-[280px] left-[330px] -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
              <div className="w-4 h-4 rounded-full border-2 border-zinc-600 group-hover:scale-125 transition-all" />
              <span className="font-mono text-[11px] text-[#F6F4EF]/50 group-hover:text-[#F6F4EF] transition-colors">await policy</span>
            </motion.div>

            {/* Blocked Alert Banner at bottom of DAG */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, type: "spring", stiffness: 400, damping: 30 }}
              className="absolute bottom-6 left-6 right-6 px-4 py-3 bg-[#1A1210] border border-[#E0483D]/20 rounded-lg flex items-center justify-between shadow-lg shadow-black/40 backdrop-blur-md"
            >
               <span className="font-mono text-[11px] text-[#E0483D]">policy.export_scope blocked run at step 3 — awaiting workspace admin approval</span>
               <button className="font-mono text-[11px] text-[#F5A623] hover:text-[#F5A623]/80 transition-colors">Review &rarr;</button>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Selected Node Detail Panel */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="rounded-xl border border-white/5 bg-white/[0.02] p-6 space-y-6 hover:border-white/10 transition-colors backdrop-blur-sm shadow-xl shadow-black/30"
        >
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
              <motion.div whileHover={{ x: 4 }} className="flex items-center gap-3 transition-transform cursor-default">
                <span className="text-[#F6F4EF]/70 w-32">invoices.q3</span>
                <span className="text-[#2FAE86]">&#10003; 214 rows</span>
              </motion.div>
              <motion.div whileHover={{ x: 4 }} className="flex items-center gap-3 transition-transform cursor-default">
                <span className="text-[#F6F4EF]/70 w-32">usage_logs.q3</span>
                <motion.span 
                  animate={{ opacity: [1, 0.5, 1] }} 
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="text-[#F5A623]"
                >&#8987; streaming</motion.span>
              </motion.div>
            </div>
          </section>

          <div className="h-px bg-white/5 w-full" />

          <section>
            <h4 className="font-mono text-[10px] tracking-widest text-[#F6F4EF]/50 uppercase mb-4">Trace</h4>
            <div className="font-mono text-[11px] text-[#F6F4EF]/50 space-y-2">
              <motion.div whileHover={{ x: 4 }} className="flex items-start gap-4 transition-transform cursor-default">
                <span className="w-16 shrink-0">t+00:31</span>
                <span className="hover:text-[#F6F4EF] transition-colors">step started</span>
              </motion.div>
              <motion.div whileHover={{ x: 4 }} className="flex items-start gap-4 transition-transform cursor-default">
                <span className="w-16 shrink-0">t+00:33</span>
                <span className="text-[#4C9FE8] hover:text-[#4C9FE8]/80 transition-colors">+ tool_call: qdrant.search</span>
              </motion.div>
              <motion.div whileHover={{ x: 4 }} className="flex items-start gap-4 transition-transform cursor-default">
                <span className="w-16 shrink-0">t+00:38</span>
                <span className="text-[#4C9FE8] hover:text-[#4C9FE8]/80 transition-colors">+ tool_call: neo4j.match</span>
              </motion.div>
              <motion.div whileHover={{ x: 4 }} className="flex items-start gap-4 transition-transform cursor-default">
                <span className="w-16 shrink-0">t+00:41</span>
                <span className="hover:text-[#F6F4EF] transition-colors">awaiting stream close</span>
              </motion.div>
            </div>
          </section>
        </motion.div>

        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          className="font-body text-[12px] text-[#F6F4EF]/40 mt-8 leading-relaxed max-w-3xl"
        >
          Reading order, deliberately: status counts first (top right), then the shape of the run, then one node's detail on demand. Nothing here is invented — qdrant.search and neo4j.match are literal calls this stack already makes; the console just makes them visible as they happen.
        </motion.p>

      </main>
    </div>
  );
}
