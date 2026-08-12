"use client"

import React, { useEffect, useState } from "react"
import { WifiOff } from "lucide-react"

export function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(false)

  useEffect(() => {
    function handleOnline() { setIsOffline(false) }
    function handleOffline() { setIsOffline(true) }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    setIsOffline(!navigator.onLine)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (!isOffline) return null

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-[#EAB308] text-black px-4 py-2 rounded-full shadow-lg shadow-[#EAB308]/20 text-sm font-semibold animate-in slide-in-from-bottom-5">
      <WifiOff size={16} />
      You are currently offline. Some features may be unavailable.
    </div>
  )
}
