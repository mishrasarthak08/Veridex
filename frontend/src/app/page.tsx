"use client";

import { useState, useEffect, useRef } from "react";
import { submitGoal, getTimelineUrl } from "../lib/api";

type TimelineEvent = {
  event: string;
  data: any;
  timestamp: string;
};

export default function Home() {
  const [goal, setGoal] = useState("");
  const [status, setStatus] = useState("Idle");
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim()) return;

    setStatus("Submitting...");
    setEvents([]);

    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      await submitGoal(goal);
      setStatus("Goal submitted. Connecting to timeline stream...");

      // Open SSE connection
      const es = new EventSource(getTimelineUrl());
      eventSourceRef.current = es;

      es.onmessage = (event) => {
        // Fallback for default 'message' event
        try {
          const data = JSON.parse(event.data);
          setEvents((prev) => [...prev, { event: "message", data, timestamp: new Date().toISOString() }]);
        } catch (err) {
          setEvents((prev) => [...prev, { event: "message", data: event.data, timestamp: new Date().toISOString() }]);
        }
      };

      // Listen for custom 'timeline_update' events
      es.addEventListener("timeline_update", (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          setEvents((prev) => [...prev, { event: "timeline_update", data, timestamp: new Date().toISOString() }]);
        } catch (err) {
          setEvents((prev) => [...prev, { event: "timeline_update", data: event.data, timestamp: new Date().toISOString() }]);
        }
      });

      es.onerror = (err) => {
        console.error("SSE Error:", err);
        setStatus("Error connecting to stream.");
        es.close();
      };

      setStatus("Streaming execution timeline...");
    } catch (err: any) {
      console.error(err);
      setStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-zinc-50 dark:bg-black font-sans text-zinc-900 dark:text-zinc-50">
      <main className="max-w-4xl mx-auto space-y-8">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight">Veridex Orchestrator</h1>
          <p className="text-zinc-500 dark:text-zinc-400">Submit a goal and watch the execution timeline stream in real-time.</p>
        </header>

        <section className="bg-white dark:bg-zinc-900 p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. Test my knowledge base..."
              className="flex-1 px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={status === "Submitting..."}
            />
            <button
              type="submit"
              disabled={status === "Submitting..." || !goal.trim()}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Run Agent
            </button>
          </form>
          <div className="mt-4 text-sm font-medium text-zinc-500 dark:text-zinc-400">
            Status: <span className="text-blue-600 dark:text-blue-400">{status}</span>
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-xl font-medium">Execution Timeline</h2>
          <div className="bg-zinc-900 rounded-xl p-4 min-h-[400px] overflow-y-auto font-mono text-sm border border-zinc-800">
            {events.length === 0 ? (
              <p className="text-zinc-500 italic">No events yet. Submit a goal to start the timeline.</p>
            ) : (
              <div className="space-y-3">
                {events.map((evt, idx) => (
                  <div key={idx} className="flex gap-4">
                    <span className="text-zinc-500 shrink-0">
                      {new Date(evt.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                    <div className="flex-1 space-y-1">
                      <span className="text-blue-400 font-semibold">[{evt.event}]</span>
                      <pre className="text-zinc-300 whitespace-pre-wrap break-words">
                        {typeof evt.data === 'object' ? JSON.stringify(evt.data, null, 2) : evt.data}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
