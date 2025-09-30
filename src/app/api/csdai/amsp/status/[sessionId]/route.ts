import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = 'http://localhost:5003'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params
    console.log('🔧 AMSP Status: Checking status for session:', sessionId)

    const response = await fetch(`${BACKEND_URL}/status/${sessionId}`, {
      method: 'GET',
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('🔧 AMSP Status: Backend error:', errorText)
      throw new Error(`Backend status check failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('🔧 AMSP Status: Status check result:', result.status || 'unknown')

    return NextResponse.json(result)
  } catch (error) {
    console.error('🔧 AMSP Status: Error checking status:', error)
    return NextResponse.json(
      { error: 'AMSP status check failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}