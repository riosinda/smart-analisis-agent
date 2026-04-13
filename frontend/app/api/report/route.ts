import { NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8000';

export async function POST() {
  try {
    const upstream = await fetch(`${BACKEND}/api/report`, { method: 'POST' });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch {
    return NextResponse.json({ error: 'Backend no disponible' }, { status: 503 });
  }
}
