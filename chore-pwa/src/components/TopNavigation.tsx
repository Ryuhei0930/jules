"use client";

import { useAuth } from "./AuthProvider";

/**
 * TopNavigation renders a simple toggle at the top of the screen
 * allowing users to easily switch between Parent and Child views.
 */
export default function TopNavigation() {
  const { role, setRole } = useAuth();

  return (
    <div className="flex justify-center items-center p-4 bg-gray-100 shadow-sm rounded-b-xl mb-4">
      <div className="bg-white rounded-full p-1 shadow-inner flex gap-1 w-full max-w-xs">
        <button
          onClick={() => setRole("parent")}
          className={`flex-1 py-2 px-4 rounded-full text-sm font-semibold transition-colors ${
            role === "parent"
              ? "bg-blue-500 text-white shadow-md"
              : "bg-transparent text-gray-600 hover:bg-gray-50"
          }`}
        >
          親ビュー
        </button>
        <button
          onClick={() => setRole("child")}
          className={`flex-1 py-2 px-4 rounded-full text-sm font-semibold transition-colors ${
            role === "child"
              ? "bg-green-500 text-white shadow-md"
              : "bg-transparent text-gray-600 hover:bg-gray-50"
          }`}
        >
          子供ビュー
        </button>
      </div>
    </div>
  );
}
