import { NextRequest, NextResponse } from 'next/server';

interface FileAnalysisRequest {
  fileName: string;
  fileSize: number;
  fileType: string;
  fileContent?: string; // For text files, first 1000 characters
  product: string;
  issueDescription?: string;
}

interface FileAnalysisResult {
  fileType: 'log' | 'diagnostic' | 'configuration' | 'screenshot' | 'archive' | 'document' | 'other';
  relevanceScore: number; // 0-100
  detectedIssues: string[];
  extractionPreview: string[];
  recommendedAnalyzer: string[];
  missingFiles: string[];
  processingPriority: 'High' | 'Medium' | 'Low';
  estimatedAnalysisTime: string;
  fileCategory: string;
  securityRisk: 'None' | 'Low' | 'Medium' | 'High';
  dataQuality: {
    completeness: number;
    readability: number;
    relevance: number;
  };
}

interface BatchFileAnalysis {
  files: (FileAnalysisResult & { fileName: string })[];
  overallAssessment: {
    completenessScore: number;
    missingCriticalFiles: string[];
    recommendedCollectionOrder: string[];
    estimatedTotalAnalysisTime: string;
  };
  suggestedAnalysisFlow: string[];
}

// AI-powered file analysis for intelligent processing
function analyzeFile(request: FileAnalysisRequest): FileAnalysisResult {
  const { fileName, fileSize, fileType, fileContent, product, issueDescription } = request;
  
  const extensionMatch = fileName.match(/\.([^.]+)$/);
  const extension = extensionMatch ? extensionMatch[1].toLowerCase() : '';
  
  // Classify file type
  const classifiedType = classifyFileType(fileName, fileType, extension);
  
  // Calculate relevance score
  const relevanceScore = calculateRelevanceScore(fileName, fileContent, product, issueDescription);
  
  // Detect potential issues in file
  const detectedIssues = detectFileIssues(fileName, fileContent, fileSize);
  
  // Generate extraction preview
  const extractionPreview = generateExtractionPreview(fileName, fileContent, classifiedType);
  
  // Recommend appropriate analyzers
  const recommendedAnalyzer = recommendAnalyzers(fileName, classifiedType, product, issueDescription);
  
  // Identify missing complementary files
  const missingFiles = identifyMissingFiles(fileName, classifiedType, product);
  
  // Determine processing priority
  const processingPriority = determineProcessingPriority(classifiedType, relevanceScore, detectedIssues);
  
  // Estimate analysis time
  const estimatedAnalysisTime = estimateAnalysisTime(classifiedType, fileSize, detectedIssues.length);
  
  // Categorize file
  const fileCategory = categorizeFile(fileName, classifiedType, product);
  
  // Assess security risk
  const securityRisk = assessSecurityRisk(fileName, fileType, fileContent);
  
  // Evaluate data quality
  const dataQuality = evaluateDataQuality(fileName, fileContent, fileSize, classifiedType);
  
  return {
    fileType: classifiedType,
    relevanceScore,
    detectedIssues,
    extractionPreview,
    recommendedAnalyzer,
    missingFiles,
    processingPriority,
    estimatedAnalysisTime,
    fileCategory,
    securityRisk,
    dataQuality
  };
}

