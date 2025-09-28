import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5003';

export async function GET() {
  try {
    // Fetch statistics from backend
    const [uploadsResponse, analyzersResponse] = await Promise.all([
      fetch(`${BACKEND_URL}/admin/stats/uploads`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      }),
      fetch(`${BACKEND_URL}/admin/stats/analyzers`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      })
    ]);

    if (!uploadsResponse.ok || !analyzersResponse.ok) {
      throw new Error(`Backend responded with status: uploads=${uploadsResponse.status}, analyzers=${analyzersResponse.status}`);
    }

    const uploadsData = await uploadsResponse.json();
    const analyzersData = await analyzersResponse.json();

    // Combine and format the statistics for frontend consumption
    const combinedStats = {
      uploads: uploadsData.data || uploadsData,
      analyzers: analyzersData.data || analyzersData,
      timestamp: new Date().toISOString(),
      source: 'main_frontend_proxy',
      backend_url: BACKEND_URL
    };

    return NextResponse.json({
      success: true,
      data: combinedStats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error fetching admin statistics:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch statistics', 
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: BACKEND_URL
      },
      { status: 500 }
    );
  }
}