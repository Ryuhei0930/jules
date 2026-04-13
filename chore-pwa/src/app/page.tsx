"use client";

import { useAuth } from "@/components/AuthProvider";
import BulletinBoard from "@/components/BulletinBoard";
import ParentDashboard from "./parent/page";
import ChildDashboard from "./child/page";
import AuthForm from "@/components/auth/AuthForm";

/**
 * Main Home Page.
 * Routes to AuthForm if not authenticated.
 * Otherwise, renders the shared Bulletin Board and either the Parent or Child dashboard
 * depending on the user's role.
 */
export default function Home() {
  const { session, role, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <p className="text-gray-500 font-bold animate-pulse">読み込み中...</p>
      </div>
    );
  }

  if (!session) {
    return <AuthForm />;
  }

  return (
    <>
      <BulletinBoard />
      {role === "parent" ? <ParentDashboard /> : role === "child" ? <ChildDashboard /> : <p>Unknown Role</p>}
    </>
  );
}
