import { NextRequest, NextResponse } from 'next/server';

interface DescriptionAnalysisRequest {
  description: string;
  product: string;
  category: string;
  severity?: string;
  currentTitle?: string;
  caseTitle?: string; // Add caseTitle field
}

interface QualityAssessment {
  overallScore: number; // 0-100
  completeness: {
    basicInfo: number;
    technicalDetails: number;
    reproductionSteps: number;
    environmentInfo: number;
    errorMessages: number;
  };
  suggestions: QualityImprovement[];
  readinessForSubmission: boolean;
  estimatedResolutionTime?: string;
  confidenceLevel: number;
}

interface QualityImprovement {
  area: string;
  suggestion: string;
  impact: 'High' | 'Medium' | 'Low';
  exampleText?: string;
  priority: number;
}

// Advanced AI-powered description analysis
function analyzeDescriptionQuality(request: DescriptionAnalysisRequest): QualityAssessment {
  const { description, product, category, severity, caseTitle } = request;
  
  if (!description || description.trim().length < 10) {
    return {
      overallScore: 0,
      completeness: {
        basicInfo: 0,
        technicalDetails: 0,
        reproductionSteps: 0,
        environmentInfo: 0,
        errorMessages: 0
      },
      suggestions: [{
        area: 'Description Length',
        suggestion: 'Please provide a more detailed description of the issue (minimum 50 characters)',
        impact: 'High',
        priority: 1,
        exampleText: 'Example: "Deep Security Agent service fails to start after Windows update, showing error code 1053 in Event Viewer. This happens consistently on all 5 Windows Server 2019 machines in our environment."'
      }],
      readinessForSubmission: false,
      confidenceLevel: 100
    };
  }

  const descriptionLower = description.toLowerCase();
  const wordCount = description.split(' ').length;
  
  // Analyze completeness dimensions
  const basicInfo = analyzeBasicInfo(descriptionLower, product);
  const technicalDetails = analyzeTechnicalDetails(descriptionLower);
  const reproductionSteps = analyzeReproductionSteps(descriptionLower);
  const environmentInfo = analyzeEnvironmentInfo(descriptionLower);
  const errorMessages = analyzeErrorMessages(descriptionLower);
  
  // Calculate weighted overall score
  const weights = {
    basicInfo: 0.25,
    technicalDetails: 0.25,
    reproductionSteps: 0.20,
    environmentInfo: 0.15,
    errorMessages: 0.15
  };
  
  const overallScore = Math.round(
    basicInfo * weights.basicInfo +
    technicalDetails * weights.technicalDetails +
    reproductionSteps * weights.reproductionSteps +
    environmentInfo * weights.environmentInfo +
    errorMessages * weights.errorMessages
  );
  
  // Generate improvement suggestions
  const suggestions = generateImprovementSuggestions({
    basicInfo,
    technicalDetails,
    reproductionSteps,
    environmentInfo,
    errorMessages,
    description,
    product,
    category,
    wordCount
  }, caseTitle);
  
  // Estimate resolution time based on quality and complexity
  const estimatedResolutionTime = estimateResolutionTime(overallScore, category, severity);
  
  return {
    overallScore,
    completeness: {
      basicInfo,
      technicalDetails,
      reproductionSteps,
      environmentInfo,
      errorMessages
    },
    suggestions,
    readinessForSubmission: overallScore >= 70,
    estimatedResolutionTime,
    confidenceLevel: calculateConfidenceLevel(description, overallScore)
  };
}

function analyzeBasicInfo(description: string, product: string): number {
  let score = 40; // Base score for having some description
  
  // Check for clear problem statement
  const problemIndicators = ['issue', 'problem', 'error', 'fail', 'not work', 'unable', 'cannot', 'trouble'];
  if (problemIndicators.some(indicator => description.includes(indicator))) {
    score += 20;
  }
  
  // Check for impact statement
  const impactIndicators = ['affect', 'impact', 'prevent', 'slow', 'down', 'performance', 'critical'];
  if (impactIndicators.some(indicator => description.includes(indicator))) {
    score += 20;
  }
  
  // Check for specific product component mention
  const dsComponents = ['agent', 'manager', 'relay', 'amsp', 'dsa', 'dsm', 'console'];
  const v1Components = ['endpoint sensor', 'connector', 'workbench', 'api'];
  const apexComponents = ['security agent', 'scan engine', 'web console'];
  
  let components: string[] = [];
  if (product.toLowerCase().includes('deep security')) components = dsComponents;
  else if (product.toLowerCase().includes('vision one')) components = v1Components;
  else if (product.toLowerCase().includes('apex')) components = apexComponents;
  
  if (components.some(comp => description.includes(comp))) {
    score += 20;
  }
  
  return Math.min(score, 100);
}

