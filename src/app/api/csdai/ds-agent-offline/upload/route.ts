import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    // Force analysis type to ds_agent_offline for this dedicated endpoint
    formData.set('analysis_type', 'ds_agent_offline');
    
    console.log('🎯 DS Agent Offline: Uploading files to backend...');
    
    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ DS Agent Offline upload failed:', response.status, errorText);
      return NextResponse.json(
        { error: 'Upload failed', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ DS Agent Offline upload successful:', data);

    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ DS Agent Offline upload error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}