function classifyFileType(fileName: string, mimeType: string, extension: string): FileAnalysisResult['fileType'] {
  const fileNameLower = fileName.toLowerCase();
  
  // Archive files
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension) || 
      mimeType.includes('zip') || mimeType.includes('compressed')) {
    return 'archive';
  }
  
  // Log files
  if (['log', 'txt'].includes(extension) || 
      fileNameLower.includes('log') || 
      fileNameLower.includes('event') ||
      fileNameLower.includes('trace') ||
      fileNameLower.includes('debug')) {
    return 'log';
  }
  
  // Configuration files
  if (['cfg', 'conf', 'config', 'ini', 'xml', 'json', 'yaml', 'yml'].includes(extension) ||
      fileNameLower.includes('config') ||
      fileNameLower.includes('setting')) {
    return 'configuration';
  }
  
  // Screenshots and images
  if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(extension) ||
      mimeType.startsWith('image/')) {
    return 'screenshot';
  }
  
  // Diagnostic packages
  if (fileNameLower.includes('diagnostic') ||
      fileNameLower.includes('support') ||
      fileNameLower.includes('package') ||
      fileNameLower.includes('bundle')) {
    return 'diagnostic';
  }
  
  // Documents
  if (['pdf', 'doc', 'docx', 'rtf'].includes(extension) ||
      mimeType.includes('document')) {
    return 'document';
  }
  
  return 'other';
}

function calculateRelevanceScore(fileName: string, content: string = '', product: string, issueDescription: string = ''): number {
  let score = 20; // Base score
  
  const fileNameLower = fileName.toLowerCase();
  const contentLower = content.toLowerCase();
  const issueLower = issueDescription.toLowerCase();
  const productLower = product.toLowerCase();
  
  // Product-specific relevance
  if (productLower.includes('deep security')) {
    const dsTerms = ['deep security', 'ds', 'agent', 'manager', 'amsp', 'dsa', 'dsm'];
    dsTerms.forEach(term => {
      if (fileNameLower.includes(term) || contentLower.includes(term)) {
        score += 15;
      }
    });
  } else if (productLower.includes('vision one')) {
    const v1Terms = ['vision one', 'v1', 'connector', 'endpoint sensor', 'workbench'];
    v1Terms.forEach(term => {
      if (fileNameLower.includes(term) || contentLower.includes(term)) {
        score += 15;
      }
    });
  } else if (productLower.includes('apex one')) {
    const apexTerms = ['apex one', 'apex', 'security agent', 'ofcscan', 'web console'];
    apexTerms.forEach(term => {
      if (fileNameLower.includes(term) || contentLower.includes(term)) {
        score += 15;
      }
    });
  }
  
  // Issue-specific relevance
  if (issueDescription) {
    const issueKeywords = issueLower.split(' ').filter(word => word.length > 3);
    issueKeywords.forEach(keyword => {
      if (fileNameLower.includes(keyword) || contentLower.includes(keyword)) {
        score += 10;
      }
    });
  }
  
  // File type relevance
  if (fileNameLower.includes('error') || contentLower.includes('error')) score += 15;
  if (fileNameLower.includes('log') || contentLower.includes('log')) score += 10;
  if (fileNameLower.includes('diagnostic') || contentLower.includes('diagnostic')) score += 20;
  
  // Temporal relevance (recent files are more relevant)
  if (fileNameLower.includes(new Date().getFullYear().toString())) score += 5;
  
  return Math.min(score, 100);
}

function detectFileIssues(fileName: string, content: string = '', fileSize: number): string[] {
  const issues: string[] = [];
  const fileNameLower = fileName.toLowerCase();
  const contentLower = content.toLowerCase();
  
  // File size issues
  if (fileSize > 100 * 1024 * 1024) { // 100MB
    issues.push('Large file size may require extended processing time');
  } else if (fileSize < 100) { // Very small files
    issues.push('File appears to be very small - may be incomplete');
  }
  
  // Content-based issue detection
  if (content) {
    // Error indicators
    const errorPatterns = [
      /error/gi, /exception/gi, /failed/gi, /failure/gi,
      /timeout/gi, /denied/gi, /refused/gi, /abort/gi
    ];
    
    let errorCount = 0;
    errorPatterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches) errorCount += matches.length;
    });
    
    if (errorCount > 10) {
      issues.push(`Multiple errors detected (${errorCount} error entries)`);
    } else if (errorCount > 0) {
      issues.push(`${errorCount} error entries found`);
    }
    
    // Performance indicators
    if (contentLower.includes('high cpu') || contentLower.includes('memory')) {
      issues.push('Performance-related entries detected');
    }
    
    // Security indicators
    if (contentLower.includes('malware') || contentLower.includes('threat') || 
        contentLower.includes('virus') || contentLower.includes('suspicious')) {
      issues.push('Security-related events detected');
    }
    
    // Service issues
    if (contentLower.includes('service') && (contentLower.includes('stop') || contentLower.includes('fail'))) {
      issues.push('Service failure events detected');
    }
  }
  
  // File name issues
  if (fileNameLower.includes('dump') || fileNameLower.includes('crash')) {
    issues.push('Crash or dump file detected');
  }
  
  if (fileNameLower.includes('corrupt') || fileNameLower.includes('partial')) {
    issues.push('Potentially corrupted or incomplete file');
  }
  
  return issues;
}