function analyzeTechnicalDetails(description: string): number {
  let score = 0;
  
  // Version information
  const versionPatterns = [
    /\d+\.\d+(\.\d+)?(\.\d+)?/,
    /version\s+\d+/i,
    /v\d+\.\d+/i,
    /build\s+\d+/i
  ];
  if (versionPatterns.some(pattern => pattern.test(description))) {
    score += 25;
  }
  
  // Operating system information
  const osIndicators = ['windows', 'linux', 'centos', 'rhel', 'ubuntu', 'server 2019', 'server 2016'];
  if (osIndicators.some(os => description.includes(os))) {
    score += 20;
  }
  
  // Error codes or specific technical identifiers
  const technicalPatterns = [
    /error\s*\d+/i,
    /code\s*\d+/i,
    /\b\d{3,5}\b/,
    /event\s*id\s*\d+/i,
    /0x[0-9a-f]+/i
  ];
  if (technicalPatterns.some(pattern => pattern.test(description))) {
    score += 25;
  }
  
  // Configuration details
  const configIndicators = ['config', 'setting', 'parameter', 'policy', 'rule'];
  if (configIndicators.some(config => description.includes(config))) {
    score += 15;
  }
  
  // Log file mentions
  const logIndicators = ['log', 'event viewer', 'syslog', 'diagnostic'];
  if (logIndicators.some(log => description.includes(log))) {
    score += 15;
  }
  
  return Math.min(score, 100);
}

function analyzeReproductionSteps(description: string): number {
  let score = 0;
  
  // Step indicators
  const stepIndicators = ['step', 'first', 'then', 'next', 'after', 'when', 'reproduce'];
  if (stepIndicators.some(step => description.includes(step))) {
    score += 30;
  }
  
  // Sequential numbering
  const sequentialPatterns = [
    /\b1[\.\)]\s/,
    /\b2[\.\)]\s/,
    /first/i,
    /second/i,
    /third/i
  ];
  if (sequentialPatterns.some(pattern => pattern.test(description))) {
    score += 35;
  }
  
  // Timing information
  const timingIndicators = ['always', 'sometimes', 'intermittent', 'consistently', 'randomly', 'daily', 'hourly'];
  if (timingIndicators.some(timing => description.includes(timing))) {
    score += 20;
  }
  
  // Conditions or triggers
  const triggerIndicators = ['when', 'if', 'after', 'during', 'before', 'trigger'];
  if (triggerIndicators.some(trigger => description.includes(trigger))) {
    score += 15;
  }
  
  return Math.min(score, 100);
}

function analyzeEnvironmentInfo(description: string): number {
  let score = 0;
  
  // Infrastructure details
  const infraIndicators = ['server', 'client', 'vm', 'virtual', 'physical', 'cloud', 'aws', 'azure'];
  if (infraIndicators.some(infra => description.includes(infra))) {
    score += 25;
  }
  
  // Network information
  const networkIndicators = ['network', 'firewall', 'port', 'connection', 'proxy', 'dns'];
  if (networkIndicators.some(network => description.includes(network))) {
    score += 20;
  }
  
  // Scale/quantity information
  const scalePatterns = [
    /\d+\s+(server|client|machine|computer|system)/i,
    /multiple/i,
    /all\s+\d+/i,
    /several/i
  ];
  if (scalePatterns.some(pattern => pattern.test(description))) {
    score += 25;
  }
  
  // Environment type
  const envTypes = ['production', 'test', 'staging', 'development', 'lab'];
  if (envTypes.some(env => description.includes(env))) {
    score += 15;
  }
  
  // Architecture details
  const archIndicators = ['x64', '32-bit', '64-bit', 'architecture'];
  if (archIndicators.some(arch => description.includes(arch))) {
    score += 15;
  }
  
  return Math.min(score, 100);
}

