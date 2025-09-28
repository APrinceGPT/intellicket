import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:5003';

export async function POST(request: NextRequest) {
  try {
    // Get the form data from the request
    const formData = await request.formData();
    
    // Forward the request to the Flask backend
    const response = await fetch(`${BACKEND_URL}/extract-and-filter`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Extract and filter proxy error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Extract and filter failed' 
      },
      { status: 500 }
    );
  }
}
