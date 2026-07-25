import React from "react";
import { FolderOpen } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full py-16 px-4 text-center border border-dashed border-white/10 rounded-2xl bg-white/[0.01]">
      <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-white/20 mb-6">
        {icon || <FolderOpen size={32} strokeWidth={1.5} />}
      </div>
      <h3 className="text-[#F6F4EF] font-display font-semibold text-lg mb-2">{title}</h3>
      <p className="text-white/40 font-mono text-sm max-w-sm mb-8 leading-relaxed">
        {description}
      </p>
      {action && (
        <div className="mt-2">
          {action}
        </div>
      )}
    </div>
  );
}
