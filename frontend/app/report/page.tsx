'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowLeft, Printer, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import type { ReportData, ReportRow } from '@/lib/types';
import { fetchReport } from '@/lib/api';
import { ChartRenderer } from '@/components/ChartRenderer';

// ---------------------------------------------------------------------------
// Chart builder — horizontal bar
// ---------------------------------------------------------------------------
function buildHorizontalBar(
  rows: ReportRow[],
  labelKeys: string[],         // columns to join for the y-axis label
  valueKey: string,            // numeric column to plot
  title: string,
  xLabel: string,
): string {
  const labels = rows.map(r =>
    labelKeys.map(k => String(r[k]).substring(0, 22)).join(' · '),
  );
  const values = rows.map(r => Number(r[valueKey]));
  const colors = values.map(v => (v < 0 ? '#e74c3c' : '#FF441B'));

  return JSON.stringify({
    data: [{
      type: 'bar',
      orientation: 'h',
      x: values,
      y: labels,
      marker: { color: colors },
      text: values.map(v => v.toFixed(1)),
      textposition: 'outside',
      cliponaxis: false,
    }],
    layout: {
      title: { text: title, font: { size: 13, color: '#111827' } },
      xaxis: { title: { text: xLabel }, zeroline: true, zerolinecolor: '#d1d5db' },
      yaxis: { automargin: true, tickfont: { size: 10 } },
      margin: { l: 180, r: 60, t: 48, b: 40 },
      height: Math.max(220, rows.length * 32 + 80),
    },
  });
}

function buildCorrelationBar(rows: ReportRow[]): string {
  const labels = rows.map(r =>
    `${String(r['metric_a']).substring(0, 18)} / ${String(r['metric_b']).substring(0, 18)}`,
  );
  const values = rows.map(r => Number(r['correlation']));
  const colors = values.map(v => (v > 0 ? '#FF441B' : '#e74c3c'));

  return JSON.stringify({
    data: [{
      type: 'bar',
      orientation: 'h',
      x: values,
      y: labels,
      marker: { color: colors },
      text: values.map(v => v.toFixed(3)),
      textposition: 'outside',
      cliponaxis: false,
    }],
    layout: {
      title: { text: 'Correlaciones Spearman entre Métricas', font: { size: 13, color: '#111827' } },
      xaxis: {
        title: { text: 'Correlación (r)' },
        range: [-1.1, 1.1],
        zeroline: true,
        zerolinecolor: '#d1d5db',
      },
      yaxis: { automargin: true, tickfont: { size: 10 } },
      margin: { l: 220, r: 60, t: 48, b: 40 },
      height: Math.max(220, rows.length * 32 + 80),
    },
  });
}

// ---------------------------------------------------------------------------
// Section: chart + table
// ---------------------------------------------------------------------------
interface SectionProps {
  title: string;
  rows: ReportRow[];
  chartJson?: string;
}

