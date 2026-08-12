import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { CommandPalette } from "@/components/ui/CommandPalette";
import { TopSearchButton } from "@/components/ui/TopSearchButton";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex w-full h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 bg-[#0B0E12]">
        {/* Global Topbar */}
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-6 shrink-0 bg-black/20 backdrop-blur-md">
          <div className="flex items-center gap-2 flex-1">
            <TopSearchButton />
          </div>
        </header>
        <main className="flex-1 overflow-hidden relative">
          {children}
        </main>
      </div>
      <CommandPalette />
    </div>
  );
}
