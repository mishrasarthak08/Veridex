import React from "react"
import { FileQuestion } from "lucide-react"

interface EmptyStateProps {
  title: string
  description: string
  action?: React.ReactNode
  icon?: React.ReactNode
}

export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center border border-dashed border-white/10 rounded-xl bg-white/[0.01]">
      <div className="h-12 w-12 rounded-full bg-white/5 flex items-center justify-center mb-4 text-[#4C9FE8]">
        {icon || <FileQuestion size={24} />}
      </div>
      <h3 className="text-lg font-display font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-white/50 max-w-md mb-6">{description}</p>
      {action}
    </div>
  )
}
