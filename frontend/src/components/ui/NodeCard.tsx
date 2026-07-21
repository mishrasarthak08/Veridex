import React from 'react';
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
    <div className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-[#0B0E12] shadow-sm">
      <div className="flex items-center gap-4">
        {/* Icon Slot: A hollow circle */}
        <div className={`w-4 h-4 rounded-full border-2 ${getIconColor()}`} />
        
        {/* Identifier and Subtitle */}
        <div className="flex flex-col gap-1">
          <div className="font-mono text-[13px] text-[#F6F4EF]">{id}</div>
          {subtitle && (
            <div className="font-mono text-[11px] text-[#F6F4EF]/50">
              {subtitle}
            </div>
          )}
        </div>
      </div>

      {/* Right Aligned Status Pill */}
      <div>
        <StatusPill status={status} />
      </div>
    </div>
  );
}
