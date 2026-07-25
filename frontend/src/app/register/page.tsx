"use client";

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Activity, CheckCircle, XCircle } from "lucide-react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${apiUrl}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          first_name: data.firstName || "",
          last_name: data.lastName || "",
          tos_accepted: data.tosAccepted,
          privacy_accepted: data.privacyAccepted,
        }),
      });

      if (!res.ok) {
        const resData = await res.json();
        throw new Error(resData.detail || "Registration failed");
      }

      const resData = await res.json();
      login(resData.access_token);
    } catch (err: any) {
      setError(err.message);
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

        <p className="mt-8 text-center text-sm text-white/40">
          Already have an account? <Link href="/login" className="text-[#4C9FE8] hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
