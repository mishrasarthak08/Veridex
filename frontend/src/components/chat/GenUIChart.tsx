import React from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export const GenUIChart = ({ data }: { data: any[] }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="w-full h-48 bg-[#0B0E12]/50 border border-white/10 rounded-lg p-4 mt-2 mb-2">
      <div className="text-xs font-mono text-white/50 mb-2 uppercase tracking-wider">
        System Telemetry
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4C9FE8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#4C9FE8" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
          <XAxis dataKey="name" stroke="#ffffff30" fontSize={10} tickLine={false} axisLine={false} />
          <YAxis stroke="#ffffff30" fontSize={10} tickLine={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: "#141820", borderColor: "#ffffff10", borderRadius: "8px" }}
            itemStyle={{ color: "#4C9FE8", fontWeight: "bold" }}
          />
          <Area type="monotone" dataKey="value" stroke="#4C9FE8" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
