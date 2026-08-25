"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";

export default function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res =
        mode === "signup"
          ? await api.signup(email, password)
          : await api.login(email, password);
      localStorage.setItem("bizora_token", res.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <form
        onSubmit={submit}
        className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-md"
      >
        <h1 className="text-2xl font-bold">
          {mode === "signup" ? "Create your account" : "Welcome back"}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {mode === "signup"
            ? "Start managing your business with AI."
            : "Log in to your Bizora dashboard."}
        </p>

        <label className="mt-6 block text-sm font-medium">Email</label>
        <input
          type="email" required value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
        />

        <label className="mt-4 block text-sm font-medium">Password</label>
        <input
          type="password" required minLength={8} value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
        />
        {mode === "signup" && (
          <p className="mt-1 text-xs text-gray-400">At least 8 characters.</p>
        )}

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        <button
          type="submit" disabled={loading}
          className="mt-6 w-full rounded-lg bg-brand-600 py-3 font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Please wait…" : mode === "signup" ? "Sign up" : "Log in"}
        </button>

        <p className="mt-4 text-center text-sm text-gray-600">
          {mode === "signup" ? (
            <>Already have an account? <Link href="/login" className="text-brand-600">Log in</Link></>
          ) : (
            <>New to Bizora? <Link href="/signup" className="text-brand-600">Create an account</Link></>
          )}
        </p>
      </form>
    </main>
  );
}
