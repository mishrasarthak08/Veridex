"use client";

import React, { useState, useEffect } from "react";
import { motion, Variants } from "framer-motion";
import dagre from "dagre";
import { submitGoal, getTimelineUrl, fetchGraph } from "../lib/api";
import { StatusPill } from "../components/ui/StatusPill";

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
  type: "info" | "tool" | "system";
}

export default function Home() {
  const [goalInput, setGoalInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [viewMode, setViewMode] = useState<"dag" | "graph">("graph");
  
  const [nodes, setNodes] = useState<DagNode[]>([]);
  const [edges, setEdges] = useState<DagEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [traces, setTraces] = useState<TraceEvent[]>([]);
  
  // Fetch Knowledge Graph
  useEffect(() => {
    if (viewMode !== "graph") return;
    
    let isMounted = true;
    const loadGraph = async () => {
      try {
        const data = await fetchGraph();
        if (!isMounted) return;
        
        const g = new dagre.graphlib.Graph();
        g.setGraph({ rankdir: "LR", align: "UL", marginx: 40, marginy: 40, ranksep: 100, nodesep: 50 });
        g.setDefaultEdgeLabel(() => ({}));
        
        data.nodes.forEach((n: any) => {
          g.setNode(n.id, { width: 120, height: 40, label: n.properties?.name || n.properties?.title || n.label });
        });
        
        data.edges.forEach((e: any) => {
          g.setEdge(e.source, e.target, { label: e.type });
        });
        
        dagre.layout(g);
        
        const computedNodes: DagNode[] = g.nodes().map(v => {
          const node = g.node(v);
          return { id: v, label: node.label, status: "kg_node", x: node.x, y: node.y };
        });
        
        const computedEdges: DagEdge[] = g.edges().map(e => {
          const edge = g.edge(e);
          const start = edge.points[0];
          const end = edge.points[edge.points.length - 1];
          return {
            source: e.v, target: e.w, label: edge.label,
            path: `M ${start.x} ${start.y} C ${(start.x + end.x)/2} ${start.y}, ${(start.x + end.x)/2} ${end.y}, ${end.x} ${end.y}`
          };
        });
        
        setNodes(computedNodes);
        setEdges(computedEdges);
      } catch (err) {
        console.error("Failed to load Knowledge Graph", err);
      }
    };
    
    loadGraph();
    
    return () => { isMounted = false; };
  }, [viewMode]);

  // DAG SSE Listener
  useEffect(() => {
    if (viewMode !== "dag") return;

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
          setTraces(prev => [...prev, { time: new Date(), message: `Task completed: ${payload.task_id}`, type: "info" }]);
        }
      } catch (err) {
        console.error("Error parsing SSE:", err);
      }
    });

    return () => es.close();
  }, [viewMode]);

  const handleGoalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalInput.trim()) return;
    
    setIsSubmitting(true);
    if (viewMode !== "dag") setViewMode("dag");
    
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
  const kgCount = nodes.filter(n => n.status === "kg_node").length;

  return (
    <div className="min-h-screen bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30 flex flex-col">
      
      <motion.header 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10"
      >
        <div className="flex items-center gap-4 text-sm">
          <span className="font-display font-bold tracking-widest text-[#F6F4EF]">VERIDEX</span>
          <div className="flex bg-white/5 rounded-full p-1 font-mono text-[10px]">
            <button 
              onClick={() => setViewMode("graph")}
              className={`px-3 py-1 rounded-full transition-colors ${viewMode === "graph" ? "bg-[#4C9FE8]/20 text-[#4C9FE8]" : "text-white/40 hover:text-white/80"}`}
            >
              KNOWLEDGE GRAPH
            </button>
            <button 
              onClick={() => setViewMode("dag")}
              className={`px-3 py-1 rounded-full transition-colors ${viewMode === "dag" ? "bg-[#4C9FE8]/20 text-[#4C9FE8]" : "text-white/40 hover:text-white/80"}`}
            >
              EXECUTION DAG
            </button>
          </div>
        </div>
        
        <form onSubmit={handleGoalSubmit} className="flex-1 max-w-xl mx-8 relative">
          <input
            type="text"
            value={goalInput}
            onChange={(e) => setGoalInput(e.target.value)}
            placeholder="Enter a new goal for the Orchestrator..."
            className="w-full bg-[#141820] border border-white/10 rounded-full px-5 py-2 text-sm focus:outline-none focus:border-[#4C9FE8]/50 focus:ring-1 focus:ring-[#4C9FE8]/50 transition-all font-mono placeholder:text-white/20"
            disabled={isSubmitting}
          />
          <button 
            type="submit" 
            disabled={isSubmitting || !goalInput.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 bg-[#4C9FE8]/10 text-[#4C9FE8] rounded-full text-xs font-mono hover:bg-[#4C9FE8]/20 transition-colors disabled:opacity-50"
          >
            EXECUTE &rarr;
          </button>
        </form>

        <div className="flex items-center gap-2 shrink-0">
          <StatusPill status={viewMode === "graph" ? "completed" : (activeCount > 0 ? "running" : "queued")} />
          <div className="flex gap-2 font-mono text-[11px]">
            {viewMode === "graph" ? (
              <motion.div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#4C9FE8]/20 bg-[#4C9FE8]/10 text-[#4C9FE8]">
                <div className="w-1.5 h-1.5 rounded-full bg-[#4C9FE8]" />
                <span>{kgCount} entities</span>
              </motion.div>
            ) : (
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
            )}
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
                  {viewMode === "graph" ? "knowledge graph overview" : "live orchestrator graph"}
                </span>
              </div>
            </div>

            <div className="relative flex-1 overflow-auto p-8">
              {nodes.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-white/20 font-mono text-sm">
                  {viewMode === "graph" ? "Loading Knowledge Graph..." : "Waiting for goal decomposition..."}
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
                        {viewMode === "dag" ? (
                          <motion.path 
                            initial={{ pathLength: 0, strokeDashoffset: 0, opacity: 0 }} 
                            animate={{ pathLength: 1, strokeDashoffset: -20, opacity: 1 }} 
                            transition={{ pathLength: { duration: 0.8, delay: i * 0.1 + 0.2 }, strokeDashoffset: { duration: 1, repeat: Infinity, ease: "linear" } }}
                            d={edge.path} fill="transparent" stroke="#4C9FE8" strokeWidth="1" strokeDasharray="4 4" 
                          />
                        ) : (
                          <text x="50%" y="50%" fill="#F6F4EF80" fontSize="8" fontFamily="monospace">
                             <textPath href={`#edge-${i}`} startOffset="50%" textAnchor="middle">{edge.label}</textPath>
                          </text>
                        )}
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
                          className="w-4 h-4 rounded-full border-2 transition-all flex items-center justify-center bg-[#0B0E12]"
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
                              className="w-1.5 h-1.5 rounded-full" 
                              style={{ backgroundColor: color }}
                            />
                          )}
                          {(isCompleted || isKG) && (
                            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
                          )}
                        </div>
                        <span 
                          className="font-mono text-[10px] transition-colors whitespace-nowrap bg-[#0B0E12]/90 px-1.5 py-0.5 rounded border border-white/10"
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
          <div className="flex-1 overflow-y-auto space-y-3 font-mono text-[11px] pr-2 custom-scrollbar">
            {traces.length === 0 ? (
              <div className="text-white/20">Awaiting events...</div>
            ) : (
              traces.map((trace, idx) => (
                <motion.div 
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-start gap-3"
                >
                  <span className="text-white/30 shrink-0">
                    {trace.time.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
                  </span>
                  <span className={
                    trace.type === "system" ? "text-[#F5A623]" :
                    trace.type === "info" ? "text-white/80" : "text-[#4C9FE8]"
                  }>
                    {trace.message}
                  </span>
                </motion.div>
              ))
            )}
            <div className="h-4" />
          </div>
        </motion.div>
      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
      `}} />
    </div>
  );
}
