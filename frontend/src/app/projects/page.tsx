"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FolderGit2, Plus } from "lucide-react";
import { EmptyState } from "../../components/ui/EmptyState";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { OpenAPI } from "../../client";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem("token");
      
      // We haven't generated a ProjectsService yet, so fallback to raw fetch via OpenAPI.BASE
      const res = await fetch(`${OpenAPI.BASE}/api/v1/projects/`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (!res.ok) {
        throw new Error("Failed to load projects. You may not have access.");
      }
      
      const data = await res.json();
      setProjects(data.data || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading your projects..." />;
  if (error) return <ErrorState message={error} onRetry={fetchProjects} />;

  return (
    <div className="flex-1 p-8 max-w-7xl mx-auto w-full">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-[#F6F4EF]">Projects & Workspaces</h1>
          <p className="text-white/40 font-mono text-sm mt-1">Manage your active workspaces</p>
        </div>
        
        <button className="flex items-center gap-2 bg-[#4C9FE8] hover:bg-[#4C9FE8]/90 text-black font-bold py-2 px-4 rounded-lg transition-colors font-mono text-xs">
          <Plus size={16} />
          New Project
        </button>
      </div>

      {projects.length === 0 ? (
        <EmptyState 
          title="No Projects Found"
          description="You don't have access to any projects yet. Create a new one or ask an org admin to add you."
          icon={<FolderGit2 size={32} />}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((proj) => (
            <motion.div 
              key={proj.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/[0.02] border border-white/5 rounded-xl p-6 hover:bg-white/[0.04] hover:border-white/10 transition-colors cursor-pointer group relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#4C9FE8] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              
              <div className="flex items-start justify-between mb-4">
                <div className="w-10 h-10 rounded-lg bg-[#4C9FE8]/10 text-[#4C9FE8] flex items-center justify-center">
                  <FolderGit2 size={20} />
                </div>
                <span className="text-[10px] font-mono px-2 py-1 rounded bg-white/5 text-white/40 border border-white/5">
                  {proj.role || "Member"}
                </span>
              </div>
              
              <h3 className="text-lg font-bold text-[#F6F4EF] mb-1">{proj.name}</h3>
              <p className="text-sm text-white/40 font-mono line-clamp-2">{proj.description || "No description provided."}</p>
              
              <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs font-mono text-white/30">
                <span>Updated 2h ago</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
