"use client";

import { useAuth } from "@/components/AuthProvider";
import BulletinBoard from "@/components/BulletinBoard";
import ParentDashboard from "./parent/page";
import ChildDashboard from "./child/page";

/**
 * Main Home Page.
 * Renders the shared Bulletin Board and either the Parent or Child dashboard
 * depending on the current global mock authentication role.
 */
export default function Home() {
  const { role } = useAuth();

  return (
    <>
      <BulletinBoard />
      {role === "parent" ? <ParentDashboard /> : <ChildDashboard />}
    </>
  );
}
