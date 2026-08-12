"use client"

import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      theme="dark"
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-[#050608] group-[.toaster]:text-[#F6F4EF] group-[.toaster]:border-white/10 group-[.toaster]:shadow-lg font-body",
          description: "group-[.toast]:text-white/60",
          actionButton:
            "group-[.toast]:bg-[#4C9FE8] group-[.toast]:text-white",
          cancelButton:
            "group-[.toast]:bg-white/5 group-[.toast]:text-white/60",
          error: "group-[.toaster]:border-[#E64C4C]/30 group-[.toaster]:bg-[#E64C4C]/10 group-[.toaster]:text-[#E64C4C]",
          success: "group-[.toaster]:border-[#2FAE86]/30 group-[.toaster]:bg-[#2FAE86]/10 group-[.toaster]:text-[#2FAE86]",
          warning: "group-[.toaster]:border-[#EAB308]/30 group-[.toaster]:bg-[#EAB308]/10 group-[.toaster]:text-[#EAB308]",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
