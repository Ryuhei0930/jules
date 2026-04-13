"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { supabase } from "@/utils/supabase/client";
import { Session } from "@supabase/supabase-js";

export type Role = "parent" | "child" | null;

interface AuthContextType {
  session: Session | null;
  role: Role;
  userId: string | null;
  userName: string | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Provider component that listens to Supabase auth state changes,
 * fetches the corresponding user profile, and provides auth context globally.
 */
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [role, setRole] = useState<Role>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initial fetch of session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        fetchProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    // Listen to auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session?.user) {
        fetchProfile(session.user.id);
      } else {
        setRole(null);
        setUserId(null);
        setUserName(null);
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  /**
   * Fetches the user profile from the custom `public.users` table.
   */
  const fetchProfile = async (id: string) => {
    try {
      const { data, error } = await supabase
        .from("users")
        .select("role, name")
        .eq("id", id)
        .single();

      if (!error && data) {
        setRole(data.role as Role);
        setUserName(data.name);
        setUserId(id);
      }
    } catch (err) {
      console.error("Error fetching user profile:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ session, role, userId, userName, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom hook to safely use the AuthContext.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
