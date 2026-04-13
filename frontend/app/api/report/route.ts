import { NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8000';

export async function POST() {
  try {
    const upstream = await fetch(`${BACKEND}/api/report`, { method: 'POST' });
    const buffer = await upstream.arrayBuffer();
    return new NextResponse(buffer, {
      status: upstream.status,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=reporte_insights_rappi.pdf',
      },
    });
  } catch {
    return NextResponse.json({ error: 'Backend no disponible' }, { status: 503 });
  }
}
