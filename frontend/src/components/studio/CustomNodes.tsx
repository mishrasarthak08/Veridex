import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Bot, Database, Zap } from "lucide-react";

export const AgentNode = ({ data }: { data: any }) => {
  return (
    <div className="bg-[#141820] border border-[#4C9FE8]/30 rounded-xl p-4 shadow-xl shadow-[#4C9FE8]/10 w-64 backdrop-blur-md">
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-[#4C9FE8] border-none" />
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-[#4C9FE8]/20 flex items-center justify-center text-[#4C9FE8]">
          <Bot size={18} />
        </div>
        <div>
          <div className="text-sm font-bold text-white">{data.label}</div>
          <div className="text-[10px] text-white/50 font-mono uppercase">{data.model || "GPT-4"}</div>
        </div>
      </div>
      <div className="text-xs text-white/70">
        {data.description || "Agent configuration pending..."}
      </div>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-[#4C9FE8] border-none" />
    </div>
  );
};

export const KnowledgeNode = ({ data }: { data: any }) => {
  return (
    <div className="bg-[#141820] border border-[#2FAE86]/30 rounded-xl p-4 shadow-xl shadow-[#2FAE86]/10 w-64 backdrop-blur-md">
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-[#2FAE86] border-none" />
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-[#2FAE86]/20 flex items-center justify-center text-[#2FAE86]">
          <Database size={18} />
        </div>
        <div>
          <div className="text-sm font-bold text-white">{data.label}</div>
          <div className="text-[10px] text-white/50 font-mono uppercase">Knowledge Source</div>
        </div>
      </div>
      <div className="text-xs text-white/70">
        {data.description || "Connect to feed data to agents"}
      </div>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-[#2FAE86] border-none" />
    </div>
  );
};

export const ActionNode = ({ data }: { data: any }) => {
  return (
    <div className="bg-[#141820] border border-[#E54D2E]/30 rounded-xl p-4 shadow-xl shadow-[#E54D2E]/10 w-64 backdrop-blur-md">
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-[#E54D2E] border-none" />
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-[#E54D2E]/20 flex items-center justify-center text-[#E54D2E]">
          <Zap size={18} />
        </div>
        <div>
          <div className="text-sm font-bold text-white">{data.label}</div>
          <div className="text-[10px] text-white/50 font-mono uppercase">Action / Tool</div>
        </div>
      </div>
      <div className="text-xs text-white/70">
        {data.description || "Executes a side-effect"}
      </div>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-[#E54D2E] border-none" />
    </div>
  );
};
