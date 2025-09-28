import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5003';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/admin/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`);
    }

    const data = await response.json();
    
    // Add proxy information
    const enhancedData = {
      ...data,
      proxy_status: 'healthy',
      data_flow: 'localhost:3001 → localhost:3000 → localhost:5003',
      frontend_check_time: new Date().toISOString()
    };
    
    return NextResponse.json(enhancedData);
  } catch (error) {
    console.error('Error checking backend health:', error);
    return NextResponse.json(
      { 
        success: false,
        proxy_status: 'error',
        error: 'Backend health check failed', 
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: BACKEND_URL,
        data_flow: 'localhost:3001 → localhost:3000 → [ERROR] → localhost:5003'
      },
      { status: 500 }
    );
  }
}