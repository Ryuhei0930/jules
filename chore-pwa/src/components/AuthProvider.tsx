"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

export type Role = "parent" | "child";

interface AuthContextType {
  role: Role;
  setRole: (role: Role) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Provider component that holds the global mock authentication state (role).
 * It allows switching between 'parent' and 'child' views.
 */
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [role, setRole] = useState<Role>("parent"); // Default role

  return (
    <AuthContext.Provider value={{ role, setRole }}>
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