function analyzeErrorMessages(description: string): number {
  let score = 0;
  
  // Explicit error messages
  if (description.includes('"') || description.includes("'")) {
    score += 40;
  }
  
  // Error keywords
  const errorKeywords = ['error', 'failed', 'failure', 'exception', 'timeout', 'denied', 'refused'];
  if (errorKeywords.some(error => description.includes(error))) {
    score += 30;
  }
  
  // Specific error patterns
  const errorPatterns = [
    /error\s*:\s*[a-z]/i,
    /failed\s*:\s*[a-z]/i,
    /exception\s*:\s*[a-z]/i,
    /message\s*:\s*[a-z]/i
  ];
  if (errorPatterns.some(pattern => pattern.test(description))) {
    score += 30;
  }
  
  return Math.min(score, 100);
}

interface AnalysisMetrics {
  basicInfo: number;
  technicalDetails: number;
  reproductionSteps: number;
  environmentInfo: number;
  errorMessages: number;
  description: string;
  product: string;
  category: string;
  wordCount: number;
}

function generateImprovementSuggestions(analysis: AnalysisMetrics, caseTitle?: string): QualityImprovement[] {
  const suggestions: QualityImprovement[] = [];
  
  // Generate contextually relevant examples based on case title
  const getContextualExample = (area: string): string => {
    if (!caseTitle) {
      return getDefaultExample(area);
    }
    
    const titleLower = caseTitle.toLowerCase();
    
    // Performance-related titles
    if (titleLower.includes('performance') || titleLower.includes('cpu') || titleLower.includes('memory') || titleLower.includes('slow')) {
      switch (area) {
        case 'Problem Description':
          return 'Example: "System performance degraded significantly after recent update, with CPU usage consistently above 80% and slow response times affecting user productivity."';
        case 'Technical Details':
          return 'Example: "CPU usage peaked at 95% for 2+ hours, 16GB RAM showing 90% utilization, Task Manager shows high resource consumption by security processes."';
        case 'Reproduction Steps':
          return 'Steps: 1. System starts normally 2. After 30 minutes of operation 3. CPU usage gradually increases 4. Performance becomes noticeably slow 5. Issue persists until reboot';
        case 'Environment Details':
          return 'Environment: Production server with 8-core Intel Xeon, 16GB RAM, Windows Server 2019, hosting critical business applications';
        case 'Error Messages':
          return 'Performance Monitor alerts: "High CPU Usage detected", Event ID 2004: "Resource threshold exceeded for extended period"';
      }
    }
    
    // Offline/Connectivity-related titles
    if (titleLower.includes('offline') || titleLower.includes('connectivity') || titleLower.includes('not reporting') || titleLower.includes('connection')) {
      switch (area) {
        case 'Problem Description':
          return 'Example: "Agents appear offline in management console and are not receiving policy updates, affecting security coverage across the infrastructure."';
        case 'Technical Details':
          return 'Example: "25 agents showing offline status since yesterday 3 PM, network connectivity normal, firewall rules unchanged, agents can ping management server."';
        case 'Reproduction Steps':
          return 'Steps: 1. Agents were online and reporting normally 2. Around 3 PM all agents went offline simultaneously 3. Management console shows "Last Contact: 24 hours ago" 4. Manual agent restart temporarily resolves but issue returns';
        case 'Environment Details':
          return 'Environment: Corporate network with 25 endpoints, Windows 10/11 workstations, centrally managed through corporate VLAN, no recent network changes';
        case 'Error Messages':
          return 'Agent logs show: "Failed to connect to management server", "Heartbeat timeout", "SSL handshake failed with manager.company.com:4119"';
      }
    }
    
    // Installation/Configuration issues
    if (titleLower.includes('installation') || titleLower.includes('install') || titleLower.includes('configuration') || titleLower.includes('setup')) {
      switch (area) {
        case 'Problem Description':
          return 'Example: "Installation process fails at 80% completion with generic error message, preventing deployment across planned infrastructure."';
        case 'Technical Details':
          return 'Example: "Installation wizard stops during component registration phase, Windows Installer logs show MSI error 1603, occurs on Windows Server 2019 Standard Edition."';
        case 'Reproduction Steps':
          return 'Steps: 1. Download installer from customer portal 2. Run as Administrator 3. Follow installation wizard 4. Process reaches 80% 5. Error appears and installation rolls back';
        case 'Environment Details':
          return 'Environment: Fresh Windows Server 2019 installation, domain-joined, local administrator rights, no conflicting security software detected';
        case 'Error Messages':
          return 'Installer error: "Installation package corrupt or incomplete", MSI log shows: "Error 1603: Fatal error during installation"';
      }
    }
    
    // Default to general examples if no specific pattern matches
    return getDefaultExample(area);
  };
  
  const getDefaultExample = (area: string): string => {
    switch (area) {
      case 'Problem Description':
        return 'Example: "Service fails to start automatically after system reboot, requiring manual intervention and impacting business operations."';
      case 'Technical Details':
        return 'Example: "Version 20.0.1.2345 on Windows Server 2019 (build 17763), error code 4118 in Application Event Log"';
      case 'Reproduction Steps':
        return 'Steps: 1. System reboots 2. Service attempts to start 3. Startup fails with timeout 4. Manual service start succeeds 5. Issue repeats on next reboot';
      case 'Environment Details':
        return 'Environment: Production environment with VMware vSphere 7.0, corporate domain, standard security policies applied';
      case 'Error Messages':
        return 'Event Log Error: "Service failed to start due to timeout or dependency failure", Service Control Manager Event ID 7009';
      default:
        return 'Please provide specific details relevant to your issue';
    }
  };
  
  
  if (analysis.basicInfo < 70) {
    suggestions.push({
      area: 'Problem Description',
      suggestion: 'Provide a clearer description of what exactly is not working and how it impacts your operations',
      impact: 'High',
      priority: 1,
      exampleText: getContextualExample('Problem Description')
    });
  }
  
  if (analysis.technicalDetails < 70) {
    suggestions.push({
      area: 'Technical Details',
      suggestion: 'Include specific version numbers, operating system details, and any error codes you\'ve observed',
      impact: 'High',
      priority: 2,
      exampleText: getContextualExample('Technical Details')
    });
  }
  
  if (analysis.reproductionSteps < 70) {
    suggestions.push({
      area: 'Reproduction Steps',
      suggestion: 'Describe the exact steps that lead to the issue, including when it occurs and how consistently',
      impact: 'Medium',
      priority: 3,
      exampleText: getContextualExample('Reproduction Steps')
    });
  }
  
  if (analysis.environmentInfo < 70) {
    suggestions.push({
      area: 'Environment Details',
      suggestion: 'Include information about your infrastructure setup, number of affected systems, and environment type',
      impact: 'Medium',
      priority: 4,
      exampleText: getContextualExample('Environment Details')
    });
  }
  
  if (analysis.errorMessages < 70) {
    suggestions.push({
      area: 'Error Messages',
      suggestion: 'Include exact error messages, event log entries, or alert notifications you\'ve received',
      impact: 'Medium',
      priority: 5,
      exampleText: getContextualExample('Error Messages')
    });
  }
  
  if (analysis.wordCount < 50) {
    suggestions.push({
      area: 'Description Length',
      suggestion: 'Provide more detailed information to help our support team understand and resolve your issue faster',
      impact: 'High',
      priority: 1
    });
  }
  
  return suggestions.sort((a, b) => a.priority - b.priority).slice(0, 3); // Return top 3 suggestions
}

