"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  tools?: string[];
}

const SUGGESTIONS = [
  "What are my best-selling products?",
  "Which products should I restock?",
  "Why did my profit change this month?",
  "Where am I losing money?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [businessId, setBusinessId] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.listBusinesses().then((b) => b[0] && setBusinessId(b[0].id)).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(question: string) {
    if (!question.trim() || busy || !businessId) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: question }]);
    setBusy(true);
    try {
      const history = messages.map(({ role, content }) => ({ role, content }));
      const res = await api.chat(businessId, question, history);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, tools: res.tools_used },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: err instanceof Error ? err.message : "Something went wrong.",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex h-screen max-w-3xl flex-col px-4">
      <header className="flex items-center justify-between py-4">
        <div>
          <h1 className="text-xl font-bold">🤖 AI Business Manager</h1>
          <p className="text-xs text-gray-500">Answers come from your own business data.</p>
        </div>
        <Link href="/dashboard" className="text-sm text-brand-600">← Dashboard</Link>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-gray-200 bg-white p-6">
        {messages.length === 0 && (
          <div className="mt-10 text-center">
            <p className="text-gray-500">Ask me anything about your business.</p>
            <div className="mt-6 grid gap-2 sm:grid-cols-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s} onClick={() => send(s)}
                  className="rounded-xl border border-gray-200 px-4 py-3 text-sm text-left hover:border-brand-500 hover:bg-brand-50"
                >
                  “{s}”
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
              m.role === "user"
                ? "ml-auto bg-brand-600 text-white"
                : "bg-gray-100 text-gray-900"
            }`}
          >
            <p className="whitespace-pre-wrap">{m.content}</p>
            {m.tools && m.tools.length > 0 && (
              <p className="mt-2 text-xs text-gray-400">
                Checked: {m.tools.join(", ")}
              </p>
            )}
          </div>
        ))}

        {busy && (
          <div className="max-w-[85%] rounded-2xl bg-gray-100 px-4 py-3 text-sm text-gray-400">
            Checking your business data…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); send(input); }}
        className="my-4 flex gap-3"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. Why did my profit decrease this month?"
          className="flex-1 rounded-xl border border-gray-300 px-4 py-3 focus:border-brand-500 focus:outline-none"
        />
        <button
          type="submit" disabled={busy || !businessId}
          className="rounded-xl bg-brand-600 px-6 font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </main>
  );
}
