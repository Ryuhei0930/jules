"use client";

import { useState } from "react";
import { supabase } from "@/utils/supabase/client";

/**
 * Authentication form handling both login and signup.
 */
export default function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<"parent" | "child">("child");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  /**
   * Handles form submission for login and registration.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    try {
      if (isLogin) {
        // Handle Login
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
      } else {
        // Handle Signup
        const { data, error: signUpError } = await supabase.auth.signUp({
          email,
          password,
        });

        if (signUpError) throw signUpError;

        // Create profile in the custom public.users table
        if (data.user) {
          const { error: profileError } = await supabase.from("users").insert([
            {
              id: data.user.id,
              name: name,
              role: role,
            },
          ]);
          if (profileError) throw profileError;
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg("An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-4">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 w-full max-w-sm">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
          {isLogin ? "ログイン" : "新規登録"}
        </h2>

        {errorMsg && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 text-center">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {!isLogin && (
            <>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-bold text-gray-600">お名前</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm font-bold text-gray-600">役割</label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setRole("parent")}
                    className={`flex-1 py-2 rounded-lg text-sm font-bold transition-colors ${
                      role === "parent"
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    親 (Parent)
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole("child")}
                    className={`flex-1 py-2 rounded-lg text-sm font-bold transition-colors ${
                      role === "child"
                        ? "bg-green-500 text-white"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    子供 (Child)
                  </button>
                </div>
              </div>
            </>
          )}

          <div className="flex flex-col gap-1">
            <label className="text-sm font-bold text-gray-600">メールアドレス</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-bold text-gray-600">パスワード</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-4 bg-gray-900 hover:bg-gray-800 text-white font-bold py-3 rounded-xl transition-colors disabled:bg-gray-400"
          >
            {loading ? "処理中..." : isLogin ? "ログインする" : "登録する"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setErrorMsg(null);
            }}
            className="text-sm text-blue-500 hover:underline font-medium"
          >
            {isLogin
              ? "アカウントをお持ちでない方はこちら"
              : "すでにアカウントをお持ちの方はこちら"}
          </button>
        </div>
      </div>
    </div>
  );
}