function estimateResolutionTime(score: number, category: string, severity?: string): string {
  let baseTime = 24; // hours
  
  // Adjust based on category
  switch (category.toLowerCase()) {
    case 'product issue':
      baseTime = 48;
      break;
    case 'how to':
      baseTime = 8;
      break;
    case 'feature request':
      baseTime = 72;
      break;
    default:
      baseTime = 24;
  }
  
  // Adjust based on severity
  switch (severity?.toLowerCase()) {
    case 'critical':
      baseTime *= 0.5;
      break;
    case 'high':
      baseTime *= 0.75;
      break;
    case 'low':
      baseTime *= 1.5;
      break;
  }
  
  // Adjust based on case quality
  if (score >= 90) baseTime *= 0.7;
  else if (score >= 80) baseTime *= 0.8;
  else if (score >= 70) baseTime *= 0.9;
  else if (score < 50) baseTime *= 1.5;
  
  if (baseTime <= 8) return 'Same day';
  if (baseTime <= 24) return '1 business day';
  if (baseTime <= 48) return '2-3 business days';
  if (baseTime <= 72) return '3-5 business days';
  return '5+ business days';
}

function calculateConfidenceLevel(description: string, score: number): number {
  const length = description.length;
  let confidence = 50;
  
  if (length > 200) confidence += 20;
  else if (length > 100) confidence += 10;
  
  if (score >= 80) confidence += 30;
  else if (score >= 60) confidence += 20;
  else if (score >= 40) confidence += 10;
  
  return Math.min(confidence, 100);
}

