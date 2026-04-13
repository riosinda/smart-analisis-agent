'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Download } from 'lucide-react';
import type { Components } from 'react-markdown';
import { ChartRenderer } from './ChartRenderer';
import { tableToCSV, detectChartType, buildFigure } from '@/lib/chartUtils';
import type { TableData } from '@/lib/chartUtils';
import type { Message } from '@/lib/types';

// ---------------------------------------------------------------------------
// Extract plain text from a ReactMarkdown node tree
// ---------------------------------------------------------------------------
function extractText(node: React.ReactNode): string {
  if (typeof node === 'string') return node;
  if (typeof node === 'number') return String(node);
  if (!node) return '';
  if (Array.isArray(node)) return node.map(extractText).join('');
  if (React.isValidElement(node)) {
    const { children } = node.props as { children?: React.ReactNode };
    return extractText(children);
  }
  return '';
}

// ---------------------------------------------------------------------------
// Extract structured { headers, rows } from the children ReactMarkdown
// passes into the <table> override.
// ReactMarkdown renders:  <table><thead><tr><th/></tr></thead><tbody>…</tbody></table>
// ---------------------------------------------------------------------------
function extractTableData(children: React.ReactNode): TableData {
  const sections: string[][][] = [];

  React.Children.forEach(children, (section) => {
    if (!React.isValidElement(section)) return;
    const sectionRows: string[][] = [];
    const { children: rowNodes } = section.props as { children?: React.ReactNode };

    React.Children.forEach(rowNodes, (row) => {
      if (!React.isValidElement(row)) return;
      const { children: cellNodes } = row.props as { children?: React.ReactNode };
      const cells: string[] = [];

      React.Children.forEach(cellNodes, (cell) => {
        if (!React.isValidElement(cell)) return;
        const { children: content } = cell.props as { children?: React.ReactNode };
        cells.push(extractText(content).trim());
      });

      if (cells.length > 0) sectionRows.push(cells);
    });

    if (sectionRows.length > 0) sections.push(sectionRows);
  });

  // sections[0] = thead rows, sections[1] = tbody rows
  return {
    headers: sections[0]?.[0] ?? [],
    rows:    sections[1]       ?? [],
  };
}

// ---------------------------------------------------------------------------
// Trigger a CSV file download in the browser
// ---------------------------------------------------------------------------
function triggerCSVDownload(csv: string) {
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = 'rappi_datos.csv';
  a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
interface Props { message: Message }

export function MessageBubble({ message }: Props) {
  if (message.role === 'user') {
    return (
      <div className="mb-5 flex justify-end">
        <div className="max-w-[72%] rounded-2xl rounded-tr-sm bg-rappi-orange px-4 py-3 text-white shadow-sm">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  // Override the <table> element: extract data from the React child tree,
  // generate CSV + auto-chart from it.
  const components: Components = {
    table({ children }) {
      const data      = extractTableData(children);
      const csv       = data.headers.length > 0 ? tableToCSV(data) : null;
      const chartType = detectChartType(data);
      const figure    = chartType ? buildFigure(data, chartType) : null;

      return (
        <div className="my-3">
          {/* Table + CSV download button */}
          <div className="group/table relative">
            {csv && (
              <button
                onClick={() => triggerCSVDownload(csv)}
                title="Descargar como CSV"
                className="absolute -top-1 right-0 z-10 flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-[11px] font-medium text-gray-400 opacity-0 shadow-sm transition-all group-hover/table:opacity-100 hover:border-rappi-orange hover:text-rappi-orange"
              >
                <Download className="h-3 w-3" />
                CSV
              </button>
            )}
            <table>{children}</table>
          </div>

          {/* Auto-generated chart below the table */}
          {figure && (
            <ChartRenderer chartJson={JSON.stringify(figure)} />
          )}
        </div>
      );
    },
  };

  return (
    <div className="mb-5 flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-rappi-orange shadow-sm">
        <span className="text-xs font-black text-white">R</span>
      </div>

      <div className="max-w-[80%] rounded-2xl rounded-tl-sm border border-gray-100 bg-white px-4 py-3 shadow-sm">
        <div className="prose prose-sm">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Charts sent explicitly by the agent (plot_zone_trend tool) */}
        {message.charts.map((chart, i) => (
          <ChartRenderer key={i} chartJson={chart} />
        ))}
      </div>
    </div>
  );
}
