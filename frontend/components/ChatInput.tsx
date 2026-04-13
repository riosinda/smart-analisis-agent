'use client';

import { useState, useRef, type KeyboardEvent } from 'react';
import { SendHorizontal } from 'lucide-react';

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('');
  const ref = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue('');
    if (ref.current) ref.current.style.height = 'auto';
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  const autoResize = () => {
    const el = ref.current;
    if (el) { el.style.height = 'auto'; el.style.height = `${Math.min(el.scrollHeight, 160)}px`; }
  };

  return (
    <div className="border-t border-gray-100 bg-white px-4 py-3">
      <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-2xl border border-gray-200 bg-gray-50 px-4 py-2 transition-all focus-within:border-rappi-orange focus-within:ring-1 focus-within:ring-rappi-orange">
        <textarea
          ref={ref}
          value={value}
          rows={1}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          onInput={autoResize}
          placeholder="Preguntá sobre zonas, métricas o tendencias..."
          disabled={disabled}
          className="max-h-40 flex-1 resize-none bg-transparent py-1 text-sm text-gray-800 placeholder-gray-400 outline-none disabled:opacity-50"
        />
        <button
          onClick={submit}
          disabled={disabled || !value.trim()}
          aria-label="Enviar"
          className="mb-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-rappi-orange text-white transition-colors hover:bg-rappi-orange-dk disabled:cursor-not-allowed disabled:opacity-40"
        >
          <SendHorizontal className="h-4 w-4" />
        </button>
      </div>
      <p className="mt-1.5 text-center text-[11px] text-gray-400">
        Enter para enviar · Shift+Enter para nueva línea
      </p>
    </div>
  );
}