function generateExtractionPreview(fileName: string, content: string = '', fileType: FileAnalysisResult['fileType']): string[] {
  const preview: string[] = [];
  const fileNameLower = fileName.toLowerCase();
  
  if (!content) {
    preview.push(`File: ${fileName}`);
    preview.push(`Type: ${fileType}`);
    preview.push('Content preview not available (binary or inaccessible file)');
    return preview;
  }
  
  const lines = content.split('\n').slice(0, 10); // First 10 lines
  
  // Extract key information based on file type
  switch (fileType) {
    case 'log':
      preview.push('Log File Analysis Preview:');
      
      // Find timestamp patterns
      const timestampPattern = /\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}/;
      const timestampLine = lines.find(line => timestampPattern.test(line));
      if (timestampLine) {
        preview.push(`Latest timestamp: ${timestampLine.substring(0, 50)}...`);
      }
      
      // Find error patterns
      const errorLine = lines.find(line => /error|exception|failed/i.test(line));
      if (errorLine) {
        preview.push(`Error detected: ${errorLine.substring(0, 80)}...`);
      }
      
      break;
      
    case 'configuration':
      preview.push('Configuration File Preview:');
      
      // Extract key configuration entries
      lines.forEach(line => {
        if (line.includes('=') || line.includes(':')) {
          preview.push(`Config: ${line.substring(0, 60)}...`);
        }
      });
      
      break;
      
    case 'diagnostic':
      preview.push('Diagnostic Package Contents:');
      preview.push(`System information and logs collection`);
      if (fileNameLower.includes('deep security')) {
        preview.push('Deep Security diagnostic data detected');
      }
      break;
      
    default:
      preview.push(`${fileType} file preview:`);
      preview.push(content.substring(0, 200) + '...');
  }
  
  return preview.slice(0, 5); // Limit preview lines
}

function recommendAnalyzers(fileName: string, fileType: FileAnalysisResult['fileType'], product: string, issueDescription: string = ''): string[] {
  const analyzers: string[] = [];
  const fileNameLower = fileName.toLowerCase();
  const issueLower = issueDescription.toLowerCase();
  const productLower = product.toLowerCase();
  
  // Product-specific analyzer recommendations
  if (productLower.includes('deep security')) {
    // AMSP Analyzer
    if (fileNameLower.includes('amsp') || fileNameLower.includes('scan') || 
        issueLower.includes('malware') || issueLower.includes('performance')) {
      analyzers.push('AMSP Performance Analyzer');
    }
    
    // Agent Log Analyzer - REMOVED FROM FRONTEND  
    // DS Agent Log analysis is handled backend-only
    // Note: DS Agent Offline Analyzer remains available for offline issues
    
    // Conflict Analyzer
    if (fileNameLower.includes('conflict') || fileNameLower.includes('third') ||
        issueLower.includes('incompatible') || issueLower.includes('antivirus')) {
      analyzers.push('Conflict Detection Analyzer');
    }
    
    // Resource Analyzer
    if (fileNameLower.includes('resource') || fileNameLower.includes('performance') ||
        issueLower.includes('cpu') || issueLower.includes('memory')) {
      analyzers.push('Resource Usage Analyzer');
    }
    
    // Diagnostic Package Analyzer
    if (fileType === 'diagnostic' || fileNameLower.includes('diagnostic') ||
        fileNameLower.includes('support') || fileNameLower.includes('package')) {
      analyzers.push('Comprehensive Diagnostic Analyzer');
    }
  }
  
  // Generic analyzers based on file type
  if (fileType === 'log') {
    analyzers.push('Log Pattern Analyzer');
  }
  
  if (fileType === 'configuration') {
    analyzers.push('Configuration Validator');
  }
  
  if (fileType === 'archive') {
    analyzers.push('Archive Content Analyzer');
  }
  
  return [...new Set(analyzers)]; // Remove duplicates
}

