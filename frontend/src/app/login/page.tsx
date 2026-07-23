"use client";

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Activity } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      // For OAuth2PasswordRequestForm, we send form urlencoded data
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }

      const data = await res.json();
      login(data.access_token);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#0B0E12] font-body text-[#F6F4EF] p-4">
      <div className="w-full max-w-md bg-white/[0.02] border border-white/5 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center gap-3 justify-center mb-8">
          <div className="bg-[#4C9FE8]/20 p-2 rounded-xl text-[#4C9FE8]">
            <Activity size={24} />
          </div>
          <h1 className="text-2xl font-display font-bold">Veridex</h1>
        </div>

        <h2 className="text-xl font-bold text-center mb-6">Welcome Back</h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg border border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E] text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[#4C9FE8] hover:bg-[#4C9FE8]/90 text-black font-bold py-2.5 rounded-lg transition-colors flex justify-center items-center h-10"
          >
            {isLoading ? <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : "Sign In"}
          </button>
        </form>

        <div className="mt-6 flex items-center gap-4">
          <div className="flex-1 h-px bg-white/10"></div>
          <span className="text-xs text-white/40 uppercase tracking-widest">or</span>
          <div className="flex-1 h-px bg-white/10"></div>
        </div>

        <div className="mt-6 space-y-3">
          <a
            href="http://localhost:8000/api/v1/auth/github/login"
            className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium py-2.5 rounded-lg transition-colors flex justify-center items-center gap-2"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
            Continue with GitHub
          </a>
          <a
            href="http://localhost:8000/api/v1/auth/google/login"
            className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium py-2.5 rounded-lg transition-colors flex justify-center items-center gap-2"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 12v10"></path><path d="M12 12 2.5 7.5"></path><path d="M12 12 21.5 7.5"></path><path d="M12 12l-9.5-4.5"></path><path d="M12 12l9.5-4.5"></path></svg>
            Continue with Google
          </a>
        </div>

        <p className="mt-8 text-center text-sm text-white/40">
          Don't have an account? <Link href="/register" className="text-[#4C9FE8] hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
