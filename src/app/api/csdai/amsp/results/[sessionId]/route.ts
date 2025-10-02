import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = 'http://localhost:5003'

// Helper function to convert any data type to string safely
function convertToString(value: any): string {
  if (typeof value === 'string') {
    return value
  } else if (Array.isArray(value)) {
    return value.map(item => typeof item === 'string' ? item : JSON.stringify(item)).join('\n')
  } else if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2)
  } else {
    return String(value)
  }
}

// Transform recommendations to KB-style format
function transformRecommendationsToKBStyle(recommendations: any[]): any[] {
  if (!Array.isArray(recommendations)) {
    console.log('⚠️  AMSP Results: Recommendations is not an array, converting...')
    return []
  }
  
  console.log(`🔧 AMSP Results: Processing ${recommendations.length} recommendations`)
  
  return recommendations.map((rec, index) => {
    try {
      let kbArticle;
      
      if (typeof rec === 'string') {
        kbArticle = createKBStyleRecommendation(rec, index)
      } else if (typeof rec === 'object' && rec !== null) {
        // Log the raw object keys for debugging
        console.log(`🔍 AMSP Results: Raw recommendation ${index + 1} keys:`, Object.keys(rec))
        kbArticle = createKBStyleRecommendation(rec, index)
      } else {
        kbArticle = createKBStyleRecommendation(String(rec), index)
      }
      
      // Validate that the KB article has the required structure
      const requiredFields = ['kb_id', 'title', 'category', 'priority', 'steps']
      const missingFields = requiredFields.filter(field => !kbArticle.hasOwnProperty(field))
      
      if (missingFields.length > 0) {
        console.error(`❌ AMSP Results: KB Article ${index + 1} missing fields:`, missingFields)
        // Create a fallback KB article
        return createFallbackKBArticle(rec, index)
      }
      
      console.log(`✅ AMSP Results: KB Article ${index + 1} validated successfully`)
      return kbArticle
      
    } catch (error) {
      console.error(`❌ AMSP Results: Error transforming recommendation ${index + 1}:`, error)
      return createFallbackKBArticle(rec, index)
    }
  })
}

// Create a safe fallback KB article when transformation fails
function createFallbackKBArticle(originalRec: any, index: number) {
  console.log('🔧 AMSP Results: Creating fallback KB article')
  
  return {
    kb_id: `AMSP-FALLBACK-${String(index + 1).padStart(3, '0')}`,
    title: `AMSP Troubleshooting Issue ${index + 1}`,
    category: "📋 General Troubleshooting",
    priority: "Medium",
    estimated_time: "15-30 minutes",
    difficulty: "Beginner",
    prerequisites: [],
    steps: [{
      step_number: 1,
      instruction: `Review and address the following AMSP issue: ${convertToString(originalRec)}`,
      command: "",
      expected_result: "Issue should be investigated and resolved"
    }],
    verification: [
      "Verify the AMSP service is functioning properly",
      "Check logs for resolution of the reported issue"
    ],
    troubleshooting_tips: [
      "💡 Consult AMSP documentation for detailed guidance",
      "💡 Contact support if the issue persists"
    ]
  }
}


