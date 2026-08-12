"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { ShieldAlert, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { AuthService, OpenAPI } from "../../services/api";
export default function MfaPage() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const token = sessionStorage.getItem("mfa_token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  const verifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const mfaToken = sessionStorage.getItem("mfa_token") || "";
    const originalToken = OpenAPI.TOKEN;
    OpenAPI.TOKEN = mfaToken;

    try {
      const resData = await AuthService.mfaVerifyApiV1AuthMfaVerifyPost({ code });

      sessionStorage.removeItem("mfa_token");
      login(resData.access_token);
      router.push("/evaluations");
    } catch (err: any) {
      if (err.body && (err.body.detail || err.body.error)) {
        setError(err.body.detail || err.body.error);
      } else {
        setError(err.message || "Verification failed");
      }
    } finally {
      OpenAPI.TOKEN = originalToken;
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#0B0E12] font-body text-[#F6F4EF] p-4">
      <div className="w-full max-w-md bg-white/[0.02] border border-white/5 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center gap-3 justify-center mb-8">
          <div className="bg-[#4C9FE8]/20 p-2 rounded-xl text-[#4C9FE8]">
            <ShieldAlert size={24} />
          </div>
          <h1 className="text-2xl font-display font-bold">Veridex MFA</h1>
        </div>

        <h2 className="text-xl font-bold text-center mb-2">Two-Factor Authentication</h2>
        <p className="text-center text-sm text-white/60 mb-6">Enter the 6-digit code from your authenticator app.</p>

        {error && (
          <div className="mb-4 p-3 rounded-lg border border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E] text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={verifyCode} className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-1 text-center">Authentication Code</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-2xl tracking-[0.5em] text-center focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
              placeholder="000000"
              maxLength={6}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading || code.length !== 6}
            className="w-full bg-[#4C9FE8] hover:bg-[#4C9FE8]/90 text-black font-bold py-2.5 rounded-lg transition-colors flex justify-center items-center h-10 mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : "Verify Code"}
          </button>
        </form>
      </div>
    </div>
  );
}
