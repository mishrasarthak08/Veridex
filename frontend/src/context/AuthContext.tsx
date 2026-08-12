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
  token: string | null;
  activeTenant: string;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
  setTenant: (tenantId: string) => void;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  activeTenant: "default_tenant",
  loading: true,
  login: () => {},
  logout: () => {},
  setTenant: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [activeTenant, setActiveTenant] = useState<string>("default_tenant");
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const isTokenExpired = (token: string) => {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
      } catch (e) {
        return true;
      }
    };

    const initAuth = async () => {
      const storedTenant = localStorage.getItem("tenant_id") || "default_tenant";
      setActiveTenant(storedTenant);
      
      const storedToken = localStorage.getItem("token");
      if (storedToken && !isTokenExpired(storedToken)) {
        try {
          setToken(storedToken);
          // TODO: Once the new API client is wired up globally, getCurrentUser() should automatically use it
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (err) {
          console.error("Failed to fetch user", err);
          localStorage.removeItem("token");
        }
      } else if (storedToken) {
        // Token is expired
        console.warn("Token expired, clearing session");
        localStorage.removeItem("token");
        setToken(null);
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
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  const setTenant = (tenantId: string) => {
    localStorage.setItem("tenant_id", tenantId);
    setActiveTenant(tenantId);
    // You could reload here if changing tenants requires a fresh data fetch,
    // or rely on components observing activeTenant from context.
  };

  return (
    <AuthContext.Provider value={{ user, token, activeTenant, loading, login, logout, setTenant }}>
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
