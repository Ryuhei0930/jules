"use client";

import { useAuth } from "./AuthProvider";
import TopNavigation from "./TopNavigation";

/**
 * Wrapper component to conditionally render the TopNavigation
 * only when a user session is active.
 */
export default function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white shadow-xl overflow-hidden pb-10">
      {session && <TopNavigation />}
      <main className="px-4">{children}</main>
    </div>
  );
}
