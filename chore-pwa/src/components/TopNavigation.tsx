"use client";

import { useAuth } from "./AuthProvider";
import { supabase } from "@/utils/supabase/client";
import { LogOut, User } from "lucide-react";

/**
 * TopNavigation displays the current user's profile info and a logout button.
 */
export default function TopNavigation() {
  const { role, userName } = useAuth();

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="flex justify-between items-center p-4 bg-gray-100 shadow-sm rounded-b-xl mb-4">
      <div className="flex items-center gap-2">
        <div className={`p-2 rounded-full ${role === 'parent' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'}`}>
          <User className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-bold text-gray-800">{userName || "User"}</span>
          <span className="text-xs text-gray-500 font-medium uppercase">{role === "parent" ? "親ビュー" : "子供ビュー"}</span>
        </div>
      </div>

      <button
        onClick={handleLogout}
        className="flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-red-500 transition-colors bg-white px-3 py-1.5 rounded-lg shadow-sm border border-gray-200"
      >
        <LogOut className="w-4 h-4" />
        ログアウト
      </button>
    </div>
  );
}
