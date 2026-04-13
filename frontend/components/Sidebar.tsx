'use client';

import { useState } from 'react';
import { Plus, MessageSquare, Trash2, FileDown, Loader2 } from 'lucide-react';
import { downloadReport } from '@/lib/api';
import type { Conversation } from '@/lib/types';

interface Props {
  conversations: Conversation[];
  activeId: string;
  onNew: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

function relativeTime(ts: number): string {
  const diff = Date.now() - ts;
  if (diff < 60_000)        return 'Ahora';
  if (diff < 3_600_000)     return `Hace ${Math.floor(diff / 60_000)} min`;
  const d = new Date(ts);
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return 'Hoy';
  return d.toLocaleDateString('es', { day: 'numeric', month: 'short' });
}

export function Sidebar({ conversations, activeId, onNew, onSelect, onDelete }: Props) {
  const [downloading, setDownloading] = useState(false);

  const handleReport = async () => {
    setDownloading(true);
    try { await downloadReport(); }
    catch (e) { console.error(e); }
    finally { setDownloading(false); }
  };

  return (
    <aside className="flex w-64 shrink-0 flex-col bg-[#0F0F0F] text-white">
      {/* Brand */}
      <div className="px-5 py-5">
        <span className="text-[26px] font-black leading-none tracking-tight text-rappi-orange">
          rappi
        </span>
        <p className="mt-1 text-[9px] uppercase tracking-[0.2em] text-white/30">
          Operations Assistant
        </p>
      </div>

      {/* New chat */}
      <div className="px-3 pb-2">
        <button
          onClick={onNew}
          className="flex w-full items-center gap-2 rounded-xl bg-rappi-orange px-3 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-rappi-orange-dk"
        >
          <Plus className="h-4 w-4" />
          Nueva conversación
        </button>
      </div>

      <div className="mx-3 my-2 h-px bg-white/10" />

      {/* Conversations */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-1">
        <p className="mb-1 px-2 text-[9px] uppercase tracking-[0.18em] text-white/25">
          Conversaciones
        </p>

        {conversations.map((conv) => {
          const isActive = conv.id === activeId;
          return (
            <div
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`group flex cursor-pointer items-start gap-2 rounded-xl px-3 py-2.5 transition-colors ${
                isActive
                  ? 'bg-rappi-orange/20 text-white'
                  : 'text-white/55 hover:bg-white/5 hover:text-white'
              }`}
            >
              <MessageSquare className="mt-0.5 h-4 w-4 shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium">{conv.title}</p>
                <p className="mt-0.5 text-[10px] text-white/25">{relativeTime(conv.createdAt)}</p>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                aria-label="Eliminar"
                className="mt-0.5 shrink-0 rounded p-0.5 opacity-0 transition-all group-hover:opacity-100 hover:text-red-400"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          );
        })}
      </nav>

      <div className="mx-3 my-2 h-px bg-white/10" />

      {/* Report button */}
      <div className="px-3 pb-4">
        <button
          onClick={handleReport}
          disabled={downloading}
          className="flex w-full items-center gap-2 rounded-xl bg-white/8 px-3 py-2.5 text-sm font-medium text-white/80 transition-colors hover:bg-white/12 hover:text-white disabled:opacity-50"
        >
          {downloading
            ? <Loader2 className="h-4 w-4 animate-spin" />
            : <FileDown className="h-4 w-4" />
          }
          {downloading ? 'Generando...' : 'Generar Reporte PDF'}
        </button>
      </div>
    </aside>
  );
}
