import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;
    
    // Try the specific session cleanup endpoint first
    let response = await fetch(`${BACKEND_URL}/cleanup/session/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // If session-specific cleanup not available, fall back to global cleanup
    if (response.status === 404) {
      response = await fetch(`${BACKEND_URL}/api/sessions/cleanup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        return NextResponse.json({ 
          success: true, 
          message: `Session cleanup completed via global cleanup (${result.cleaned_sessions} sessions cleaned)`,
          fallback: true,
          ...result
        });
      }
    }

    if (response.ok) {
      const result = await response.json();
      return NextResponse.json({ 
        success: true, 
        message: `Session ${sessionId} cleaned up successfully`,
        ...result
      });
    } else {
      const errorResult = await response.json().catch(() => ({}));
      return NextResponse.json({ 
        success: false, 
        message: `Failed to cleanup session ${sessionId}`,
        ...errorResult
      }, { status: response.status });
    }
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      message: 'Error cleaning up session',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function POST() {
  try {
    // Clean up all old sessions using the new cache endpoint
    const response = await fetch(`${BACKEND_URL}/cleanup/cache`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const result = await response.json();
      return NextResponse.json({ 
        success: true, 
        message: 'Cache cleanup completed successfully',
        ...result
      });
    } else {
      const errorResult = await response.json().catch(() => ({}));
      return NextResponse.json({ 
        success: false, 
        message: 'Failed to cleanup cache',
        ...errorResult
      }, { status: response.status });
    }
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      message: 'Error cleaning up cache',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}