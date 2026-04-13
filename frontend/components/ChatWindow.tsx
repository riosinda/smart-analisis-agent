'use client';

import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import type { Message } from '@/lib/types';

const SUGGESTIONS = [
  '¿Cuáles son las 5 zonas con mayor % Lead Penetration esta semana?',
  'Compara el Perfect Order entre zonas Wealthy y Non Wealthy en México',
  'Muestra la evolución de Gross Profit UE en Chapinero últimas 8 semanas',
  '¿Cuál es el promedio de Lead Penetration por país?',
  '¿Qué zonas tienen alto Lead Penetration pero bajo Perfect Order?',
  '¿Cuáles son las zonas que más crecen en las últimas 5 semanas y qué podría explicar el crecimiento?',
];

function TypingIndicator() {
  return (
    <div className="mb-5 flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-rappi-orange shadow-sm">
        <span className="text-xs font-black text-white">R</span>
      </div>
      <div className="rounded-2xl rounded-tl-sm border border-gray-100 bg-white px-4 py-3.5 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-gray-300 animate-bounce [animation-delay:-0.3s]" />
          <span className="h-2 w-2 rounded-full bg-gray-300 animate-bounce [animation-delay:-0.15s]" />
          <span className="h-2 w-2 rounded-full bg-gray-300 animate-bounce" />
        </div>
      </div>
    </div>
  );
}

function EmptyState({ onSend }: { onSend: (text: string) => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-6 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-rappi-orange shadow-lg">
        <span className="text-2xl font-black text-white">R</span>
      </div>
      <h2 className="text-xl font-semibold text-gray-800">Operations Assistant</h2>
      <p className="mt-2 max-w-xs text-sm text-gray-500">
        Consultá zonas, métricas operacionales, tendencias y comparaciones entre segmentos.
      </p>

      <div className="mt-7 grid w-full max-w-md gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSend(s)}
            className="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-left text-sm text-gray-600 shadow-sm transition-colors hover:border-rappi-orange hover:bg-rappi-orange-bg hover:text-rappi-orange"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

interface Props {
  messages: Message[];
  loading: boolean;
  onSend: (text: string) => void;
}

export function ChatWindow({ messages, loading, onSend }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto max-w-3xl">
        {messages.length === 0 && !loading ? (
          <EmptyState onSend={onSend} />
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {loading && <TypingIndicator />}
          </>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
