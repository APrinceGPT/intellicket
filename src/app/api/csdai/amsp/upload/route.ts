import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = 'http://localhost:5003'

export async function POST(request: NextRequest) {
  try {
    console.log('🔧 AMSP Upload: Starting file upload process...')
    
    // Get the form data from the request
    const formData = await request.formData()
    
    // Force analysis_type to 'amsp' for dedicated endpoint
    formData.set('analysis_type', 'amsp')
    
    console.log('🔧 AMSP Upload: Forcing analysis_type to "amsp"')
    
    // Count uploaded files for logging
    const fileCount = Array.from(formData.entries()).filter(([key]) => key.startsWith('file')).length
    console.log(`🔧 AMSP Upload: Processing ${fileCount} files`)
    
    // Forward to backend
    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('🔧 AMSP Upload: Backend error:', errorText)
      throw new Error(`Backend upload failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('🔧 AMSP Upload: Success! Session ID:', result.session_id)

    return NextResponse.json(result)
  } catch (error) {
    console.error('🔧 AMSP Upload: Error during upload:', error)
    return NextResponse.json(
      { error: 'AMSP file upload failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}