"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getCurrentUser } from "../lib/api";

type User = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (err) {
          console.error("Failed to fetch user", err);
          localStorage.removeItem("token");
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  useEffect(() => {
    // Route protection
    if (!loading) {
      const publicPaths = ["/login", "/register", "/auth/callback"];
      const isPublic = publicPaths.some(p => pathname?.startsWith(p));
      
      if (!user && !isPublic) {
        router.push("/login");
      } else if (user && isPublic) {
        router.push("/");
      }
    }
  }, [user, loading, pathname, router]);

  const login = (token: string) => {
    localStorage.setItem("token", token);
    // Reload to fetch user and redirect
    window.location.href = "/";
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {loading ? (
        <div className="flex h-screen w-full items-center justify-center bg-[#0B0E12]">
          <div className="animate-spin h-8 w-8 border-4 border-[#4C9FE8] border-t-transparent rounded-full"></div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