function DataSection({ title, rows, chartJson }: SectionProps) {
  if (!rows.length) return null;

  const headers = Object.keys(rows[0]);

  const fmt = (v: string | number) => {
    if (typeof v === 'number') return v.toLocaleString('es', { maximumFractionDigits: 3 });
    return v === '' ? '—' : v;
  };

  const getValueClass = (key: string, val: string | number): string => {
    if (typeof val !== 'number') return '';
    if (key === 'cambio_pct' || key === 'decline_total_pct')
      return val < 0 ? 'text-red-600 font-semibold' : 'text-emerald-600 font-semibold';
    if (key === 'z_score') return 'text-red-600 font-semibold';
    if (key === 'correlation')
      return val > 0 ? 'text-emerald-600 font-semibold' : 'text-red-600 font-semibold';
    return '';
  };

  return (
    <section className="mb-12 print:break-before-page">
      <h3 className="mb-4 text-sm font-bold uppercase tracking-wide text-gray-500">{title}</h3>

      {/* Chart */}
      {chartJson && (
        <div className="mb-5">
          <ChartRenderer chartJson={chartJson} />
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="bg-[#0F0F0F]">
              {headers.map((h) => (
                <th
                  key={h}
                  className="whitespace-nowrap px-3 py-2.5 text-left text-[10px] font-semibold uppercase tracking-wider text-white/70"
                >
                  {h.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50/60'}>
                {headers.map((h) => (
                  <td
                    key={h}
                    className={`whitespace-nowrap px-3 py-2 text-gray-700 ${getValueClass(h, row[h])}`}
                  >
                    {fmt(row[h])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Loading skeleton
// ---------------------------------------------------------------------------
function Skeleton() {
  return (
    <div className="mx-auto max-w-4xl space-y-6 px-8 pt-28 pb-12">
      <div className="flex items-center gap-3 text-gray-500">
        <Loader2 className="h-5 w-5 animate-spin text-rappi-orange" />
        <span className="text-sm">Generando reporte — puede tardar unos segundos…</span>
      </div>
      {[140, 80, 200, 260, 160, 260, 120].map((h, i) => (
        <div key={i} className="animate-pulse rounded-lg bg-gray-100" style={{ height: h }} />
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------
function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="mx-auto mt-32 max-w-md rounded-2xl border border-red-100 bg-red-50 p-8 text-center">
      <AlertCircle className="mx-auto mb-4 h-10 w-10 text-red-400" />
      <p className="mb-1 font-semibold text-red-700">Error al generar el reporte</p>
      <p className="mb-6 text-sm text-red-500">{error}</p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 rounded-xl bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
      >
        <RefreshCw className="h-4 w-4" />
        Reintentar
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function ReportPage() {
  const router = useRouter();
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchReport());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const generatedAt = data
    ? new Date(data.generated_at).toLocaleString('es', {
        day: '2-digit', month: 'long', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })
    : '';

  return (
    <div className="min-h-screen bg-gray-50">

      {/* ── Top bar (hidden on print) ── */}
      <header className="print:hidden fixed inset-x-0 top-0 z-20 flex items-center justify-between border-b border-gray-200 bg-white/90 px-6 py-3 backdrop-blur-sm">
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver al chat
        </button>

        <span className="text-lg font-black text-rappi-orange">rappi</span>

        <button
          onClick={() => window.print()}
          disabled={!data}
          className="flex items-center gap-2 rounded-xl bg-rappi-orange px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-rappi-orange-dk disabled:opacity-40"
        >
          <Printer className="h-4 w-4" />
          Imprimir / PDF
        </button>
      </header>

      {/* ── States ── */}
      {loading && <Skeleton />}
      {!loading && error && <ErrorState error={error} onRetry={load} />}

      {/* ── Report content ── */}
      {!loading && data && (
        <main className="mx-auto max-w-4xl px-8 pt-24 pb-16 print:max-w-none print:px-12 print:pt-0">

          {/* Print-only header */}
          <div className="mb-8 hidden border-b-2 border-rappi-orange pb-5 print:flex print:items-end print:justify-between">
            <div>
              <span className="text-3xl font-black text-rappi-orange">rappi</span>
              <p className="mt-0.5 text-xs uppercase tracking-widest text-gray-400">
                Operations Intelligence
              </p>
            </div>
            <p className="text-xs text-gray-400">{generatedAt}</p>
          </div>

          {/* Screen date */}
          <p className="print:hidden mb-6 text-xs text-gray-400">{generatedAt}</p>

          {/* Narrative */}
          <article className="prose prose-sm max-w-none
            prose-headings:font-bold
            prose-h1:text-2xl prose-h1:text-[#FF441B] prose-h1:border-b prose-h1:border-[#FF441B]/20 prose-h1:pb-2
            prose-h2:text-base prose-h2:text-gray-800 prose-h2:border-l-4 prose-h2:border-[#FF441B] prose-h2:pl-3
            prose-h3:text-sm prose-h3:text-gray-700
            prose-li:my-0.5
            prose-strong:text-gray-900
            print:prose-h1:text-xl print:prose-h2:text-sm
          ">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.narrative}</ReactMarkdown>
          </article>

          {/* Divider */}
          <div className="my-10 flex items-center gap-4">
            <div className="h-px flex-1 bg-gray-200" />
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
              Anexo — Datos del Análisis
            </span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>

          {/* Anomalías */}
          <DataSection
            title="Anomalías WoW (cambio > 10%)"
            rows={data.anomalies}
            chartJson={data.anomalies.length ? buildHorizontalBar(
              data.anomalies, ['ZONE', 'METRIC'], 'cambio_pct',
              'Cambio semana a semana (%)', 'Cambio %',
            ) : undefined}
          />

          {/* Tendencias */}
          <DataSection
            title="Tendencias Decrecientes (3+ semanas consecutivas)"
            rows={data.trends}
            chartJson={data.trends.length ? buildHorizontalBar(
              data.trends, ['ZONE', 'METRIC'], 'decline_total_pct',
              'Deterioro acumulado 3 semanas (%)', 'Deterioro %',
            ) : undefined}
          />

          {/* Benchmarking */}
          <DataSection
            title="Benchmarking — Zonas Rezagadas (z-score < −2)"
            rows={data.benchmarking}
            chartJson={data.benchmarking.length ? buildHorizontalBar(
              data.benchmarking, ['ZONE', 'METRIC'], 'z_score',
              'Z-score vs Peer Group', 'Z-score',
            ) : undefined}
          />

          {/* Correlaciones */}
          <DataSection
            title="Correlaciones entre Métricas (|r| > 0.5)"
            rows={data.correlations}
            chartJson={data.correlations.length ? buildCorrelationBar(data.correlations) : undefined}
          />
        </main>
      )}

      {/* Print styles */}
      <style>{`
        @media print {
          body { background: white; }
          @page { margin: 1.5cm; size: A4 landscape; }
        }
      `}</style>
    </div>
  );
}
