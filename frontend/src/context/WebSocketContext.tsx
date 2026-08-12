"use client";

import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { API_URL } from '@/lib/api';

interface WebSocketContextType {
  traces: any[];
  connected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType>({ traces: [], connected: false });

export const WebSocketProvider = ({ children }: { children: React.ReactNode }) => {
  const [traces, setTraces] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Determine WS URL from API_URL (handle https vs http)
    const wsUrl = API_URL.replace(/^http/, 'ws') + '/api/v1/ws/telemetry';
    
    const connect = () => {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'INIT') {
            setTraces(msg.data.map((t: any) => ({ ...t, time: new Date(t.time) })));
          } else if (msg.type === 'NEW_EVENT') {
            setTraces((prev) => [...prev, { ...msg.data, time: new Date(msg.data.time) }]);
          }
        } catch (e) {
          console.error("Error parsing WS message", e);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        // Auto-reconnect after 2 seconds
        setTimeout(connect, 2000);
      };

      ws.onerror = (err) => {
        console.error("WebSocket error", err);
        ws.close();
      };

      wsRef.current = ws;
    };

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ traces, connected }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);
