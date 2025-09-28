import { NextRequest, NextResponse } from 'next/server';
import JSZip from 'jszip';

const BACKEND_URL = 'http://localhost:5003';

// File mapping for different analyzers - EXACT REQUIREMENTS MATCH
const ANALYZER_FILE_MAPPING = {
  'amsp': ['AMSPInstallDebuglog.log', 'ds_am.log', 'ds_agent.log'],  // Only required AMSP files
  'amsp_logs': ['AMSPInstallDebuglog.log', 'ds_am.log', 'ds_agent.log'],  // Only required AMSP files
  'resource': ['TopNBusyProcess.txt', 'RunningProcess.xml', 'RunningProcesses.xml'],  // Resource files with both XML variants
  'resource_analysis': ['TopNBusyProcess.txt', 'RunningProcess.xml', 'RunningProcesses.xml'],  // Resource files with both XML variants
  'ds_agent_offline': ['ds_connect.log', 'ds_agent.log', 'ds_agent-err.log'],  // Only core files for offline analysis
  'conflict': ['RunningProcess.xml', 'RunningProcesses.xml'],  // Both XML variants for conflict analysis
  'av_conflicts': ['RunningProcess.xml', 'RunningProcesses.xml']  // Both XML variants for conflict analysis
};

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];
    const analyzerId = formData.get('analyzerId') as string;

    if (!analyzerId || !ANALYZER_FILE_MAPPING[analyzerId as keyof typeof ANALYZER_FILE_MAPPING]) {
      return NextResponse.json({ 
        success: false, 
        error: 'Invalid analyzer ID' 
      }, { status: 400 });
    }

    const requiredFiles = ANALYZER_FILE_MAPPING[analyzerId as keyof typeof ANALYZER_FILE_MAPPING];
    const extractedFiles: File[] = [];

    for (const file of files) {
      if (file.name.toLowerCase().endsWith('.zip')) {
        // Extract ZIP file
        const arrayBuffer = await file.arrayBuffer();
        const zip = new JSZip();
        const zipContent = await zip.loadAsync(arrayBuffer);

        // Look for required files in the ZIP
        for (const [path, zipFile] of Object.entries(zipContent.files)) {
          if (!zipFile.dir) {
            const fileName = path.split('/').pop()?.toLowerCase() || '';
            
            // Check if this file is needed for the analyzer
            const isRequired = requiredFiles.some(reqFile => {
              // Use EXACT matching for ALL analyzers to prevent unwanted files
              return fileName === reqFile.toLowerCase(); // Exact match only
            }) && !fileName.includes('timestamp') && !fileName.includes('temp'); // Exclude timestamp and temp files

            if (isRequired) {
              const content = await zipFile.async('arraybuffer');
              
              // Skip empty files
              if (content.byteLength === 0) {
                continue;
              }
              
              const extractedFile = new File([content], path.split('/').pop() || fileName, {
                type: 'text/plain'
              });
              extractedFiles.push(extractedFile);
            }
          }
        }
      } else {
        // Check if the file itself is required
        const fileName = file.name.toLowerCase();
        const isRequired = requiredFiles.some(reqFile => {
          const reqFileBase = reqFile.toLowerCase().replace('.log', '');
          const fileNameBase = fileName.replace(/\.(log|txt|xml)$/, '');
          
          return (
            fileName === reqFile.toLowerCase() || // Exact match
            fileName.includes(reqFileBase) || // Partial match
            reqFile.toLowerCase().includes(fileNameBase) || // Reverse partial match
            (fileName.endsWith('.log') && reqFileBase.includes(fileNameBase)) || // Log file match
            (fileName.endsWith('.xml') && reqFile.toLowerCase().includes('xml')) || // XML file match
            (fileName === 'runningprocesses.xml' || fileName === 'runningprocess.xml') || // Process files
            (fileName === 'topnbusyprocess.txt') // Resource analysis files
          );
        }) && !fileName.includes('timestamp') && !fileName.includes('temp'); // Exclude timestamp and temp files

        if (isRequired) {
          // Skip empty files
          if (file.size === 0) {
            continue;
          }
          
          extractedFiles.push(file);
        }
      }
    }

    if (extractedFiles.length === 0) {
      return NextResponse.json({ 
        success: false, 
        error: `No required files found for ${analyzerId} analyzer`,
        requiredFiles: requiredFiles
      }, { status: 404 });
    }

    // Upload extracted files to the backend
    const uploadFormData = new FormData();
    extractedFiles.forEach((file) => {
      uploadFormData.append('files', file);
    });

    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      body: uploadFormData,
    });

    let uploadResult;
    try {
      // Try to parse as JSON first
      const responseText = await response.text();
      
      if (responseText.trim().startsWith('{') || responseText.trim().startsWith('[')) {
        uploadResult = JSON.parse(responseText);
      } else {
        // Handle HTML error responses
        console.error('Backend returned non-JSON response:', responseText);
        
        if (response.status === 413 || responseText.includes('Request Entity Too Large')) {
          return NextResponse.json({ 
            success: false, 
            error: 'File size too large. Please upload smaller files.',
            statusCode: 413
          }, { status: 413 });
        }
        
        if (responseText.includes('Security Error') || responseText.includes('File must be')) {
          return NextResponse.json({ 
            success: false, 
            error: 'File type validation error. Some extracted files may not be supported.',
            statusCode: 400
          }, { status: 400 });
        }
        
        return NextResponse.json({ 
          success: false, 
          error: `Backend error: ${response.statusText} (${response.status})`,
          statusCode: response.status
        }, { status: 500 });
      }
    } catch (parseError) {
      console.error('Error parsing response:', parseError);
      return NextResponse.json({ 
        success: false, 
        error: 'Invalid response from backend',
        statusCode: response.status
      }, { status: 500 });
    }

    // Check if the upload was successful
    if (!response.ok) {
      return NextResponse.json({ 
        success: false, 
        error: uploadResult?.error || `Upload failed with status ${response.status}`,
        statusCode: response.status
      }, { status: response.status });
    }

    return NextResponse.json({
      success: true,
      extractedFiles: extractedFiles.map(f => ({ name: f.name, size: f.size })),
      uploadResult,
      analyzerId
    }, { 
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    });

  } catch (error) {
    console.error('Extract and upload error:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Extract and upload failed'
    }, { status: 500 });
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