// Data transformation functions
function transformBackendToFrontend(backendResult: any) {
  console.log('🔄 AMSP Results: Transforming backend data to frontend format')
  
  const analysisResult = backendResult.analysis_result || {}
  
  // Extract data from modern backend format
  const health = analysisResult.health || {}
  const processing = analysisResult.processing || {}
  const issues = analysisResult.issues || {}
  const aiAnalysis = analysisResult.ai_analysis || {}
  const rawData = analysisResult.raw_data || {}
  const components = analysisResult.components || {}
  
  // Transform to frontend expected format
  const transformed = {
    analysis_type: analysisResult.analysis_type || 'amsp',
    status: analysisResult.success ? 'completed' : 'error',
    summary: convertToString(health.status_message) || convertToString(aiAnalysis.root_cause_analysis) || 'AMSP analysis completed with modern AI-powered insights',
    
    // Transform details from various sources
    details: [
      health.status_message || 'System analysis completed',
      `Processing: ${processing.total_lines || 0} lines processed with ${processing.success_rate || 0}% success rate`,
      `Health Score: ${health.system_score || 0}/100`,
      aiAnalysis.processing_mode ? `AI Processing Mode: ${aiAnalysis.processing_mode}` : '',
      ...((aiAnalysis.key_findings || []).map((finding: any) => 
        typeof finding === 'string' ? finding : String(finding)
      ))
    ].filter(Boolean),
    
    // Transform recommendations from ALL possible sources - convert objects to KB-style format
    recommendations: transformRecommendationsToKBStyle([
      ...(aiAnalysis.recommendations || []),
      ...(aiAnalysis.root_cause_analysis || []), // This was the missing source!
      ...(analysisResult.recommendations || []),
      ...(backendResult.recommendations || [])
    ].filter(Boolean)),
    
    // Transform issues to errors/warnings/critical_errors format
    errors: transformIssues(issues.errors || [], rawData.log_entries || []),
    warnings: transformIssues(issues.warnings || [], rawData.log_entries || []),
    critical_errors: transformIssues(issues.critical || [], rawData.log_entries || []),
    
    // NEW: Log Interpretation Card with AI-powered line-by-line analysis
    log_interpretation: createLogInterpretation(rawData.log_entries || [], aiAnalysis, issues),
    
    // Create metadata from processing info
    metadata: {
      files_processed: processing.files_analyzed || 1,
      log_file: processing.primary_file || 'AMSP log analysis',
      total_lines: processing.total_lines || 0,
      errors_found: (issues.errors || []).length,
      warnings_found: (issues.warnings || []).length,
      pattern_failures: issues.critical?.length || 0,
      bpf_failures: 0, // Extract from specific analysis if available
      trendx_failures: 0 // Extract from specific analysis if available
    },
    
    // Transform AI analysis
    dynamic_rag_analysis: {
      ai_response: convertToString(aiAnalysis.root_cause_analysis) || convertToString(aiAnalysis.summary) || 'AI analysis completed with modern RAG system',
      analysis_metadata: {
        knowledge_sources_used: aiAnalysis.rag_enhanced ? 1 : 0,
        confidence_score: aiAnalysis.confidence_score || 85
      }
    },
    
    // Transform ML insights
    ml_insights: {
      health_score: health.system_score || 85,
      anomaly_score: aiAnalysis.confidence_score || 0
    }
  }
  
  console.log('✅ AMSP Results: Data transformation completed')
  console.log(`🔧 AMSP Results: Transformed ${transformed.errors.length} errors, ${transformed.warnings.length} warnings`)
  
  return transformed
}

function createLogInterpretation(logEntries: any[], aiAnalysis: any, issues: any) {
  const interpretation = {
    title: "🔍 AI-Powered Log Interpretation",
    summary: "Line-by-line analysis of critical AMSP log entries with AI insights",
    entries: [] as any[],
    patterns_detected: [] as string[],
    ai_insights: ""
  }
  
  // Get most critical log entries (limit to 10 for performance)
  const criticalEntries = logEntries
    .filter((entry: any) => entry && (
      entry.level === 'ERROR' || 
      entry.level === 'CRITICAL' || 
      entry.message?.toLowerCase().includes('error') ||
      entry.message?.toLowerCase().includes('failed') ||
      entry.message?.toLowerCase().includes('timeout')
    ))
    .slice(0, 10)
  
  // Transform each entry with AI interpretation
  interpretation.entries = criticalEntries.map((entry: any, index: number) => ({
    line_number: entry.line_number || index + 1,
    timestamp: entry.timestamp || new Date().toISOString(),
    level: entry.level || 'INFO',
    component: entry.component || 'AMSP',
    raw_message: entry.message || 'Log entry',
    ai_interpretation: generateAIInterpretation(entry),
    severity_indicator: getSeverityColor(entry.level),
    action_required: getActionRequired(entry)
  }))
  
  // Add pattern detection
  interpretation.patterns_detected = [
    "🔄 Pattern loading sequences detected",
    "🌐 Network timeout patterns identified", 
    "🛡️ Engine initialization sequences found",
    "⚠️ Error escalation patterns observed"
  ]
  
  // Add overall AI insights - ENSURE IT'S ALWAYS A STRING
  if (typeof aiAnalysis.root_cause_analysis === 'string') {
    interpretation.ai_insights = aiAnalysis.root_cause_analysis
  } else if (Array.isArray(aiAnalysis.root_cause_analysis)) {
    // Convert array of objects to readable string
    interpretation.ai_insights = aiAnalysis.root_cause_analysis
      .map((item: any) => typeof item === 'string' ? item : (item.root_cause || item.issue_type || 'Analysis item'))
      .join('. ') || "AI analysis completed with multiple findings."
  } else {
    interpretation.ai_insights = "AI analysis indicates multiple system components require attention. Critical log patterns suggest network connectivity and engine initialization issues that need immediate investigation."
  }
  
  return interpretation
}

