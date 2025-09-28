import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5003';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/admin/system/overview`, {
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
    
    // Add proxy and frontend information
    const enhancedData = {
      ...data,
      proxy_info: {
        frontend_proxy: 'localhost:3000',
        admin_dashboard: 'localhost:3001',
        backend: 'localhost:5003',
        data_flow: 'Admin Dashboard → Main Frontend → Backend',
        proxy_healthy: true,
        check_time: new Date().toISOString()
      }
    };
    
    return NextResponse.json(enhancedData);
  } catch (error) {
    console.error('Error fetching system overview:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch system overview', 
        details: error instanceof Error ? error.message : 'Unknown error',
        proxy_info: {
          frontend_proxy: 'localhost:3000',
          admin_dashboard: 'localhost:3001', 
          backend: 'localhost:5003',
          data_flow: 'Admin Dashboard → Main Frontend → [ERROR] → Backend',
          proxy_healthy: false,
          error_time: new Date().toISOString()
        }
      },
      { status: 500 }
    );
  }
}