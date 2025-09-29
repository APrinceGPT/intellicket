import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;
    
    console.log(`📊 DS Agent Offline: Fetching results for session ${sessionId}`);
    
    const response = await fetch(`${BACKEND_URL}/results/${sessionId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ DS Agent Offline results fetch failed:', response.status, errorText);
      return NextResponse.json(
        { error: 'Results fetch failed', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ DS Agent Offline results fetched successfully');

    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ DS Agent Offline results error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}