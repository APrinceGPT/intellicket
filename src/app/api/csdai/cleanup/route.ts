import { NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function POST() {
  try {
    // Use the existing working cleanup endpoint
    const response = await fetch(`${BACKEND_URL}/api/sessions/cleanup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const result = await response.json();
      return NextResponse.json({ 
        success: true, 
        message: 'Global cache cleanup completed successfully',
        ...result
      });
    } else {
      const errorResult = await response.json().catch(() => ({}));
      return NextResponse.json({ 
        success: false, 
        message: 'Failed to cleanup global cache',
        ...errorResult
      }, { status: response.status });
    }
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      message: 'Error cleaning up global cache',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}