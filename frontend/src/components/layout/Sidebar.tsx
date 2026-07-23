"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Network, 
  Plug, 
  ShieldCheck, 
  Activity,
  MessageSquare
} from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  { name: "Orchestrator", href: "/", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Knowledge Graph", href: "/knowledge-graph", icon: Network },
  { name: "Connectors", href: "/connectors", icon: Plug },
  { name: "Policies", href: "/policies", icon: ShieldCheck },
  { name: "Telemetry", href: "/telemetry", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-full border-r border-white/5 bg-[#0B0E12]/95 backdrop-blur-md flex flex-col shrink-0">
      <div className="h-16 flex items-center px-6 border-b border-white/5">
        <span className="font-display font-bold tracking-widest text-[#F6F4EF]">VERIDEX</span>
      </div>

      <nav className="flex-1 px-4 py-6 flex flex-col gap-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link key={item.name} href={item.href}>
              <div
                className={`relative flex items-center gap-3 px-3 py-2 rounded-md font-mono text-xs transition-colors cursor-pointer ${
                  isActive
                    ? "text-[#4C9FE8] bg-[#4C9FE8]/10"
                    : "text-white/40 hover:text-white/80 hover:bg-white/5"
                }`}
              >
                <Icon size={16} />
                <span>{item.name}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-[#4C9FE8] rounded-full"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 mt-auto border-t border-white/5">
        <div className="flex items-center gap-3 px-3 py-2 rounded-md border border-white/5 bg-white/5">
          <div className="w-6 h-6 rounded-full bg-[#E54D2E]/20 text-[#E54D2E] flex items-center justify-center font-bold text-[10px]">
            SA
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-white/80 font-mono">System Admin</span>
            <span className="text-[9px] text-white/40 font-mono">u_dev</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
