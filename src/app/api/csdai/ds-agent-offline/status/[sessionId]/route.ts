import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;
    
    console.log(`🔍 DS Agent Offline: Checking status for session ${sessionId}`);
    
    const response = await fetch(`${BACKEND_URL}/status/${sessionId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ DS Agent Offline status check failed:', response.status, errorText);
      return NextResponse.json(
        { error: 'Status check failed', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ DS Agent Offline status:', data);

    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ DS Agent Offline status error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}