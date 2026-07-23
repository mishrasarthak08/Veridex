"use client";

import React, { useState, useEffect } from "react";
import { motion, Variants } from "framer-motion";
import dagre from "dagre";
import { fetchGraph } from "../../lib/api";
import { StatusPill } from "../../components/ui/StatusPill";

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

interface DagNode {
  id: string;
  label?: string;
  status: "kg_node";
  x: number;
  y: number;
}

interface DagEdge {
  source: string;
  target: string;
  label?: string;
  path: string;
}

export default function KnowledgeGraphPage() {
  const [nodes, setNodes] = useState<DagNode[]>([]);
  const [edges, setEdges] = useState<DagEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
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
  }, []);

  return (
    <div className="flex flex-col h-full bg-[#0B0E12] font-body text-[#F6F4EF] selection:bg-[#4C9FE8]/30">
      <header className="px-6 py-4 flex items-center justify-between border-b border-white/5 backdrop-blur-sm bg-[#0B0E12]/80 sticky top-0 z-10 shrink-0">
        <h1 className="text-sm font-display font-bold text-[#F6F4EF]">Knowledge Graph Explorer</h1>
        <div className="flex items-center gap-2">
          <StatusPill status="done" />
          <motion.div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[#4C9FE8]/20 bg-[#4C9FE8]/10 text-[#4C9FE8] font-mono text-[11px]">
            <div className="w-1.5 h-1.5 rounded-full bg-[#4C9FE8]" />
            <span>{nodes.length} entities</span>
          </motion.div>
        </div>
      </header>

      <main className="flex-1 p-6 relative overflow-hidden flex flex-col">
        <div className="absolute inset-0 p-6 pointer-events-none">
          <div className="w-full h-full rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden shadow-2xl shadow-black/50 relative pointer-events-auto">
            
            <div className="px-6 py-4 border-b border-white/5 bg-white/[0.01]">
              <span className="font-mono text-xs text-[#F6F4EF]/70">Neo4j Enterprise Graph</span>
            </div>

            <div className="relative flex-1 h-[calc(100%-53px)] overflow-auto p-8">
              {nodes.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-white/20 font-mono text-sm">
                  Loading Knowledge Graph...
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
                        <text x="50%" y="50%" fill="#F6F4EF80" fontSize="8" fontFamily="monospace">
                          <textPath href={`#edge-kg-${i}`} startOffset="50%" textAnchor="middle">{edge.label}</textPath>
                        </text>
                        <path id={`edge-kg-${i}`} d={edge.path} fill="none" />
                      </React.Fragment>
                    ))}
                  </svg>

                  {nodes.map((node) => {
                    const isSelected = selectedNode === node.id;
                    const color = "#9D4EDD";

                    return (
                      <motion.div 
                        key={node.id}
                        variants={itemVariants} 
                        className="absolute flex flex-col items-center justify-center gap-2 group cursor-pointer"
                        style={{ 
                          left: node.x - 60, 
                          top: node.y - 20,
                          width: 120,
                          height: 40,
                          zIndex: isSelected ? 10 : 1
                        }}
                        onClick={() => setSelectedNode(node.id)}
                      >
                        <div 
                          className="w-4 h-4 rounded-full border-2 transition-all flex items-center justify-center bg-[#0B0E12]"
                          style={{ 
                            borderColor: color, 
                            boxShadow: `0 0 16px ${color}66`,
                            transform: isSelected ? 'scale(1.25)' : 'scale(1)'
                          }}
                        >
                          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
                        </div>
                        <span 
                          className="font-mono text-[10px] transition-colors whitespace-nowrap bg-[#0B0E12]/90 px-1.5 py-0.5 rounded border border-white/10 text-[#F6F4EF]"
                        >
                          {node.label || node.id}
                        </span>
                      </motion.div>
                    );
                  })}
                </motion.div>
              )}
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
