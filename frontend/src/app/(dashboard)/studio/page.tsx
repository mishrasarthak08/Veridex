"use client";
import React, { useCallback, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { API_URL } from "@/lib/api";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
  Panel
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { AgentNode, KnowledgeNode, ActionNode } from "@/components/studio/CustomNodes";
import { Play, Save, Settings2, Info } from "lucide-react";

const nodeTypes = {
  agent: AgentNode,
  knowledge: KnowledgeNode,
  action: ActionNode,
};

const initialNodes: Node[] = [
  {
    id: "1",
    type: "agent",
    position: { x: 250, y: 100 },
    data: { label: "Triage Agent", model: "GPT-4", description: "Routes incoming tasks" },
  },
  {
    id: "2",
    type: "knowledge",
    position: { x: 100, y: 300 },
    data: { label: "Confluence Docs", description: "Internal company policies" },
  },
  {
    id: "3",
    type: "action",
    position: { x: 400, y: 300 },
    data: { label: "Slack Notifier", description: "Sends alerts to #devops" },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "2", target: "1", animated: true, style: { stroke: "#2FAE86", strokeWidth: 2 } },
  { id: "e1-3", source: "1", target: "3", animated: true, style: { stroke: "#4C9FE8", strokeWidth: 2 } },
];

export default function StudioPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges]
  );

  const [isSaving, setIsSaving] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);

  const handleSaveSwarm = async () => {
    setIsSaving(true);
    try {
      // Mock Project ID
      const projectId = "proj_123";
      const token = localStorage.getItem("token");
      await axios.post(`${API_URL}/api/v1/projects/${projectId}/swarm`, {
        nodes,
        edges,
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success("Swarm Configuration Saved", {
        description: `Successfully persisted ${nodes.length} nodes to the database.`
      });
    } catch (error) {
      console.error(error);
      toast.error("Failed to save swarm configuration");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeploySwarm = async () => {
    setIsDeploying(true);
    try {
      const projectId = "proj_123";
      const token = localStorage.getItem("token");
      await axios.post(`${API_URL}/api/v1/projects/${projectId}/deploy`, {}, {
          headers: { Authorization: `Bearer ${token}` }
      });
      toast.success("Swarm Deployed!", {
        description: "The Swarm Engine has been initiated. Open the Terminal to view live execution logs."
      });
    } catch (error) {
      console.error(error);
      toast.error("Failed to deploy swarm");
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <div className="w-full h-full relative bg-[#050608]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        className="bg-[#050608]"
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#ffffff10" />
        <Controls className="!bg-[#141820] !border-[#ffffff10] !fill-white/70" />
        <MiniMap 
          nodeColor={(node) => {
            if (node.type === 'agent') return '#4C9FE8';
            if (node.type === 'knowledge') return '#2FAE86';
            if (node.type === 'action') return '#E54D2E';
            return '#fff';
          }}
          maskColor="rgba(0,0,0,0.7)"
          style={{ backgroundColor: '#141820', border: '1px solid rgba(255,255,255,0.1)' }}
        />
        <Panel position="top-right" className="flex gap-2">
          <button 
            onClick={() => toast.info("Configuration Panel", { description: "Node configuration settings are coming soon." })}
            className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-md hover:bg-white/10 text-white/80 transition-colors text-sm"
          >
            <Settings2 size={16} />
            Configure
          </button>
          <button 
            onClick={handleSaveSwarm}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-md hover:bg-white/10 text-white/80 transition-colors text-sm disabled:opacity-50"
          >
            <Save size={16} />
            {isSaving ? "Saving..." : "Save Swarm"}
          </button>
          <button 
            onClick={handleDeploySwarm}
            disabled={isDeploying}
            className="flex items-center gap-2 px-4 py-2 bg-[#4C9FE8] text-black font-semibold rounded-md hover:bg-[#4C9FE8]/90 transition-colors shadow-lg shadow-[#4C9FE8]/20 text-sm disabled:opacity-50"
          >
            <Play size={16} />
            {isDeploying ? "Deploying..." : "Deploy Swarm"}
          </button>
        </Panel>
        <Panel position="bottom-left" className="bg-[#141820]/90 backdrop-blur-md border border-white/10 rounded-lg p-4 max-w-sm shadow-xl m-4">
          <h3 className="text-white font-semibold mb-2 flex items-center gap-2 text-sm">
            <Info size={16} className="text-[#4C9FE8]" />
            Swarm Studio Guide
          </h3>
          <p className="text-white/60 text-xs leading-relaxed">
            Drag and drop nodes to build your multi-agent architecture. Connect <strong>Agents</strong> to <strong>Knowledge</strong> sources and <strong>Action</strong> nodes to define their capabilities. Click <strong>Deploy</strong> to launch your swarm into production.
          </p>
        </Panel>
      </ReactFlow>
    </div>
  );
}
