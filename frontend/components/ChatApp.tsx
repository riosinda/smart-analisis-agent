'use client';

import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Sidebar } from './Sidebar';
import { ChatWindow } from './ChatWindow';
import { ChatInput } from './ChatInput';
import { sendMessage } from '@/lib/api';
import type { Conversation, Message } from '@/lib/types';

const STORAGE_KEY = 'rappi_conversations';

function newConversation(): Conversation {
  return { id: uuidv4(), title: 'Nueva conversación', messages: [], createdAt: Date.now() };
}

export function ChatApp() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId]           = useState<string>('');
  const [loading, setLoading]             = useState(false);
  const [ready, setReady]                 = useState(false);

  // Hydrate from localStorage only on the client
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: Conversation[] = JSON.parse(stored);
        if (parsed.length > 0) {
          setConversations(parsed);
          setActiveId(parsed[0].id);
          setReady(true);
          return;
        }
      }
    } catch { /* corrupt storage */ }
    const initial = newConversation();
    setConversations([initial]);
    setActiveId(initial.id);
    setReady(true);
  }, []);

  // Persist on every change
  useEffect(() => {
    if (ready) localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
  }, [conversations, ready]);

  const handleNewChat = useCallback(() => {
    const conv = newConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveId(conv.id);
  }, []);

  const handleSelect = useCallback((id: string) => setActiveId(id), []);

  const handleDelete = useCallback((id: string) => {
    setConversations((prev) => {
      const next = prev.filter((c) => c.id !== id);
      if (next.length === 0) {
        const fresh = newConversation();
        setActiveId(fresh.id);
        return [fresh];
      }
      if (id === activeId) setActiveId(next[0].id);
      return next;
    });
  }, [activeId]);

  const handleSend = useCallback(async (text: string) => {
    if (!activeId || loading) return;

    const userMsg: Message = {
      id: uuidv4(), role: 'user', content: text, charts: [], timestamp: Date.now(),
    };

    // Append user message + set title on first message
    setConversations((prev) => prev.map((c) => {
      if (c.id !== activeId) return c;
      return {
        ...c,
        title: c.messages.length === 0 ? text.slice(0, 48) : c.title,
        messages: [...c.messages, userMsg],
      };
    }));

    setLoading(true);
    try {
      const result = await sendMessage({ message: text, thread_id: activeId });
      const assistantMsg: Message = {
        id: uuidv4(), role: 'assistant',
        content: result.response, charts: result.charts, timestamp: Date.now(),
      };
      setConversations((prev) => prev.map((c) =>
        c.id === activeId ? { ...c, messages: [...c.messages, assistantMsg] } : c
      ));
    } catch {
      const errMsg: Message = {
        id: uuidv4(), role: 'assistant',
        content: 'Ocurrió un error al procesar tu mensaje. Por favor intentá de nuevo.',
        charts: [], timestamp: Date.now(),
      };
      setConversations((prev) => prev.map((c) =>
        c.id === activeId ? { ...c, messages: [...c.messages, errMsg] } : c
      ));
    } finally {
      setLoading(false);
    }
  }, [activeId, loading]);

  // Avoid hydration mismatch
  if (!ready) return null;

  const active = conversations.find((c) => c.id === activeId);

  return (
    <div className="flex h-screen overflow-hidden bg-white">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onNew={handleNewChat}
        onSelect={handleSelect}
        onDelete={handleDelete}
      />
      <main className="flex min-w-0 flex-1 flex-col bg-[#F8F8F8]">
        <ChatWindow
          messages={active?.messages ?? []}
          loading={loading}
          onSend={handleSend}
        />
        <ChatInput onSend={handleSend} disabled={loading} />
      </main>
    </div>
  );
}