// Enhanced Claude AI integration (when API key is available)
async function enhanceWithClaude(assessment: QualityAssessment, request: DescriptionAnalysisRequest): Promise<QualityAssessment> {
  const claudeApiKey = process.env.OPENAI_API_KEY;
  
  if (!claudeApiKey) {
    return assessment; // Return original assessment if no Claude API key
  }
  
  try {
    const prompt = `Analyze this technical support case description for quality and completeness:

Product: ${request.product}
Category: ${request.category}
Severity: ${request.severity || 'Not specified'}
Description: "${request.description}"

Current AI Assessment Score: ${assessment.overallScore}/100

Please provide:
1. Enhanced quality assessment with specific technical insights
2. Additional improvement suggestions specific to ${request.product}
3. Potential root cause analysis hints
4. Recommended troubleshooting approach

Respond in JSON format matching the QualityAssessment interface.`;

    const response = await fetch(process.env.OPENAI_BASE_URL || 'https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${claudeApiKey}`,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'claude-4-sonnet',
        max_tokens: 1500,
        messages: [{
          role: 'user',
          content: prompt
        }]
      })
    });
    
    if (response.ok) {
      const claudeResult = await response.json();
      const enhancedAnalysis = JSON.parse(claudeResult.content[0].text);
      
      // Merge Claude insights with local analysis
      return {
        ...assessment,
        overallScore: Math.max(assessment.overallScore, enhancedAnalysis.overallScore || assessment.overallScore),
        suggestions: [
          ...assessment.suggestions,
          ...(enhancedAnalysis.suggestions || []).slice(0, 2)
        ].slice(0, 5),
        confidenceLevel: 95 // Higher confidence with Claude enhancement
      };
    }
  } catch {
    console.log('Claude enhancement not available, using local analysis');
  }
  
  return assessment;
}

export async function POST(request: NextRequest) {
  try {
    const body: DescriptionAnalysisRequest = await request.json();
    
    // Validate required fields
    if (!body.description || !body.product || !body.category) {
      return NextResponse.json(
        { error: 'Description, product, and category are required' },
        { status: 400 }
      );
    }
    
    // Generate quality assessment
    let assessment = analyzeDescriptionQuality(body);
    
    // Enhance with Claude if available
    assessment = await enhanceWithClaude(assessment, body);
    
    return NextResponse.json(assessment);
    
  } catch (error) {
    console.error('Error analyzing description quality:', error);
    return NextResponse.json(
      { error: 'Failed to analyze description quality' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Description Quality Analysis Service is running',
    capabilities: [
      'Multi-dimensional quality assessment',
      'Real-time improvement suggestions',
      'Technical completeness scoring',
      'Resolution time estimation',
      'Claude AI enhancement (when available)',
      'Product-specific analysis'
    ],
    qualityDimensions: [
      'Basic Information (25%)',
      'Technical Details (25%)',
      'Reproduction Steps (20%)',
      'Environment Information (15%)',
      'Error Messages (15%)'
    ]
  });
}