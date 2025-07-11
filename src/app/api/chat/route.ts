// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  try {
    const res = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();

    return NextResponse.json({ response: data.response });
  } catch (err) {
    console.error('API error:', err);
    return NextResponse.json({ response: 'Error contacting GeminiBot' }, { status: 500 });
  }
}
