'use client';

import { useRef } from 'react';
import dynamic from 'next/dynamic';
import type { ComponentType } from 'react';
import type { PlotParams } from 'react-plotly.js';
import { Download } from 'lucide-react';

const Plot = dynamic<PlotParams>(
  () => import('react-plotly.js').then((mod) => mod.default as ComponentType<PlotParams>),
  {
    ssr: false,
    loading: () => <div className="mt-3 h-64 rounded-xl bg-gray-50 animate-pulse" />,
  },
);

interface Props {
  chartJson: string;
}

export function ChartRenderer({ chartJson }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let fig: { data: any[]; layout: any };
  try {
    fig = JSON.parse(chartJson);
  } catch {
    return <p className="mt-2 text-xs text-red-400">Error al renderizar el gráfico.</p>;
  }

  const handleDownload = () => {
    const container = containerRef.current;
    if (!container) return;

    // Plotly renders a <svg class="main-svg"> inside the container div
    const svg = container.querySelector<SVGSVGElement>('.main-svg');
    if (!svg) return;

    const { width, height } = svg.getBoundingClientRect();
    const scale = 2;
    const svgStr = new XMLSerializer().serializeToString(svg);
    const blobUrl = URL.createObjectURL(
      new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' }),
    );

    const img = new Image();

    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width  = width  * scale;
      canvas.height = height * scale;
      const ctx = canvas.getContext('2d')!;
      ctx.scale(scale, scale);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(blobUrl);

      const a = document.createElement('a');
      a.href     = canvas.toDataURL('image/png');
      a.download = 'rappi_grafico.png';
      a.click();
    };

    // Fallback: download raw SVG if canvas conversion fails
    img.onerror = () => {
      URL.revokeObjectURL(blobUrl);
      const svgUrl = URL.createObjectURL(
        new Blob([svgStr], { type: 'image/svg+xml' }),
      );
      const a = document.createElement('a');
      a.href     = svgUrl;
      a.download = 'rappi_grafico.svg';
      a.click();
      URL.revokeObjectURL(svgUrl);
    };

    img.src = blobUrl;
  };

  return (
    <div
      ref={containerRef}
      className="group/chart relative mt-3 overflow-hidden rounded-xl border border-gray-100 bg-white"
    >
      <button
        onClick={handleDownload}
        title="Descargar como PNG"
        className="absolute right-2 top-2 z-10 flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-[11px] font-medium text-gray-400 opacity-0 shadow-sm transition-all group-hover/chart:opacity-100 hover:border-rappi-orange hover:text-rappi-orange"
      >
        <Download className="h-3 w-3" />
        PNG
      </button>

      <Plot
        data={fig.data}
        layout={{
          ...fig.layout,
          paper_bgcolor: '#ffffff',
          plot_bgcolor: '#ffffff',
          autosize: true,
          margin: { l: 48, r: 24, t: 48, b: 48 },
          font: { family: 'Inter, sans-serif', size: 12, color: '#374151' },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
        useResizeHandler
      />
    </div>
  );
}
