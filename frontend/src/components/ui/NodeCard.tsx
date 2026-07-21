import React from 'react';
import { motion } from 'framer-motion';
import { StatusPill, StatusType } from './StatusPill';

interface NodeCardProps {
  id: string;
  subtitle?: React.ReactNode;
  status: StatusType;
  iconColor?: string;
}

export function NodeCard({ id, subtitle, status, iconColor }: NodeCardProps) {
  // Determine icon ring color based on status or override
  const getIconColor = () => {
    if (iconColor) return iconColor;
    switch (status) {
      case 'running':
      case 'degraded':
        return 'border-[#F5A623]';
      case 'done':
        return 'border-[#2FAE86]';
      case 'blocked':
        return 'border-[#E0483D]';
      case 'trace':
        return 'border-[#4C9FE8]';
      case 'queued':
      default:
        return 'border-zinc-500';
    }
  };

  return (
    <motion.div 
      layout
      whileHover={{ scale: 1.02, y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-[#0B0E12] shadow-sm hover:border-white/15 hover:shadow-xl hover:shadow-black/50 hover:bg-white/[0.03] transition-colors cursor-default group"
    >
      <div className="flex items-center gap-4">
        {/* Icon Slot: A hollow circle */}
        <div className="relative">
          <motion.div 
            layout
            className={`w-4 h-4 rounded-full border-2 ${getIconColor()} transition-colors duration-300 group-hover:shadow-[0_0_8px_rgba(255,255,255,0.1)]`} 
          />
        </div>
        
        {/* Identifier and Subtitle */}
        <div className="flex flex-col gap-1">
          <motion.div layout className="font-mono text-[13px] text-[#F6F4EF] transition-colors group-hover:text-white">{id}</motion.div>
          {subtitle && (
            <motion.div layout className="font-mono text-[11px] text-[#F6F4EF]/50 transition-colors group-hover:text-[#F6F4EF]/80">
              {subtitle}
            </motion.div>
          )}
        </div>
      </div>

      {/* Right Aligned Status Pill */}
      <div>
        <StatusPill status={status} />
      </div>
    </motion.div>
  );
}
