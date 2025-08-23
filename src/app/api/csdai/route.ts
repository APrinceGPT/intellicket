import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/wizard/1`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      redirect: 'manual' // Don't follow redirects
    });

    // CSDAIv2 returns 200 or 302 when working properly
    if (response.status === 200 || response.status === 302) {
      return NextResponse.json({ 
        success: true, 
        status: 'connected',
        message: 'CSDAIv2 backend is running',
        backend_status: response.status 
      });
    } else {
      return NextResponse.json({ 
        success: false, 
        status: 'error',
        message: 'Backend returned error' 
      }, { status: response.status });
    }
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      status: 'offline',
      message: 'Cannot connect to CSDAIv2 backend',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 503 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    
    return NextResponse.json(data, { 
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    });
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
