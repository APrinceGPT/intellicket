import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5003';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/admin/stats/uploads`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    // Add frontend processing timestamp and source info
    const enhancedData = {
      ...data,
      frontend_processed_at: new Date().toISOString(),
      data_flow: 'localhost:3001 → localhost:3000 → localhost:5003',
      proxy_source: 'main_frontend'
    };
    
    return NextResponse.json(enhancedData);
  } catch (error) {
    console.error('Error fetching upload statistics:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch upload statistics', 
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: BACKEND_URL,
        data_flow: 'localhost:3001 → localhost:3000 → [ERROR] → localhost:5003'
      },
      { status: 500 }
    );
  }
}