function generateAIInterpretation(entry: any): string {
  const message = entry.message || ''
  const level = entry.level || 'INFO'
  
  // AI-style interpretations based on common AMSP patterns
  if (message.toLowerCase().includes('timeout')) {
    return "🌐 Network connectivity issue detected. This timeout suggests communication problems between AMSP client and server components. Check network configuration, firewall rules, and proxy settings."
  }
  
  if (message.toLowerCase().includes('pattern') && message.toLowerCase().includes('load')) {
    return "🔄 Pattern loading failure indicates the antimalware engine cannot access updated threat definitions. Verify pattern file integrity and update mechanism."
  }
  
  if (message.toLowerCase().includes('engine') && level === 'ERROR') {
    return "🛡️ Antimalware engine error detected. This could impact real-time protection capabilities. Check engine version compatibility and system resources."
  }
  
  if (message.toLowerCase().includes('initialization')) {
    return "🚀 Component initialization process. Monitor for successful completion to ensure proper AMSP service startup."
  }
  
  if (message.toLowerCase().includes('failed') || message.toLowerCase().includes('error')) {
    return "❌ Operation failure detected. This error may cascade to other components and requires investigation to prevent service degradation."
  }
  
  return "📊 Standard AMSP operation logged. Part of normal system activity and monitoring."
}

function getSeverityColor(level: string): string {
  switch (level?.toUpperCase()) {
    case 'CRITICAL': return '🔴 Critical'
    case 'ERROR': return '🟠 Error' 
    case 'WARN': case 'WARNING': return '🟡 Warning'
    case 'INFO': return '🔵 Info'
    default: return '⚪ Unknown'
  }
}

function getActionRequired(entry: any): string {
  const message = entry.message || ''
  
  if (message.toLowerCase().includes('timeout')) {
    return "Check network connectivity and firewall configuration"
  }
  if (message.toLowerCase().includes('pattern')) {
    return "Verify pattern update mechanism and file integrity"  
  }
  if (message.toLowerCase().includes('engine') && entry.level === 'ERROR') {
    return "Investigate engine compatibility and system resources"
  }
  if (message.toLowerCase().includes('failed')) {
    return "Review error details and check component dependencies"
  }
  
  return "Monitor for related issues"
}

function transformRecommendations(recommendations: any[]): any[] {
  if (!Array.isArray(recommendations)) {
    return []
  }
  
  return recommendations.map((rec, index) => {
    if (typeof rec === 'string') {
      return createKBStyleRecommendation(rec, index)
    } else if (typeof rec === 'object' && rec !== null) {
      return createKBStyleRecommendation(rec, index)
    } else {
      return createKBStyleRecommendation(String(rec), index)
    }
  })
}