function identifyMissingFiles(fileName: string, fileType: FileAnalysisResult['fileType'], product: string): string[] {
  const missing: string[] = [];
  const fileNameLower = fileName.toLowerCase();
  const productLower = product.toLowerCase();
  
  // Product-specific missing file detection
  if (productLower.includes('deep security')) {
    if (fileNameLower.includes('agent') && !fileNameLower.includes('manager')) {
      missing.push('Deep Security Manager logs');
    }
    
    if (fileNameLower.includes('manager') && !fileNameLower.includes('agent')) {
      missing.push('Deep Security Agent logs from affected systems');
    }
    
    if (fileType === 'log' && !fileNameLower.includes('system')) {
      missing.push('System event logs (Windows Event Log or syslog)');
    }
    
    if (!fileNameLower.includes('diagnostic') && !fileNameLower.includes('config')) {
      missing.push('Configuration files or diagnostic package');
    }
    
    if (fileNameLower.includes('performance') && !fileNameLower.includes('resource')) {
      missing.push('Resource utilization data (CPU, memory, disk usage)');
    }
  }
  
  // General missing files based on file type
  if (fileType === 'configuration' && !missing.some(m => m.includes('log'))) {
    missing.push('Related log files showing configuration application');
  }
  
  if (fileType === 'screenshot' && !missing.some(m => m.includes('log'))) {
    missing.push('Log files corresponding to the time of the screenshot');
  }
  
  return missing.slice(0, 4); // Limit to 4 suggestions
}

function determineProcessingPriority(fileType: FileAnalysisResult['fileType'], relevanceScore: number, detectedIssues: string[]): 'High' | 'Medium' | 'Low' {
  // High priority conditions
  if (relevanceScore >= 80 || detectedIssues.length >= 3) {
    return 'High';
  }
  
  if (fileType === 'diagnostic' || fileType === 'log') {
    return 'High';
  }
  
  // Medium priority conditions
  if (relevanceScore >= 50 || detectedIssues.length >= 1) {
    return 'Medium';
  }
  
  if (fileType === 'configuration') {
    return 'Medium';
  }
  
  // Low priority for everything else
  return 'Low';
}

function estimateAnalysisTime(fileType: FileAnalysisResult['fileType'], fileSize: number, issueCount: number): string {
  let baseTime = 2; // minutes
  
  // Adjust for file type
  switch (fileType) {
    case 'diagnostic':
      baseTime = 15;
      break;
    case 'log':
      baseTime = 8;
      break;
    case 'archive':
      baseTime = 12;
      break;
    case 'configuration':
      baseTime = 5;
      break;
    case 'screenshot':
      baseTime = 1;
      break;
    default:
      baseTime = 3;
  }
  
  // Adjust for file size
  const sizeMB = fileSize / (1024 * 1024);
  if (sizeMB > 100) baseTime *= 3;
  else if (sizeMB > 10) baseTime *= 2;
  else if (sizeMB > 1) baseTime *= 1.5;
  
  // Adjust for issue complexity
  baseTime += issueCount * 2;
  
  if (baseTime <= 3) return '1-3 minutes';
  if (baseTime <= 8) return '5-8 minutes';
  if (baseTime <= 15) return '10-15 minutes';
  if (baseTime <= 30) return '15-30 minutes';
  return '30+ minutes';
}

