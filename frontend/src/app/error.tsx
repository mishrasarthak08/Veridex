"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Unhandled runtime error:", error);
  }, [error]);

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-zinc-950 text-white">
      <AlertTriangle className="h-16 w-16 text-red-500 mb-6" />
      <h2 className="text-2xl font-bold mb-2">Something went wrong!</h2>
      <p className="text-zinc-400 mb-8 max-w-md text-center">
        An unexpected error occurred in the application.
      </p>
      <Button onClick={() => reset()} variant="default" className="flex items-center gap-2">
        <RefreshCw className="h-4 w-4" />
        Try again
      </Button>
    </div>
  );
}
