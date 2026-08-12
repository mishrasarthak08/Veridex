"use client";

import React, { useEffect, useState } from "react";
import { Command } from "cmdk";
import { useRouter } from "next/navigation";
import { 
  Network, 
  MessageSquare, 
  Settings, 
  Activity, 
  Database,
  Plug,
  ShieldCheck,
  Search,
  Workflow,
  BrainCircuit,
  LineChart,
  Terminal,
  Trash2,
  RefreshCw
} from "lucide-react";
import "./command-palette.css"; // Custom styles for cmdk

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-[#11161d] border border-white/10 rounded-xl shadow-2xl overflow-hidden shadow-[#4C9FE8]/5">
        <Command label="Command Menu" className="flex flex-col h-full w-full">
          <div className="flex items-center border-b border-white/10 px-4">
            <Search className="w-5 h-5 text-white/40" />
            <Command.Input 
              placeholder="Type a command or search..." 
              className="w-full bg-transparent border-none focus:outline-none text-white px-4 py-4 text-sm font-mono placeholder:text-white/30"
              autoFocus
            />
          </div>
          
          <Command.List className="max-h-[60vh] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-white/40 font-mono">
              No results found.
            </Command.Empty>

            <Command.Group heading="Global Search (Projects & Agents)" className="px-2 py-2 text-xs font-mono text-white/40">
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/projects"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Database className="w-4 h-4 text-[#4C9FE8]" />
                <span>Search: Default Workspace (Project ID: proj_123)</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/studio"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Workflow className="w-4 h-4 text-[#2FAE86]" />
                <span>Search: Triage Agent (Active Swarm)</span>
              </Command.Item>
            </Command.Group>

            <Command.Group heading="Navigation" className="px-2 py-2 text-xs font-mono text-white/40 border-t border-white/5 mt-2 pt-4">
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/chat"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <MessageSquare className="w-4 h-4" />
                <span>New Chat Session</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/knowledge-graph"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Network className="w-4 h-4" />
                <span>Explore Knowledge Graph</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/projects"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Database className="w-4 h-4" />
                <span>View Projects</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/studio"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Workflow className="w-4 h-4" />
                <span>Veridex Studio (IDE)</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/memory"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <BrainCircuit className="w-4 h-4" />
                <span>Agent Memory Store</span>
              </Command.Item>
            </Command.Group>

            <Command.Group heading="Platform" className="px-2 py-2 text-xs font-mono text-white/40">
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/connectors"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Plug className="w-4 h-4" />
                <span>Manage Connectors</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/terminal"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Terminal className="w-4 h-4" />
                <span>Developer Command Center</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/evaluations"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <LineChart className="w-4 h-4" />
                <span>Agent Evaluations</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => router.push("/policies"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>RBAC Policies</span>
              </Command.Item>
            </Command.Group>

            <Command.Group heading="Quick Actions" className="px-2 py-2 text-xs font-mono text-white/40 border-t border-white/5 mt-2 pt-4">
              <Command.Item 
                onSelect={() => runCommand(() => console.log("Pruning Memory..."))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-red-500/10 cursor-pointer text-red-400 transition-colors my-1 aria-selected:bg-red-500/20"
              >
                <Trash2 className="w-4 h-4" />
                <span>Prune Old Agent Memories</span>
              </Command.Item>
              <Command.Item 
                onSelect={() => runCommand(() => console.log("Running Evals..."))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-green-500/10 cursor-pointer text-green-400 transition-colors my-1 aria-selected:bg-green-500/20"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Run Evaluation Suite</span>
              </Command.Item>
            </Command.Group>

            <Command.Group heading="Settings" className="px-2 py-2 text-xs font-mono text-white/40 border-t border-white/5 mt-2 pt-4">
              <Command.Item 
                onSelect={() => runCommand(() => console.log("Settings"))}
                className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer text-white/80 transition-colors my-1 aria-selected:bg-[#4C9FE8]/10 aria-selected:text-[#4C9FE8]"
              >
                <Settings className="w-4 h-4" />
                <span>User Preferences</span>
              </Command.Item>
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
