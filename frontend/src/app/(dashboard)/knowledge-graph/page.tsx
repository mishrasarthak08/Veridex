"use client";

import React, { useState, useEffect, useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Text, Html } from "@react-three/drei";
import { fetchGraph } from "@/lib/api";
import * as THREE from "three";
import { Search, Info } from "lucide-react";

interface NodeData {
  id: string;
  label: string;
  type: string;
  position: THREE.Vector3;
}

interface EdgeData {
  source: THREE.Vector3;
  target: THREE.Vector3;
}

const HOVER_SCALE = new THREE.Vector3(1.5, 1.5, 1.5);
const NORMAL_SCALE = new THREE.Vector3(1, 1, 1);

function GraphNode({ data, onClick }: { data: NodeData, onClick: () => void }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
      meshRef.current.rotation.x += 0.01;
      if (hovered) {
        meshRef.current.scale.lerp(HOVER_SCALE, 0.1);
      } else {
        meshRef.current.scale.lerp(NORMAL_SCALE, 0.1);
      }
    }
  });

  const color = data.type === 'connector' ? '#4C9FE8' : '#2FAE86';

  return (
    <group position={data.position}>
      <mesh
        ref={meshRef}
        onPointerOver={() => setHover(true)}
        onPointerOut={() => setHover(false)}
        onClick={onClick}
      >
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial 
          color={color} 
          emissive={color}
          emissiveIntensity={hovered ? 2 : 0.5}
          wireframe={true}
        />
      </mesh>
      <Html position={[0, -1, 0]} center>
        <div className="text-white text-xs font-mono whitespace-nowrap bg-black/60 border border-white/10 px-2 py-1 rounded backdrop-blur-sm pointer-events-none">
          {data.label}
        </div>
      </Html>
    </group>
  );
}

function GraphEdge({ edge }: { edge: EdgeData }) {
  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints([edge.source, edge.target]);
  }, [edge.source, edge.target]);

  const material = useMemo(() => {
    return new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.15 });
  }, []);

  const lineObj = useMemo(() => {
    return new THREE.Line(lineGeometry, material);
  }, [lineGeometry, material]);

  return <primitive object={lineObj} />;
}

function GalaxyGraph({ nodes, edges, onNodeClick }: { nodes: NodeData[], edges: EdgeData[], onNodeClick: (n: NodeData) => void }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001; // Slow global rotation
    }
  });

  return (
    <group ref={groupRef}>
      {edges.map((edge, i) => (
        <GraphEdge key={i} edge={edge} />
      ))}
      {nodes.map((node) => (
        <GraphNode key={node.id} data={node} onClick={() => onNodeClick(node)} />
      ))}
    </group>
  );
}

export default function KnowledgeGraph3DPage() {
  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [edges, setEdges] = useState<EdgeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);

  useEffect(() => {
    fetchGraph().then((data) => {
      // Convert 2D graph data into 3D positions using spherical distribution
      const nodeCount = data.nodes.length;
      const radius = Math.max(10, nodeCount * 0.5);
      
      const newNodes = data.nodes.map((n: any, i: number) => {
        const phi = Math.acos(-1 + (2 * i) / nodeCount);
        const theta = Math.sqrt(nodeCount * Math.PI) * phi;
        const x = radius * Math.cos(theta) * Math.sin(phi);
        const y = radius * Math.sin(theta) * Math.sin(phi);
        const z = radius * Math.cos(phi);

        return {
          id: n.id,
          label: n.label || n.id,
          type: n.type || 'document',
          position: new THREE.Vector3(x, y, z)
        };
      });

      const nodeMap = new Map(newNodes.map((n: any) => [n.id, n.position]));
      
      const newEdges = data.edges.map((e: any) => ({
        source: nodeMap.get(e.source) || new THREE.Vector3(),
        target: nodeMap.get(e.target) || new THREE.Vector3(),
      }));

      setNodes(newNodes);
      setEdges(newEdges);
      setLoading(false);
    });
  }, []);

  return (
    <div className="w-full h-full relative bg-[#050608] flex flex-col">
      <div className="absolute top-6 left-6 z-10">
        <h1 className="text-2xl font-display font-bold text-[#F6F4EF]">Knowledge Nexus (3D)</h1>
        <p className="text-white/40 text-sm font-mono mt-1">Interactive WebGL Galaxy Map</p>
      </div>

      <div className="absolute top-6 right-6 z-10 w-64">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
          <input 
            type="text" 
            placeholder="Search constellation..." 
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-[#4C9FE8] border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="flex-1 w-full h-full cursor-move">
          <Canvas camera={{ position: [0, 0, 30], fov: 60 }}>
            <color attach="background" args={["#050608"]} />
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
            
            <GalaxyGraph 
              nodes={nodes} 
              edges={edges} 
              onNodeClick={setSelectedNode} 
            />
            
            <OrbitControls 
              enablePan={true} 
              enableZoom={true} 
              enableRotate={true}
              autoRotate={true}
              autoRotateSpeed={0.5}
            />
          </Canvas>
        </div>
      )}

      {selectedNode && (
        <div className="absolute top-0 right-0 h-full w-80 bg-[#141820]/90 backdrop-blur-md border-l border-white/10 p-6 flex flex-col transform transition-transform shadow-2xl z-20">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-white">Node Details</h2>
            <button onClick={() => setSelectedNode(null)} className="text-white/60 hover:text-white">✕</button>
          </div>
          <div className="flex flex-col gap-4">
            <div className="p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs text-white/50 uppercase tracking-wider mb-1">Type</div>
              <div className="text-sm font-medium text-[#4C9FE8] capitalize">{selectedNode.type}</div>
            </div>
            <div className="p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs text-white/50 uppercase tracking-wider mb-1">Label</div>
              <div className="text-sm font-medium text-white break-words">{selectedNode.label}</div>
            </div>
          </div>
        </div>
      )}

      <div className="absolute bottom-6 left-6 max-w-sm bg-[#141820]/90 backdrop-blur-md border border-white/10 rounded-lg p-4 shadow-xl z-10 pointer-events-none">
        <h3 className="text-white font-semibold mb-2 flex items-center gap-2 text-sm">
          <Info size={16} className="text-[#4C9FE8]" />
          Knowledge Graph Guide
        </h3>
        <p className="text-white/60 text-xs leading-relaxed">
          Explore semantic relationships across your organization. 
          <strong> Click and drag</strong> to rotate the view. 
          <strong> Scroll</strong> to zoom in and out. 
          <strong> Click on any node</strong> to view its detailed properties.
        </p>
      </div>
    </div>
  );
}
