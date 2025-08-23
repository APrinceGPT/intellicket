import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params;
    
    const response = await fetch(`${BACKEND_URL}/export/${sessionId}`, {
      method: 'GET',
    });

    if (response.ok) {
      const data = await response.blob();
      const contentType = response.headers.get('content-type') || 'application/octet-stream';
      const contentDisposition = response.headers.get('content-disposition') || `attachment; filename="analysis-${sessionId}.txt"`;
      
      return new NextResponse(data, {
        status: 200,
        headers: {
          'Content-Type': contentType,
          'Content-Disposition': contentDisposition,
          'Access-Control-Allow-Origin': '*',
        },
      });
    } else {
      return NextResponse.json({ 
        success: false, 
        error: 'Export failed'
      }, { status: response.status });
    }
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Export failed'
    }, { status: 500 });
  }
}
