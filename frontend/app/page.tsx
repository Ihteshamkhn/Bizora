"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

/* ---------- Icons (stroke-based, consistent style) ---------- */

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

/* ---------- Hooks ---------- */

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

/**
 * Mouse-driven 3D tilt. Sets --tilt-x / --tilt-y CSS vars on the element,
 * consumed by the .tilt-card class in globals.css.
 */
function useTilt<T extends HTMLElement>(max = 10) {
  const ref = useRef<T>(null);

  const onMove = useCallback(
    (e: React.MouseEvent) => {
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width - 0.5;
      const py = (e.clientY - rect.top) / rect.height - 0.5;
      el.style.setProperty("--tilt-y", `${px * max * 2}deg`);
      el.style.setProperty("--tilt-x", `${-py * max * 2}deg`);
    },
    [max]
  );

  const onLeave = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--tilt-x", "0deg");
    el.style.setProperty("--tilt-y", "0deg");
  }, []);

  return { ref, onMouseMove: onMove, onMouseLeave: onLeave };
}

/* ---------- 3D Dashboard mock — layered glass cards in perspective ---------- */

function DashboardMock() {
  const tilt = useTilt<HTMLDivElement>(8);

  return (
    <div className="scene-3d relative mx-auto w-full max-w-xl">
      {/* soft shadow "floor" */}
      <div
        aria-hidden="true"
        className="absolute inset-x-8 bottom-[-28px] h-16 rounded-[50%] bg-moss-600/20 blur-2xl"
      />

      <div
        ref={tilt.ref}
        onMouseMove={tilt.onMouseMove}
        onMouseLeave={tilt.onMouseLeave}
        className="tilt-card preserve-3d relative"
      >
        {/* Main dashboard card (depth layer 1) */}
        <div className="mock-card depth-1 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wider text-gray-400">
                Revenue · this month
              </p>
              <p className="mt-1 text-2xl font-bold text-gray-900">PKR 61,800</p>
            </div>
            <span className="rounded-full bg-moss-50 px-3 py-1 text-xs font-semibold text-moss-600 ring-1 ring-moss-200">
              ▲ +9.6%
            </span>
          </div>

          {/* mini area chart */}
          <svg viewBox="0 0 300 90" className="mt-4 h-24 w-full" aria-hidden="true">
            <defs>
              <linearGradient id="revFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2D5016" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#2D5016" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0,70 C30,62 45,40 75,44 C105,48 120,26 150,30 C180,34 200,14 230,20 C260,26 280,10 300,14 L300,90 L0,90 Z"
              fill="url(#revFill)"
            />
            <path
              d="M0,70 C30,62 45,40 75,44 C105,48 120,26 150,30 C180,34 200,14 230,20 C260,26 280,10 300,14"
              fill="none" stroke="#2D5016" strokeWidth="2.5" strokeLinecap="round"
            />
          </svg>

          <div className="mt-4 grid grid-cols-3 gap-3">
            {([
              { label: "Orders", value: "1,248" },
              { label: "Profit", value: "PKR 19.7K" },
              { label: "Margin", value: "31.9%" },
            ]).map((s) => (
              <div key={s.label} className="rounded-lg bg-cream-muted px-3 py-2">
                <p className="text-[10px] uppercase tracking-wide text-gray-400">{s.label}</p>
                <p className="text-sm font-bold text-gray-800">{s.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Floating AI insight card (depth layer 3, top-right) */}
        <div className="mock-card animate-float depth-3 absolute -right-6 -top-10 w-52 p-4 sm:-right-12">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-moss-600 text-white">
              <IconAI className="h-4 w-4" />
            </span>
            <p className="text-xs font-semibold text-gray-700">AI Manager</p>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-gray-500">
            “Reorder <span className="font-semibold text-moss-600">Running Shoes</span> — stockout in ~1 day.”
          </p>
        </div>

        {/* Floating import chip (depth layer 2, bottom-left) */}
        <div
          className="mock-card animate-float depth-2 absolute -bottom-8 -left-4 flex items-center gap-3 p-3 sm:-left-10"
          style={{ animationDelay: "1.5s" }}
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-cream-sand text-moss-600">
            <IconImport className="h-4 w-4" />
          </span>
          <div>
            <p className="text-xs font-semibold text-gray-700">CSV imported</p>
            <p className="text-[11px] text-gray-400">1,248 rows cleaned ✓</p>
          </div>
        </div>

        {/* Floating health badge (depth layer 2, mid-left) */}
        <div
          className="mock-card animate-float depth-2 absolute -left-8 top-1/3 hidden items-center gap-2 p-3 sm:flex"
          style={{ animationDelay: "3s" }}
        >
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-moss-400 opacity-70" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-moss-600" />
          </span>
          <p className="text-xs font-semibold text-gray-700">Health score <span className="text-moss-600">92/100</span></p>
        </div>
      </div>
    </div>
  );
}

/* ---------- Feature card with scroll reveal + hover 3D lift ---------- */

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
      className={`group scene-3d relative rounded-2xl border border-cream-border bg-white p-8 shadow-sm
        transition-all duration-700 ease-out hover:-translate-y-2 hover:border-moss-200
        hover:shadow-xl hover:shadow-moss-100/60
        ${visible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"}`}
    >
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br
        from-moss-50 via-transparent to-transparent opacity-0 transition-opacity
        duration-500 group-hover:opacity-100" />
      <div className="preserve-3d relative transition-transform duration-300 group-hover:[transform:rotateX(6deg)_rotateY(-6deg)]">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl
          bg-gradient-to-br from-moss-400 to-moss-600 text-white shadow-lg shadow-moss-200
          transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3">
          {icon}
        </div>
        <h3 className="mt-5 text-lg font-semibold text-gray-900">{title}</h3>
        <p className="mt-2 leading-relaxed text-gray-600">{body}</p>
      </div>
    </div>
  );
}

/* ---------- Landing page ---------- */

export default function Landing() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <main className="relative min-h-screen overflow-hidden bg-cream">
      {/* Warm ambient blobs */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="animate-blob absolute -top-24 -left-24 h-96 w-96 rounded-full bg-moss-100/60 blur-3xl" />
        <div className="animate-blob absolute top-40 -right-32 h-[28rem] w-[28rem] rounded-full bg-cream-sand/50 blur-3xl [animation-delay:4s]" />
        <div className="animate-blob absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-moss-50 blur-3xl [animation-delay:8s]" />
      </div>

      {/* Nav */}
      <nav className={`relative mx-auto flex max-w-6xl items-center justify-between px-6 py-5
        transition-all duration-700 ${mounted ? "translate-y-0 opacity-100" : "-translate-y-4 opacity-0"}`}>
        <span className="flex items-center gap-2 text-2xl font-bold tracking-tight text-moss-600">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-moss-400 to-moss-600 text-sm text-white shadow-md">B</span>
          Bizora
        </span>
        <div className="space-x-4">
          <Link href="/login" className="text-gray-700 transition-colors hover:text-moss-600">
            Log in
          </Link>
          <Link
            href="/signup"
            className="rounded-lg bg-moss-600 px-4 py-2 text-white shadow-md shadow-moss-200 transition-all hover:-translate-y-0.5 hover:bg-moss-500 hover:shadow-lg"
          >
            Get started free
          </Link>
        </div>
      </nav>

      {/* Hero — two-column with 3D mock */}
      <section className="relative mx-auto grid max-w-6xl items-center gap-14 px-6 pb-24 pt-12 lg:grid-cols-2 lg:pt-20">
        {/* Copy */}
        <div className="text-center lg:text-left">
          <div className={`inline-flex items-center gap-2 rounded-full border border-moss-200 bg-white/70
            px-4 py-1.5 text-sm text-moss-600 shadow-sm backdrop-blur transition-all delay-100 duration-700
            ${mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"}`}>
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-moss-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-moss-600" />
            </span>
            AI-powered insights for small businesses
          </div>

          <h1 className={`mt-6 text-5xl font-extrabold leading-tight tracking-tight text-gray-900 sm:text-6xl
            transition-all delay-200 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"}`}>
            Your{" "}
            <span className="bg-gradient-to-r from-moss-600 via-moss-500 to-moss-400 bg-clip-text text-transparent">
              AI Business
            </span>{" "}
            Manager
          </h1>

          <p className={`mx-auto mt-6 max-w-xl text-lg leading-relaxed text-gray-600 lg:mx-0
            transition-all delay-300 duration-700 ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"}`}>
            Upload your sales, inventory and expense spreadsheets. Bizora cleans
            them, builds your dashboard, predicts problems before they happen,
            and answers your questions like a real manager.
          </p>

          <div className={`mt-10 flex flex-wrap justify-center gap-4 transition-all delay-[400ms] duration-700
            ${mounted ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0"} lg:justify-start`}>
            <Link href="/signup"
              className="group relative overflow-hidden rounded-xl bg-moss-600 px-8 py-4 text-lg
              font-semibold text-white shadow-xl shadow-moss-300/50 transition-all
              hover:-translate-y-0.5 hover:bg-moss-500 hover:shadow-2xl">
              <span className="relative z-10">Create your account</span>
              <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent
                via-white/25 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
            </Link>
            <Link href="/login"
              className="rounded-xl border border-cream-border bg-white/70 px-8 py-4 text-lg font-semibold
              backdrop-blur transition-all hover:-translate-y-0.5 hover:border-moss-300 hover:bg-white">
              I already have one
            </Link>
          </div>

          {/* trust row */}
          <div className={`mt-10 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-gray-400
            transition-all delay-500 duration-700 ${mounted ? "opacity-100" : "opacity-0"} lg:justify-start`}>
            <span>✓ Free to start</span>
            <span>✓ No credit card</span>
            <span>✓ Your data stays yours</span>
          </div>
        </div>

        {/* 3D dashboard mock */}
        <div className={`transition-all delay-300 duration-1000 ${mounted ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`}>
          <DashboardMock />
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

      {/* Footer strip */}
      <footer className="relative border-t border-cream-border py-8 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} Bizora — Your AI Business Manager
      </footer>
    </main>
  );
}
