"use client";

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Activity, CheckCircle, XCircle } from "lucide-react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { AuthService } from "../../services/api";
import { API_URL } from "../../lib/api";
const registerSchema = z.object({
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[^A-Za-z0-9]/, "Password must contain at least one special character"),
  tosAccepted: z.boolean().refine(val => val === true, {
    message: "You must accept the Terms of Service",
  }),
  privacyAccepted: z.boolean().refine(val => val === true, {
    message: "You must accept the Privacy Policy",
  }),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const [error, setError] = useState("");
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    mode: "onChange",
  });

  const passwordValue = watch("password") || "";

  const onSubmit = async (data: RegisterFormValues) => {
    setError("");

    try {
      const resData = await AuthService.registerUserApiV1AuthRegisterPost({
        email: data.email,
        password: data.password,
        first_name: data.firstName || "",
        last_name: data.lastName || "",
        tos_accepted: data.tosAccepted,
        privacy_accepted: data.privacyAccepted,
      });

      login(resData.access_token);
    } catch (err: any) {
      if (err.body && (err.body.detail || err.body.error)) {
        setError(err.body.detail || err.body.error);
      } else {
        setError(err.message || "Registration failed");
      }
    }
  };

  const passwordRequirements = [
    { label: "At least 8 characters", test: (val: string) => val.length >= 8 },
    { label: "Uppercase letter", test: (val: string) => /[A-Z]/.test(val) },
    { label: "Lowercase letter", test: (val: string) => /[a-z]/.test(val) },
    { label: "Number", test: (val: string) => /[0-9]/.test(val) },
    { label: "Special character", test: (val: string) => /[^A-Za-z0-9]/.test(val) },
  ];

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

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm text-white/60 mb-1">First Name</label>
              <input
                type="text"
                {...register("firstName")}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
                placeholder="Jane"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-white/60 mb-1">Last Name</label>
              <input
                type="text"
                {...register("lastName")}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#4C9FE8]/50 transition-colors"
                placeholder="Doe"
              />
            </div>
          </div>
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
            
            {/* Password requirements visual indicator */}
            <div className="mt-3 space-y-1">
              {passwordRequirements.map((req, index) => {
                const isValid = req.test(passwordValue);
                return (
                  <div key={index} className={`flex items-center gap-2 text-xs ${isValid ? 'text-green-500' : 'text-zinc-500'}`}>
                    {isValid ? <CheckCircle className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    <span>{req.label}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-start gap-2">
              <input
                type="checkbox"
                id="tosAccepted"
                {...register("tosAccepted")}
                className="mt-1 h-4 w-4 rounded border-white/20 bg-white/5 text-[#4C9FE8] focus:ring-[#4C9FE8]/50 focus:ring-offset-0"
              />
              <label htmlFor="tosAccepted" className="text-sm text-white/70">
                I agree to the <Link href="/policies/terms" className="text-[#4C9FE8] hover:underline">Terms of Service</Link>
              </label>
            </div>
            {errors.tosAccepted && <p className="text-red-500 text-xs">{errors.tosAccepted.message}</p>}

            <div className="flex items-start gap-2">
              <input
                type="checkbox"
                id="privacyAccepted"
                {...register("privacyAccepted")}
                className="mt-1 h-4 w-4 rounded border-white/20 bg-white/5 text-[#4C9FE8] focus:ring-[#4C9FE8]/50 focus:ring-offset-0"
              />
              <label htmlFor="privacyAccepted" className="text-sm text-white/70">
                I agree to the <Link href="/policies/privacy" className="text-[#4C9FE8] hover:underline">Privacy Policy</Link>
              </label>
            </div>
            {errors.privacyAccepted && <p className="text-red-500 text-xs">{errors.privacyAccepted.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting || Object.keys(errors).length > 0}
            className="w-full bg-[#4C9FE8] hover:bg-[#4C9FE8]/90 text-black font-bold py-2.5 rounded-lg transition-colors flex justify-center items-center h-10 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : "Sign Up"}
          </button>
        </form>
        <div className="mt-6 flex items-center justify-between">
          <span className="w-1/5 border-b border-white/10 lg:w-1/4"></span>
          <span className="text-xs text-center text-white/40 uppercase">or sign up with</span>
          <span className="w-1/5 border-b border-white/10 lg:w-1/4"></span>
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={() => window.location.href = `${API_URL}/api/v1/auth/github/login`}
            className="flex-1 flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            GitHub
          </button>
          <button
            onClick={() => window.location.href = `${API_URL}/api/v1/auth/google/login`}
            className="flex-1 flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            <svg viewBox="0 0 24 24" className="w-5 h-5">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              <path fill="none" d="M1 1h22v22H1z" />
            </svg>
            Google
          </button>
        </div>

        <p className="mt-8 text-center text-sm text-white/40">
          Already have an account? <Link href="/login" className="text-[#4C9FE8] hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