function categorizeFile(fileName: string, fileType: FileAnalysisResult['fileType'], product: string): string {
  const fileNameLower = fileName.toLowerCase();
  const productLower = product.toLowerCase();
  
  // Product-specific categorization
  if (productLower.includes('deep security')) {
    if (fileNameLower.includes('amsp')) return 'Anti-Malware Scan Performance';
    if (fileNameLower.includes('agent')) return 'Agent Communication & Status';
    if (fileNameLower.includes('manager')) return 'Manager Operations & Configuration';
    if (fileNameLower.includes('policy')) return 'Policy Management & Deployment';
    if (fileNameLower.includes('database')) return 'Database Operations & Performance';
  }
  
  // Generic categorization by file type
  switch (fileType) {
    case 'log': return 'System & Application Logs';
    case 'diagnostic': return 'Comprehensive Diagnostic Data';
    case 'configuration': return 'Configuration & Settings';
    case 'screenshot': return 'Visual Documentation';
    case 'archive': return 'Compressed File Collection';
    case 'document': return 'Documentation & Reports';
    default: return 'General Support Files';
  }
}

function assessSecurityRisk(fileName: string, mimeType: string, content: string = ''): 'None' | 'Low' | 'Medium' | 'High' {
  const contentLower = content.toLowerCase();
  
  // High risk indicators
  if (mimeType.includes('executable') || 
      ['exe', 'bat', 'cmd', 'ps1', 'sh'].some(ext => fileName.endsWith(ext))) {
    return 'High';
  }
  
  // Medium risk indicators
  if (contentLower.includes('password') || contentLower.includes('credential') ||
      contentLower.includes('private key') || contentLower.includes('certificate')) {
    return 'Medium';
  }
  
  if (['zip', 'rar', '7z'].some(ext => fileName.endsWith(ext))) {
    return 'Low'; // Archives need to be scanned
  }
  
  // Low risk for standard support files
  if (['log', 'txt', 'cfg', 'xml', 'json'].some(ext => fileName.endsWith(ext))) {
    return 'None';
  }
  
  return 'Low'; // Default to low risk
}

function evaluateDataQuality(fileName: string, content: string = '', fileSize: number, fileType: FileAnalysisResult['fileType']): { completeness: number; readability: number; relevance: number } {
  let completeness = 50;
  let readability = 50;
  let relevance = 50;
  
  // Completeness assessment
  if (fileSize > 10 * 1024) completeness += 20; // Files > 10KB are likely more complete
  if (content && content.length > 1000) completeness += 15;
  if (fileType === 'diagnostic') completeness += 20; // Diagnostic packages are comprehensive
  
  // Readability assessment
  if (content) {
    const lines = content.split('\n');
    if (lines.length > 10) readability += 15;
    
    // Check for structured data
    if (content.includes('{') || content.includes('<') || content.includes('=')) {
      readability += 20; // Structured data is more readable
    }
    
    // Check for timestamps (indicates organized logging)
    if (/\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}/.test(content)) {
      readability += 15;
    }
  }
  
  // Relevance assessment based on file name and type
  if (fileName.toLowerCase().includes('error') || fileName.toLowerCase().includes('diagnostic')) {
    relevance += 25;
  }
  
  if (['log', 'diagnostic', 'configuration'].includes(fileType)) {
    relevance += 20;
  }
  
  return {
    completeness: Math.min(completeness, 100),
    readability: Math.min(readability, 100),
    relevance: Math.min(relevance, 100)
  };
}

