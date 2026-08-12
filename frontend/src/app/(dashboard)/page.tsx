"use client";

import React, { useState, useEffect } from "react";
import { motion, Variants, AnimatePresence } from "framer-motion";
import dagre from "dagre";
import { 
  PlayCircle, 
  TerminalSquare, 
  CheckCircle2, 
  Info, 
  Sparkles,
  BrainCircuit,
  ArrowRight
} from "lucide-react";
import { submitGoal, getTimelineUrl, submitApproval } from "@/lib/api";
import { StatusPill } from "@/components/ui/StatusPill";

const SUGGESTIONS = [
  "Analyze Q3 retention metrics",
  "Evaluate connector latency",
  "Deploy updated policies"
];

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.1 }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  show: { opacity: 1, scale: 1, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

type NodeStatus = "queued" | "running" | "completed" | "blocked" | "kg_node";

interface DagNode {
  id: string;
  label?: string;
  status: NodeStatus;
  x: number;
  y: number;
}

interface DagEdge {
  source: string;
  target: string;
  label?: string;
  path: string;
}

interface TraceEvent {
  time: Date;
  message: string;
  type: "info" | "tool" | "system" | "success";
}

export default function Home() {
  const [goalInput, setGoalInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [nodes, setNodes] = useState<DagNode[]>([]);
  const [edges, setEdges] = useState<DagEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [traces, setTraces] = useState<TraceEvent[]>([]);
  const [pendingApproval, setPendingApproval] = useState<{task_id: string, context: string} | null>(null);
  


  // DAG SSE Listener
  useEffect(() => {
    // Reset view
    setNodes([]);
    setEdges([]);
    setTraces([{ time: new Date(), message: "Switched to Execution DAG view. Awaiting goals...", type: "system" }]);

    const es = new EventSource(getTimelineUrl());
    
    es.addEventListener("timeline_update", (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (payload.event === "dag_created" && payload.dag) {
          const g = new dagre.graphlib.Graph();
          g.setGraph({ rankdir: "LR", align: "UL", marginx: 40, marginy: 40, ranksep: 80, nodesep: 40 });
          g.setDefaultEdgeLabel(() => ({}));
          
          payload.dag.forEach((n: any) => g.setNode(n.id, { width: 100, height: 40 }));
          payload.dag.forEach((n: any) => {
            if (n.dependencies) {
              n.dependencies.forEach((dep: string) => g.setEdge(dep, n.id));
            }
          });
          
          dagre.layout(g);
          
          const computedNodes: DagNode[] = g.nodes().map(v => {
            const node = g.node(v);
            return { id: v, status: "queued", x: node.x, y: node.y };
          });
          
          const computedEdges: DagEdge[] = g.edges().map(e => {
            const edge = g.edge(e);
            const start = edge.points[0];
            const end = edge.points[edge.points.length - 1];
            return {
              source: e.v, target: e.w,
              path: `M ${start.x} ${start.y} C ${(start.x + end.x)/2} ${start.y}, ${(start.x + end.x)/2} ${end.y}, ${end.x} ${end.y}`
            };
          });
          
          setNodes(computedNodes);
          setEdges(computedEdges);
          setTraces(prev => [...prev, { time: new Date(), message: `DAG Generated: ${payload.dag.length} tasks`, type: "system" }]);
        }
        else if (payload.event === "task_started") {
          setNodes(prev => prev.map(n => n.id === payload.task_id ? { ...n, status: "running" } : n));
          setTraces(prev => [...prev, { time: new Date(), message: `Task started: ${payload.task_id}`, type: "info" }]);
        }
        else if (payload.event === "task_completed") {
          setNodes(prev => prev.map(n => n.id === payload.task_id ? { ...n, status: "completed" } : n));
          setTraces(prev => [
            ...prev, 
            { time: new Date(), message: `Task completed: ${payload.task_id}`, type: "info" }
          ]);
          if (payload.result) {
            setTraces(prev => [
              ...prev,
              { time: new Date(), message: `Result:\n${payload.result}`, type: "success" }
            ]);
          }
        }
        else if (payload.event === "approval_requested") {
          setPendingApproval({ task_id: payload.task_id, context: payload.context });
          setTraces(prev => [...prev, { time: new Date(), message: `Human approval required for task: ${payload.task_id}`, type: "system" }]);
        }
      } catch (err) {
        console.error("Error parsing SSE:", err);
      }
    });

    return () => es.close();
  }, []);

  const handleGoalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalInput.trim()) return;
    
    setIsSubmitting(true);
    
    setNodes([]);
    setEdges([]);
    setTraces([]);
    
    try {
      await submitGoal(goalInput);
      setGoalInput("");
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeCount = nodes.filter(n => n.status === "running").length;
  const completedCount = nodes.filter(n => n.status === "completed").length;
  const queuedCount = nodes.filter(n => n.status === "queued").length;

  return (
    <div className="min-h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30 flex flex-col">
      
      <motion.header 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10"
      >
        <div className="flex items-center gap-4 text-sm">
          <span className="font-display font-bold tracking-widest text-[#F6F4EF]">VERIDEX ORCHESTRATOR</span>
        </div>
        
        <div className="flex-1 max-w-xl mx-8 relative flex flex-col gap-2">
          <form onSubmit={handleGoalSubmit} className="relative w-full">
            <input
              type="text"
              value={goalInput}
              onChange={(e) => setGoalInput(e.target.value)}
              placeholder="Enter a new goal for the Orchestrator..."
              className="w-full bg-[#141820]/80 backdrop-blur-sm border border-white/10 hover:border-white/20 rounded-full px-5 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 focus:ring-1 focus:ring-[#4C9FE8]/50 transition-all font-mono placeholder:text-white/20 shadow-inner"
              disabled={isSubmitting}
            />
            <button 
              type="submit" 
              disabled={isSubmitting || !goalInput.trim()}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-[#4C9FE8]/10 text-[#4C9FE8] rounded-full text-xs font-mono hover:bg-[#4C9FE8]/20 transition-colors disabled:opacity-50 flex items-center gap-1 group"
            >
              EXECUTE 
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </form>
          
          {nodes.length === 0 && !isSubmitting && (
            <motion.div 
              initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}
              className="absolute top-full left-0 mt-3 w-full flex flex-wrap gap-2 px-2"
            >
              {SUGGESTIONS.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => setGoalInput(suggestion)}
                  className="px-3 py-1.5 rounded-full border border-white/5 bg-white/[0.03] hover:bg-white/[0.08] hover:border-white/10 text-[10px] font-mono text-white/50 hover:text-white/80 transition-all flex items-center gap-1.5 whitespace-nowrap"
                >
                  <Sparkles className="w-3 h-3 text-[#4C9FE8]/60" />
                  {suggestion}
                </button>
              ))}
            </motion.div>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <StatusPill status={activeCount > 0 ? "running" : "queued"} />
          <div className="flex gap-2 font-mono text-[11px]">
              <>
                <motion.div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#2FAE86]/20 bg-[#2FAE86]/10 text-[#2FAE86]">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#2FAE86]" />
                  <span>{completedCount} done</span>
                </motion.div>
                <motion.div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#F5A623]/20 bg-[#F5A623]/10 text-[#F5A623]">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#F5A623]" />
                  <span>{activeCount} active</span>
                </motion.div>
                <motion.div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-zinc-500/20 bg-zinc-500/10 text-zinc-500">
                  <div className="w-1.5 h-1.5 rounded-full bg-zinc-500" />
                  <span>{queuedCount} queued</span>
                </motion.div>
              </>
          </div>
        </div>
      </motion.header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-3 gap-6">
        <div className="col-span-2 flex flex-col gap-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden hover:border-white/10 transition-colors shadow-2xl shadow-black/50 flex-1 min-h-[500px] flex flex-col"
          >
            <div className="px-6 py-4 flex items-center justify-between border-b border-white/5 bg-white/[0.01]">
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs text-[#F6F4EF]/70">
                  live orchestrator graph
                </span>
              </div>
            </div>

            <div className="relative flex-1 overflow-auto p-8">
              {nodes.length === 0 ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-white/20 font-mono text-sm">
                  <motion.div 
                    animate={{ scale: [1, 1.05, 1], opacity: [0.3, 0.6, 0.3] }} 
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    className="mb-6 relative"
                  >
                    <div className="absolute inset-0 bg-[#4C9FE8]/20 blur-xl rounded-full" />
                    <BrainCircuit className="w-16 h-16 text-[#4C9FE8]/50 relative z-10" strokeWidth={1} />
                  </motion.div>
                  <span className="text-white/40 tracking-wider">Awaiting Goal Decomposition</span>
                  <span className="text-white/20 text-[10px] mt-2 max-w-xs text-center">
                    Enter a command above to watch the AI orchestrator break it down into execution graphs.
                  </span>
                </div>
              ) : (
                <motion.div 
                  variants={containerVariants}
                  initial="hidden"
                  animate="show"
                  className="relative"
                  style={{ width: '100%', height: '100%' }}
                >
                  <svg className="absolute inset-0 pointer-events-none w-full h-full" style={{ zIndex: 0, overflow: 'visible' }}>
                    {edges.map((edge, i) => (
                      <React.Fragment key={edge.source + "-" + edge.target + i}>
                        <motion.path 
                          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: i * 0.1 }}
                          d={edge.path} fill="transparent" stroke="rgba(246, 244, 239, 0.1)" strokeWidth="1.5" 
                        />
                        <motion.path 
                          initial={{ pathLength: 0, strokeDashoffset: 0, opacity: 0 }} 
                          animate={{ pathLength: 1, strokeDashoffset: -20, opacity: 1 }} 
                          transition={{ pathLength: { duration: 0.8, delay: i * 0.1 + 0.2 }, strokeDashoffset: { duration: 1, repeat: Infinity, ease: "linear" } }}
                          d={edge.path} fill="transparent" stroke="#4C9FE8" strokeWidth="1" strokeDasharray="4 4" 
                        />
                        <path id={`edge-${i}`} d={edge.path} fill="none" />
                      </React.Fragment>
                    ))}
                  </svg>

                  {nodes.map((node) => {
                    const isRunning = node.status === "running";
                    const isCompleted = node.status === "completed";
                    const isSelected = selectedNode === node.id;
                    const isKG = node.status === "kg_node";
                    
                    let color = "#71717A"; 
                    if (isRunning) color = "#F5A623";
                    if (isCompleted) color = "#2FAE86";
                    if (isKG) color = "#9D4EDD";

                    return (
                      <motion.div 
                        key={node.id}
                        variants={itemVariants} 
                        className="absolute flex flex-col items-center justify-center gap-2 group cursor-pointer"
                        style={{ 
                          left: node.x - (isKG ? 60 : 50), 
                          top: node.y - 20,
                          width: isKG ? 120 : 100,
                          height: 40,
                          zIndex: isSelected ? 10 : 1
                        }}
                        onClick={() => setSelectedNode(node.id)}
                      >
                        <div 
                          className="w-5 h-5 rounded-full border-2 transition-all flex items-center justify-center backdrop-blur-md bg-[#0B0E12]/80"
                          style={{ 
                            borderColor: color, 
                            boxShadow: (isRunning || isSelected || isKG) ? `0 0 16px ${color}66` : "none",
                            transform: isSelected ? 'scale(1.25)' : 'scale(1)'
                          }}
                        >
                          {isRunning && (
                            <motion.div 
                              animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }} 
                              transition={{ duration: 1.5, repeat: Infinity }}
                              className="w-2 h-2 rounded-full" 
                              style={{ backgroundColor: color }}
                            />
                          )}
                          {(isCompleted || isKG) && (
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                          )}
                        </div>
                        <span 
                          className="font-mono text-[10px] transition-colors whitespace-nowrap backdrop-blur-md bg-[#0B0E12]/80 px-2 py-1 rounded shadow-lg border border-white/10 group-hover:border-white/30 group-hover:text-white"
                          style={{ color: (isRunning || isKG) ? "#F6F4EF" : "#F6F4EF80" }}
                        >
                          {node.label || node.id}
                        </span>
                      </motion.div>
                    );
                  })}
                </motion.div>
              )}
            </div>
          </motion.div>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="rounded-xl border border-white/5 bg-white/[0.02] p-6 flex flex-col hover:border-white/10 transition-colors backdrop-blur-sm shadow-xl shadow-black/30"
        >
          <header className="mb-4">
            <h3 className="font-mono text-[10px] tracking-widest text-[#F6F4EF]/50 uppercase">Execution Trace</h3>
          </header>
          <div className="h-px bg-white/5 w-full mb-4" />
          <div className="flex-1 overflow-y-auto font-mono text-[11px] pr-2 custom-scrollbar">
            {traces.length === 0 ? (
              <div className="text-white/20">Awaiting events...</div>
            ) : (
              <AnimatePresence initial={false}>
                <div className="space-y-3">
                  {traces.map((trace, idx) => {
                    const isSystem = trace.type === "system";
                    const isSuccess = trace.type === "success";
                    const isInfo = trace.type === "info";
                    
                    const Icon = isSuccess ? CheckCircle2 : isSystem ? TerminalSquare : isInfo ? Info : PlayCircle;
                    const colorClass = isSuccess ? "text-[#2FAE86]" : isSystem ? "text-[#F5A623]" : isInfo ? "text-[#4C9FE8]" : "text-white/80";
                    const bgClass = isSuccess ? "bg-[#2FAE86]/10" : isSystem ? "bg-[#F5A623]/10" : isInfo ? "bg-[#4C9FE8]/10" : "bg-white/5";

                    return (
                      <motion.div 
                        key={idx}
                        initial={{ opacity: 0, y: 10, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        className="flex items-start gap-3 group"
                      >
                        <span className="text-white/30 shrink-0 mt-0.5">
                          {trace.time.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
                        </span>
                        
                        <div className={`p-1 rounded shrink-0 ${bgClass}`}>
                          <Icon className={`w-3 h-3 ${colorClass}`} />
                        </div>

                        <span className={`mt-0.5 ${
                          isSuccess ? "text-[#2FAE86] font-bold whitespace-pre-wrap" :
                          isSystem ? "text-white/90" :
                          isInfo ? "text-white/70" : "text-white/50"
                        }`}>
                          {trace.message}
                        </span>
                      </motion.div>
                    );
                  })}
                </div>
              </AnimatePresence>
            )}
            <div className="h-4" />
          </div>
        </motion.div>
      </main>

      {pendingApproval && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-[#141820] border border-white/10 rounded-xl p-6 max-w-lg w-full shadow-2xl"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-[#E54D2E]/20 flex items-center justify-center text-[#E54D2E]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
              </div>
              <div>
                <h3 className="text-[#F6F4EF] font-display font-bold">Action Requires Approval</h3>
                <p className="text-white/40 text-xs font-mono mt-0.5">Task ID: {pendingApproval.task_id}</p>
              </div>
            </div>
            
            <div className="bg-black/40 rounded p-4 mb-6 border border-white/5 font-mono text-sm text-white/80">
              {pendingApproval.context}
            </div>

            <div className="flex items-center justify-end gap-3">
              <button 
                onClick={() => submitApproval(pendingApproval.task_id, 'reject').then(() => setPendingApproval(null))}
                className="px-4 py-2 rounded font-mono text-xs text-white/60 hover:text-white/90 transition-colors"
              >
                Reject Action
              </button>
              <button 
                onClick={() => submitApproval(pendingApproval.task_id, 'reject').then(() => setPendingApproval(null))}
                className="px-4 py-2 rounded font-mono text-xs border border-white/10 text-white/80 hover:bg-white/5 transition-colors"
              >
                Revise
              </button>
              <button 
                onClick={() => submitApproval(pendingApproval.task_id, 'approve').then(() => setPendingApproval(null))}
                className="px-4 py-2 rounded font-mono text-xs bg-[#E54D2E] text-white hover:bg-[#E54D2E]/80 transition-colors shadow-lg shadow-[#E54D2E]/20"
              >
                Approve & Execute
              </button>
            </div>
          </motion.div>
        </div>
      )}
      
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
      `}} />
    </div>
  );
}