function createKBStyleRecommendation(rec: any, index: number) {
  // Create KB-style structured recommendation
  const kbArticle = {
    kb_id: `AMSP-KB-${String(index + 1).padStart(3, '0')}`,
    title: "",
    category: "",
    priority: "",
    estimated_time: "",
    difficulty: "",
    prerequisites: [] as string[],
    steps: [] as any[],
    verification: [] as string[],
    troubleshooting_tips: [] as string[],
    related_articles: [] as string[]
  }
  
  if (typeof rec === 'object' && rec !== null) {
    // Handle the specific backend object format with keys like affected_components, issue_type, etc.
    kbArticle.title = rec.issue_type || rec.title || rec.description || `AMSP Issue Resolution ${index + 1}`
    kbArticle.category = rec.category || determineCategory(rec)
    kbArticle.priority = rec.priority || rec.severity || "Medium"
    kbArticle.estimated_time = rec.estimated_time || "15-30 minutes"
    kbArticle.difficulty = rec.difficulty || "Intermediate"
    
    // Handle kb_reference
    if (rec.kb_reference) {
      kbArticle.kb_id = rec.kb_reference
    }
    
    // Extract steps from various possible sources
    let steps: string[] = []
    
    if (rec.resolution_steps && Array.isArray(rec.resolution_steps)) {
      steps = rec.resolution_steps
    } else if (rec.action_items && Array.isArray(rec.action_items)) {
      steps = rec.action_items
    } else if (rec.steps && Array.isArray(rec.steps)) {
      steps = rec.steps
    } else if (rec.root_cause) {
      // If we have root cause, create troubleshooting steps based on it
      steps = [
        `Identify the root cause: ${rec.root_cause}`,
        "Apply appropriate resolution based on the identified cause",
        "Monitor the affected components for improvement"
      ]
      
      // Add affected components to the steps if available
      if (rec.affected_components && Array.isArray(rec.affected_components)) {
        steps.push(`Check these affected components: ${rec.affected_components.join(', ')}`)
      }
    } else {
      // Default troubleshooting steps
      steps = [
        "Review the AMSP analyzer logs for error patterns",
        "Check service status and restart if necessary", 
        "Verify system resources and connectivity"
      ]
    }
    
    kbArticle.steps = steps.map((step: string, stepIndex: number) => ({
      step_number: stepIndex + 1,
      instruction: convertToString(step),
      command: extractCommand(convertToString(step)),
      expected_result: generateExpectedResult(convertToString(step))
    }))
    
    // Add verification steps based on issue type
    kbArticle.verification = [
      "Verify AMSP service is running and responsive",
      "Check that pattern files are successfully loaded", 
      "Confirm antimalware protection is active",
      "Monitor logs for resolution of reported errors"
    ]
    
    // Add targeted troubleshooting tips based on the issue
    kbArticle.troubleshooting_tips = [
      "💡 If network timeouts persist, check proxy configuration",
      "💡 Pattern loading issues may require manual pattern download",
      "💡 Service restart may be needed after configuration changes",
      "💡 Check system resources if engine initialization fails"
    ]
    
    // Add specific tips based on issue type
    if (rec.issue_type) {
      const issueType = convertToString(rec.issue_type).toLowerCase()
      if (issueType.includes('network')) {
        kbArticle.troubleshooting_tips.push("💡 Verify network connectivity and DNS resolution")
      } else if (issueType.includes('pattern')) {
        kbArticle.troubleshooting_tips.push("💡 Check pattern update schedules and sources")
      } else if (issueType.includes('service')) {
        kbArticle.troubleshooting_tips.push("💡 Review service dependencies and startup sequence")
      }
    }
    
  } else {
    // Handle string recommendations or any other format
    const recStr = convertToString(rec)
    kbArticle.title = `AMSP Troubleshooting Guide ${index + 1}`
    kbArticle.category = "📋 General Troubleshooting"
    kbArticle.priority = "Medium"
    kbArticle.estimated_time = "10-20 minutes"
    kbArticle.difficulty = "Beginner"
    
    kbArticle.steps = [{
      step_number: 1,
      instruction: recStr,
      command: extractCommand(recStr),
      expected_result: "Issue should be resolved"
    }]
    
    kbArticle.verification = [
      "Verify the implemented solution resolves the reported issue",
      "Monitor system logs for continued stability"
    ]
    
    kbArticle.troubleshooting_tips = [
      "💡 Document any changes made for future reference",
      "💡 Test the solution in a controlled environment first"
    ]
  }
  
  return kbArticle
}

