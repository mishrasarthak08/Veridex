import React from 'react';
import { motion } from 'framer-motion';

export type StatusType = 'queued' | 'running' | 'done' | 'blocked' | 'trace' | 'degraded';

interface StatusPillProps {
  status: StatusType;
}

export function StatusPill({ status }: StatusPillProps) {
  const normalizedStatus = status === 'degraded' ? 'running' : status;

  const colorMap = {
    queued: 'text-zinc-500 border-zinc-500/20 bg-zinc-500/10',
    running: 'text-[#F5A623] border-[#F5A623]/20 bg-[#F5A623]/10',
    done: 'text-[#2FAE86] border-[#2FAE86]/20 bg-[#2FAE86]/10',
    blocked: 'text-[#E0483D] border-[#E0483D]/20 bg-[#E0483D]/10',
    trace: 'text-[#4C9FE8] border-[#4C9FE8]/20 bg-[#4C9FE8]/10',
  };

  const dotColorMap = {
    queued: 'bg-zinc-500',
    running: 'bg-[#F5A623]',
    done: 'bg-[#2FAE86]',
    blocked: 'bg-[#E0483D]',
    trace: 'bg-[#4C9FE8]',
  };

  const textMap = {
    queued: 'queued',
    running: status === 'degraded' ? 'degraded' : 'running',
    done: 'done',
    blocked: 'blocked',
    trace: 'trace',
  };

  const isActive = normalizedStatus === 'running' || normalizedStatus === 'trace';

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[11px] font-mono leading-none ${colorMap[normalizedStatus]}`}
    >
      <div className="relative flex items-center justify-center">
        <motion.div 
          className={`w-1.5 h-1.5 rounded-full ${dotColorMap[normalizedStatus]}`} 
        />
        {isActive && (
          <motion.div
            className={`absolute w-full h-full rounded-full ${dotColorMap[normalizedStatus]}`}
            animate={{ scale: [1, 2.5], opacity: [0.6, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
          />
        )}
      </div>
      <span>{textMap[normalizedStatus]}</span>
    </motion.div>
  );
}
