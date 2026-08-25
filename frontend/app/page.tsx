"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

/* ---------- Professional SVG icons (stroke-based, consistent style) ---------- */

function IconImport({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <path d="M12 3v10" />
      <path d="m8 9 4 4 4-4" />
      <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
    </svg>
  );
}

function IconDashboard({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="3" />
      <path d="M8 16v-5" />
      <path d="M12 16V8" />
      <path d="M16 16v-3" />
    </svg>
  );
}

function IconAI({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <rect x="5" y="7" width="14" height="12" rx="3" />
      <path d="M12 4v3" />
      <circle cx="12" cy="3" r="1" fill="currentColor" stroke="none" />
      <circle cx="9.5" cy="12.5" r="1" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="12.5" r="1" fill="currentColor" stroke="none" />
      <path d="M9.5 16h5" />
      <path d="M5 11H3" />
      <path d="M21 11h-2" />
    </svg>
  );
}

/* ---------- Scroll-reveal hook ---------- */

function useReveal<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => entry.isIntersecting && setVisible(true),
      { threshold: 0.15 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);
  return { ref, visible };
}

/* ---------- Animated feature card ---------- */

function FeatureCard({
  icon, title, body, delay,
}: {
  icon: React.ReactNode; title: string; body: string; delay: number;
}) {
  const { ref, visible } = useReveal<HTMLDivElement>();
  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={`group relative rounded-2xl border border-gray-200 bg-white p-8 shadow-sm
        transition-all duration-700 ease-out hover:-translate-y-2 hover:border-brand-200
        hover:shadow-xl hover:shadow-brand-100/60
        ${visible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"}`}
    >
      {/* gradient glow on hover */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br
        from-brand-50 via-transparent to-transparent opacity-0 transition-opacity
        duration-500 group-hover:opacity-100" />

      <div className="relative">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl
          bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-lg
          shadow-brand-200 transition-transform duration-500 group-hover:scale-110
          group-hover:rotate-3">
          {icon}
        </div>
        <h3 className="mt-5 text-lg font-semibold text-gray-900">{title}</h3>
        <p className="mt-2 leading-relaxed text-gray-600">{body}</p>
      </div>
    </div>
  );
}

export default function Landing() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-b from-brand-50 to-white">
      {/* Floating background orbs (motion graphics) */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-brand-200/40 blur-3xl animate-blob" />
        <div className="absolute top-40 -right-32 h-[28rem] w-[28rem] rounded-full bg-indigo-200/30 blur-3xl animate-blob [animation-delay:4s]" />
        <div className="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-sky-100/50 blur-3xl animate-blob [animation-delay:8s]" />
      </div>

      {/* Nav */}
      <nav className={`relative mx-auto flex max-w-6xl items-center justify-between px-6 py-5
        transition-all duration-700 ${mounted ? "translate-y-0 opacity-100" : "-translate-y-4 opacity-0"}`}>
        <span className="flex items-center gap-2 text-2xl font-bold tracking-tight text-brand-600">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-sm text-white shadow-md">B</span>
          Bizora
        </span>
        <div className="space-x-4">
          <Link href="/login" className="text-gray-700 transition-colors hover:text-brand-600">
            Log in
          </Link>
          <Link
            href="/signup"
            className="rounded-lg bg-brand-600 px-4 py-2 text-white shadow-md shadow-brand-200 transition-all hover:-translate-y-0.5 hover:bg-brand-700 hover:shadow-lg"
          >
            Get started free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative mx-auto max-w-4xl px-6 pb-20 pt-16 text-center sm:pt-24">
        <div className={`inline-flex items-center gap-2 rounded-full border border-brand-200 bg-white/70
          px-4 py-1.5 text-sm text-brand-700 shadow-sm backdrop-blur transition-all duration-700
          ${mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"}`}>
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-500" />
          </span>
          AI-powered insights for small businesses
        </div>

        <h1 className={`mt-6 bg-gradient-to-br from-gray-900 via-gray-800 to-brand-700 bg-clip-text
          text-5xl font-extrabold tracking-tight text-transparent sm:text-6xl
          transition-all delay-100 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"}`}>
          Your AI Business Manager
        </h1>

        <p className={`mx-auto mt-6 max-w-2xl text-xl leading-relaxed text-gray-600
          transition-all delay-200 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"}`}>
          Upload your sales, inventory and expense spreadsheets. Bizora cleans
          them, builds your dashboard, predicts problems before they happen,
          and answers your questions like a real manager.
        </p>

        <div className={`mt-10 flex flex-wrap justify-center gap-4 transition-all delay-300 duration-700
          ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"}`}>
          <Link href="/signup"
            className="group relative overflow-hidden rounded-xl bg-brand-600 px-8 py-4 text-lg
            font-semibold text-white shadow-xl shadow-brand-300/50 transition-all
            hover:-translate-y-0.5 hover:bg-brand-700 hover:shadow-2xl">
            <span className="relative z-10">Create your account</span>
            <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent
              via-white/25 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
          </Link>
          <Link href="/login"
            className="rounded-xl border border-gray-300 bg-white/70 px-8 py-4 text-lg font-semibold
            backdrop-blur transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:bg-white">
            I already have one
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="relative mx-auto grid max-w-5xl gap-8 px-6 pb-24 md:grid-cols-3">
        <FeatureCard
          delay={0}
          icon={<IconImport className="h-6 w-6" />}
          title="Import in minutes"
          body="Drag & drop your CSV files. We clean messy data automatically."
        />
        <FeatureCard
          delay={150}
          icon={<IconDashboard className="h-6 w-6" />}
          title="Live dashboard"
          body="Revenue, profit, inventory health and customer insights at a glance."
        />
        <FeatureCard
          delay={300}
          icon={<IconAI className="h-6 w-6" />}
          title="AI manager"
          body="Ask “Why did my profit fall?” and get real answers from your own data."
        />
      </section>
    </main>
  );
}
