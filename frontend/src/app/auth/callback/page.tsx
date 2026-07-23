"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "../../../context/AuthContext";

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      login(token);
    } else {
      router.push("/login?error=OAuthFailed");
    }
  }, [searchParams, login, router]);

  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#0B0E12]">
      <div className="animate-spin h-8 w-8 border-4 border-[#4C9FE8] border-t-transparent rounded-full"></div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex h-screen w-full items-center justify-center bg-[#0B0E12]">
        <div className="animate-spin h-8 w-8 border-4 border-[#4C9FE8] border-t-transparent rounded-full"></div>
      </div>
    }>
      <CallbackHandler />
    </Suspense>
  );
}
