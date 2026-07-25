import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Loading..." }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full py-16 px-4 text-center">
      <Loader2 size={32} className="text-[#4C9FE8] animate-spin mb-4" />
      <p className="text-white/40 font-mono text-sm">
        {message}
      </p>
    </div>
  );
}
