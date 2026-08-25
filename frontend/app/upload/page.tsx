"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

const FILE_TYPES = [
  { key: "sales", label: "📊 Sales", hint: "Orders with product, quantity, price, date" },
  { key: "inventory", label: "📦 Inventory", hint: "Products with stock levels" },
  { key: "customers", label: "👥 Customers", hint: "Customer names and contact info" },
  { key: "expenses", label: "💰 Expenses", hint: "Business costs by category and date" },
] as const;

interface PreviewReport {
  report: {
    total_rows: number; valid_rows: number; duplicates_removed: number;
    warnings: string[]; errors: string[]; summary: string;
  };
  sample: Record<string, string>[];
}

export default function UploadPage() {
  const [fileType, setFileType] = useState<string>("sales");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewReport | null>(null);
  const [result, setResult] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setPreview(null); setResult(""); setError(""); setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  }, [fileType]);

  async function handleFile(f: File | null) {
    if (!f) return;
    setFile(f); setPreview(null); setResult(""); setError("");
    setBusy(true);
    try {
      const businesses = await api.listBusinesses();
      const biz = businesses[0];
      if (!biz) throw new Error("Create a business first (visit the dashboard).");
      setPreview(await api.previewUpload(biz.id, fileType, f));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function confirmImport() {
    if (!file) return;
    setBusy(true); setError("");
    try {
      const businesses = await api.listBusinesses();
      const biz = businesses[0];
      if (!biz) throw new Error("No business found.");
      const res = await api.confirmImport(biz.id, fileType, file);
      setResult(res.message);
      setPreview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/dashboard" className="text-sm text-brand-600">← Back to dashboard</Link>
      <h1 className="mt-4 text-2xl font-bold">Import Data</h1>
      <p className="mt-1 text-gray-500">
        Upload your spreadsheets. We check them for problems automatically.
      </p>

      {/* Type selector */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {FILE_TYPES.map((t) => (
          <button
            key={t.key} onClick={() => setFileType(t.key)}
            className={`rounded-xl border p-4 text-left text-sm transition ${
              fileType === t.key
                ? "border-brand-500 bg-brand-50 font-semibold"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
          >
            <div>{t.label}</div>
            <div className="mt-1 text-xs text-gray-400">{t.hint}</div>
          </button>
        ))}
      </div>

      {/* Drop zone */}
      {!preview && !result && (
        <label
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
          className="mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-300 bg-white p-14 text-center hover:border-brand-500"
        >
          <span className="text-4xl">📁</span>
          <p className="mt-3 font-medium">Drag & drop your CSV here</p>
          <p className="text-sm text-gray-400">or click to choose a file</p>
          <input
            ref={inputRef} type="file" accept=".csv" className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
          />
        </label>
      )}

      {busy && <p className="mt-6 text-gray-500">Processing your file…</p>}
      {error && (
        <p className="mt-6 rounded-lg bg-red-50 px-4 py-3 text-red-600">{error}</p>
      )}

      {/* Preview / validation report */}
      {preview && (
        <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Validation Report</h2>
          <ul className="mt-3 space-y-1 text-sm">
            <li>✓ {preview.report.total_rows.toLocaleString()} rows detected</li>
            <li>✓ {preview.report.valid_rows.toLocaleString()} valid records</li>
            {preview.report.duplicates_removed > 0 && (
              <li>⚠ {preview.report.duplicates_removed} duplicates will be removed</li>
            )}
            {preview.report.warnings.map((w, i) => (
              <li key={i}>⚠ {w}</li>
            ))}
          </ul>

          {preview.sample.length > 0 && (
            <>
              <h3 className="mt-5 text-sm font-semibold">First rows preview</h3>
              <div className="mt-2 overflow-x-auto">
                <table className="min-w-full text-xs">
                  <thead>
                    <tr className="bg-gray-50">
                      {Object.keys(preview.sample[0]).map((c) => (
                        <th key={c} className="px-2 py-1 text-left font-medium">{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.sample.map((row, i) => (
                      <tr key={i} className="border-t border-gray-100">
                        {Object.values(row).map((v, j) => (
                          <td key={j} className="px-2 py-1">{v}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          <div className="mt-6 flex gap-3">
            <button
              onClick={confirmImport} disabled={busy}
              className="rounded-lg bg-brand-600 px-5 py-2.5 font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
            >
              Import Data
            </button>
            <button
              onClick={() => { setPreview(null); setFile(null); }}
              className="rounded-lg border border-gray-300 px-5 py-2.5 font-semibold hover:bg-gray-100"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="mt-6 rounded-2xl border border-green-200 bg-green-50 p-6">
          <p className="font-semibold text-green-700">✓ Import complete</p>
          <p className="mt-1 text-sm text-green-800">{result}</p>
          <Link href="/dashboard" className="mt-4 inline-block rounded-lg bg-brand-600 px-5 py-2.5 font-semibold text-white hover:bg-brand-700">
            Go to dashboard →
          </Link>
        </div>
      )}
    </main>
  );
}
