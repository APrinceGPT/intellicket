import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = 'http://localhost:5003'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  try {
    const { sessionId } = await params
    console.log('🔧 AMSP Results: Fetching results for session:', sessionId)

    const response = await fetch(`${BACKEND_URL}/results/${sessionId}`, {
      method: 'GET',
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('🔧 AMSP Results: Backend error:', errorText)
      throw new Error(`Backend results fetch failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('🔧 AMSP Results: Results fetched successfully')
    
    // Log some key information about the results
    if (result.metadata) {
      console.log(`🔧 AMSP Results: Files processed: ${result.metadata.files_processed}`)
      console.log(`🔧 AMSP Results: Errors found: ${result.metadata.errors_found}`)
      console.log(`🔧 AMSP Results: Pattern failures: ${result.metadata.pattern_failures}`)
    }

    return NextResponse.json(result)
  } catch (error) {
    console.error('🔧 AMSP Results: Error fetching results:', error)
    return NextResponse.json(
      { error: 'AMSP results fetch failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}