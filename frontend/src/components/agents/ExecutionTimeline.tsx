import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { useWebSocket } from '../../context/WebSocketContext';

export interface TimelineEvent {
  id: string;
  timestamp: string;
  state: string;
  details?: Record<string, any>;
}

export function ExecutionTimeline() {
  const { traces, connected: isConnected } = useWebSocket();

  // Convert WebSocket trace data to TimelineEvent format
  const events: TimelineEvent[] = traces.map((t, idx) => ({
    id: idx.toString(),
    timestamp: t.time.toISOString(),
    state: t.type === 'system' ? 'planning' : t.type === 'success' ? 'complete' : t.type === 'error' ? 'failed' : 'executing',
    details: { goal: t.message }
  })).reverse().slice(0, 50);

  const getStateIcon = (state: string) => {
    switch (state) {
      case 'idle':
        return <Clock className="w-5 h-5 text-gray-400" />;
      case 'planning':
        return <Brain className="w-5 h-5 text-blue-400" />;
      case 'executing':
        return <Loader2 className="w-5 h-5 text-yellow-400 animate-spin" />;
      case 'awaiting_approval':
        return <AlertCircle className="w-5 h-5 text-orange-400" />;
      case 'complete':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'idle': return 'bg-gray-500/10 border-gray-500/20 text-gray-400';
      case 'planning': return 'bg-blue-500/10 border-blue-500/20 text-blue-400';
      case 'executing': return 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400';
      case 'awaiting_approval': return 'bg-orange-500/10 border-orange-500/20 text-orange-400';
      case 'complete': return 'bg-green-500/10 border-green-500/20 text-green-400';
      case 'failed': return 'bg-red-500/10 border-red-500/20 text-red-400';
      default: return 'bg-gray-500/10 border-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="flex flex-col h-full bg-white/[0.02] border border-white/5 rounded-xl overflow-hidden backdrop-blur-sm">
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between bg-black/20">
        <h3 className="text-sm font-semibold text-white/90 flex items-center gap-2">
          <Brain size={16} className="text-[#4C9FE8]" />
          Agent Orchestrator
        </h3>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            {isConnected && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            )}
            <span className={`relative inline-flex rounded-full h-2 w-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          </span>
          <span className="text-xs font-mono text-white/50">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {events.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-white/30 space-y-2">
            <Clock size={24} className="opacity-50" />
            <span className="text-sm">Waiting for orchestrator events...</span>
          </div>
        ) : (
          <AnimatePresence>
            {events.map((event, i) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                layout
                className="relative pl-6"
              >
                {/* Timeline line */}
                {i !== events.length - 1 && (
                  <div className="absolute left-[11px] top-7 bottom-[-20px] w-px bg-white/10" />
                )}
                
                <div className={`absolute left-0 top-1 p-0.5 rounded-full bg-[#0B0E12] border ${getStateColor(event.state).split(' ')[1]}`}>
                  <div className="w-4 h-4 flex items-center justify-center">
                    {getStateIcon(event.state)}
                  </div>
                </div>
                
                <div className={`p-3 rounded-lg border ${getStateColor(event.state)} shadow-lg`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold uppercase tracking-wider">{event.state.replace('_', ' ')}</span>
                    <span className="text-[10px] font-mono opacity-60">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {event.details?.goal && (
                    <div className="text-sm text-white/80 mt-2 bg-black/20 p-2 rounded border border-white/5">
                      <span className="text-xs opacity-50 block mb-1">GOAL</span>
                      {event.details.goal}
                    </div>
                  )}
                  {event.details?.error && (
                    <div className="text-sm text-red-400 mt-2 bg-red-500/10 p-2 rounded border border-red-500/20 font-mono text-xs">
                      {event.details.error}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
