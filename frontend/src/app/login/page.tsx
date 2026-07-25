"use client";

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Activity } from "lucide-react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter } from "next/navigation";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const [error, setError] = useState("");
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const router = useRouter();

  const onSubmit = async (data: LoginFormValues) => {
    setError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", data.email);
      formData.append("password", data.password);

      // Make sure NEXT_PUBLIC_API_URL is properly configured for the app
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!res.ok) {
        const resData = await res.json();
        throw new Error(resData.detail || "Login failed");
      }

      const resData = await res.json();
      
      if (resData.requires_mfa) {
        // Store partial token and redirect to MFA verification page
        sessionStorage.setItem("mfa_token", resData.mfa_token);
        router.push("/mfa");
        return;
      }
      
      login(resData.access_token);
    } catch (err: any) {
      setError(err.message);
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

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-1">Email</label>
            <input
              type="email"
              {...register("email")}
              className={`w-full bg-white/5 border ${errors.email ? 'border-red-500' : 'border-white/10'} rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors`}
              placeholder="you@example.com"
            />
            {errors.email && (
              <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Password</label>
            <input
              type="password"
              {...register("password")}
              className={`w-full bg-white/5 border ${errors.password ? 'border-red-500' : 'border-white/10'} rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors`}
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-[#4C9FE8] hover:bg-[#4C9FE8]/90 text-black font-bold py-2.5 rounded-lg transition-colors flex justify-center items-center h-10"
          >
            {isSubmitting ? <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : "Sign In"}
          </button>
        </form>



        <p className="mt-8 text-center text-sm text-white/40">
          Don't have an account? <Link href="/register" className="text-[#4C9FE8] hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
