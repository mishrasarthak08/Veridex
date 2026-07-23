"use client";

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Activity } from "lucide-react";
import Link from "next/link";

export default function RegisterPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
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
      const res = await fetch("http://localhost:8000/api/v1/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
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
    <div className="flex min-h-screen w-full items-center justify-center bg-[#0B0E12] font-body text-[#F6F4EF] p-4 py-12">
      <div className="w-full max-w-md bg-white/[0.02] border border-white/5 rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center gap-3 justify-center mb-8">
          <div className="bg-[#4C9FE8]/20 p-2 rounded-xl text-[#4C9FE8]">
            <Activity size={24} />
          </div>
          <h1 className="text-2xl font-display font-bold">Veridex</h1>
        </div>

        <h2 className="text-xl font-bold text-center mb-6">Create an Account</h2>

        {error && (
          <div className="mb-4 p-3 rounded-lg border border-[#E54D2E]/20 bg-[#E54D2E]/10 text-[#E54D2E] text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm text-white/60 mb-1">First Name</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
                placeholder="Jane"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-white/60 mb-1">Last Name</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
                placeholder="Doe"
              />
            </div>
          </div>
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
              minLength={8}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[#4C9FE8] hover:bg-[#4C9FE8]/90 text-black font-bold py-2.5 rounded-lg transition-colors flex justify-center items-center h-10 mt-2"
          >
            {isLoading ? <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : "Sign Up"}
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-white/40">
          Already have an account? <Link href="/login" className="text-[#4C9FE8] hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