// Batch analysis for multiple files
function analyzeBatch(files: FileAnalysisRequest[]): BatchFileAnalysis {
  const analyzedFiles = files.map(file => ({
    fileName: file.fileName,
    ...analyzeFile(file)
  }));
  
  // Calculate overall assessment
  const completenessScore = Math.round(
    analyzedFiles.reduce((sum, file) => sum + file.dataQuality.completeness, 0) / analyzedFiles.length
  );
  
  // Identify missing critical files
  const allMissingFiles = analyzedFiles.flatMap(file => file.missingFiles);
  const missingCriticalFiles = [...new Set(allMissingFiles)].slice(0, 5);
  
  // Recommend collection order based on priority and relevance
  const recommendedOrder = analyzedFiles
    .sort((a, b) => {
      const priorityScore = (file: typeof analyzedFiles[0]) => {
        let score = file.relevanceScore;
        if (file.processingPriority === 'High') score += 30;
        else if (file.processingPriority === 'Medium') score += 15;
        return score;
      };
      return priorityScore(b) - priorityScore(a);
    })
    .map(file => file.fileName);
  
  // Calculate total analysis time
  const totalMinutes = analyzedFiles.reduce((total, file) => {
    const timeStr = file.estimatedAnalysisTime;
    const maxTime = parseInt(timeStr.split('-')[1] || timeStr.split(' ')[0]) || 5;
    return total + maxTime;
  }, 0);
  
  const estimatedTotalTime = totalMinutes > 60 ? 
    `${Math.ceil(totalMinutes / 60)} hours` : 
    `${totalMinutes} minutes`;
  
  // Generate analysis flow
  const suggestedFlow = [
    'Process high-priority files first',
    'Analyze diagnostic packages for comprehensive overview',
    'Review log files for specific error patterns',
    'Validate configuration files against known issues',
    'Cross-reference findings across multiple files'
  ];
  
  return {
    files: analyzedFiles,
    overallAssessment: {
      completenessScore,
      missingCriticalFiles,
      recommendedCollectionOrder: recommendedOrder,
      estimatedTotalAnalysisTime: estimatedTotalTime
    },
    suggestedAnalysisFlow: suggestedFlow
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Handle batch analysis
    if (Array.isArray(body)) {
      const batchAnalysis = analyzeBatch(body);
      return NextResponse.json(batchAnalysis);
    }
    
    // Handle single file analysis
    const fileRequest: FileAnalysisRequest = body;
    
    // Validate required fields
    if (!fileRequest.fileName || !fileRequest.product) {
      return NextResponse.json(
        { error: 'fileName and product are required' },
        { status: 400 }
      );
    }
    
    const analysis = analyzeFile(fileRequest);
    return NextResponse.json(analysis);
    
  } catch (error) {
    console.error('Error analyzing file:', error);
    return NextResponse.json(
      { error: 'Failed to analyze file' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'File Analysis Service is running',
    capabilities: [
      'Intelligent file type classification',
      'Relevance scoring based on product and issue context',
      'Automated issue detection in file content',
      'Analyzer recommendation based on file characteristics',
      'Missing file identification for comprehensive analysis',
      'Processing priority determination',
      'Security risk assessment',
      'Data quality evaluation',
      'Batch analysis for multiple files'
    ],
    supportedFileTypes: [
      'Log files (.log, .txt)',
      'Configuration files (.cfg, .conf, .xml, .json)',
      'Diagnostic packages (.zip, .7z, archives)',
      'Screenshots and images (.png, .jpg, .gif)',
      'Documents (.pdf, .doc, .docx)',
      'Archive files (.zip, .rar, .tar.gz)',
      'System dumps and traces'
    ],
    analysisMetrics: [
      'Relevance Score (0-100) - How relevant file is to the reported issue',
      'Data Quality - Completeness, readability, and relevance assessment',
      'Processing Priority - High/Medium/Low based on potential value',
      'Security Risk - Assessment of potential security implications',
      'Estimated Analysis Time - Processing time prediction'
    ]
  });
}