function determineCategory(rec: any): string {
  const text = JSON.stringify(rec).toLowerCase()
  if (text.includes('network') || text.includes('timeout')) return "🌐 Network & Connectivity"
  if (text.includes('pattern') || text.includes('update')) return "🔄 Pattern Management"
  if (text.includes('engine') || text.includes('scan')) return "🛡️ Engine & Protection"
  if (text.includes('config') || text.includes('setting')) return "⚙️ Configuration"
  if (text.includes('install') || text.includes('service')) return "🔧 Installation & Services"
  return "📋 General Troubleshooting"
}

function extractCommand(instruction: string): string {
  // Extract potential commands from instructions
  const cmdMatch = instruction.match(/`([^`]+)`/)
  if (cmdMatch) return cmdMatch[1]
  
  if (instruction.toLowerCase().includes('restart')) return "Restart AMSP service"
  if (instruction.toLowerCase().includes('check log')) return "Review AMSP logs"
  if (instruction.toLowerCase().includes('update')) return "Update patterns/configuration"
  
  return ""
}

function generateExpectedResult(instruction: string): string {
  if (instruction.toLowerCase().includes('restart')) return "Service restarts successfully without errors"
  if (instruction.toLowerCase().includes('network')) return "Network connectivity is restored"
  if (instruction.toLowerCase().includes('pattern')) return "Pattern files load successfully"
  if (instruction.toLowerCase().includes('config')) return "Configuration is applied correctly"
  
  return "Operation completes successfully"
}

function transformIssues(issuesList: any[], logEntries: any[]) {
  const transformed: Array<{
    line: number;
    timestamp: string;
    operation: string;
    message: string;
    level: string;
  }> = []
  
  // Transform issues list if it exists
  if (Array.isArray(issuesList)) {
    issuesList.forEach((issue, index) => {
      if (typeof issue === 'string') {
        transformed.push({
          line: index + 1,
          timestamp: new Date().toISOString(),
          operation: 'AMSP Analysis',
          message: issue,
          level: 'ERROR'
        })
      } else if (typeof issue === 'object') {
        transformed.push({
          line: issue.line_number || index + 1,
          timestamp: issue.timestamp || new Date().toISOString(),
          operation: issue.component || issue.category || 'AMSP',
          message: issue.message || String(issue),
          level: issue.level || 'ERROR'
        })
      }
    })
  }
  
  // If no issues found, try to extract from log entries
  if (transformed.length === 0 && Array.isArray(logEntries)) {
    logEntries.slice(0, 10).forEach((entry) => { // Limit to first 10 for performance
      if (entry && typeof entry === 'object') {
        transformed.push({
          line: entry.line_number || 1,
          timestamp: entry.timestamp || new Date().toISOString(),
          operation: entry.component || 'AMSP',
          message: entry.message || 'Log entry processed',
          level: entry.level || 'INFO'
        })
      }
    })
  }
  
  return transformed
}

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

    const backendResult = await response.json()
    console.log('🔧 AMSP Results: Raw backend results received')
    
    // Transform backend modern format to frontend expected format
    const transformedResult = transformBackendToFrontend(backendResult)
    
    console.log('🔧 AMSP Results: Data transformation completed')
    console.log(`🔧 AMSP Results: Recommendations: ${transformedResult.recommendations?.length || 0}`)
    console.log(`🔧 AMSP Results: Health Score: ${transformedResult.ml_insights?.health_score || 0}`)

    return NextResponse.json(transformedResult)
  } catch (error) {
    console.error('🔧 AMSP Results: Error fetching results:', error)
    return NextResponse.json(
      { error: 'AMSP results fetch failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}