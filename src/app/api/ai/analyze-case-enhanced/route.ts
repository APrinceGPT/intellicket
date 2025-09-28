import { NextRequest, NextResponse } from 'next/server';

interface EnhancedCaseAnalysisRequest {
  description: string;
  caseTitle?: string;
  product: string;
  category: string;
  severity?: string;
  attachmentCount?: number;
  attachmentTypes?: string[];
  businessImpact?: string;
  affectedUsers?: string;
}

interface AnalyzerRecommendation {
  analyzerId: string;
  analyzerName: string;
  confidence: number;
  reasoning: string;
  icon: string;
  priority: number;
  estimatedAnalysisTime: string;
  requiredFiles?: string[];
}

interface CaseComplexityAnalysis {
  level: 'Simple' | 'Moderate' | 'Complex' | 'Expert-Level';
  factors: string[];
  estimatedResolutionTime: string;
  requiredExpertise: string[];
  similarCasePatterns: string[];
}

interface EnhancedCaseAnalysis {
  analyzerRecommendations: AnalyzerRecommendation[];
  caseComplexity: CaseComplexityAnalysis;
  requiredInformation: string[];
  suggestedActions: string[];
  potentialRootCauses: string[];
  troubleshootingPriority: string[];
  knowledgeBaseReferences: string[];
  escalationTriggers: string[];
}

// Comprehensive AI-powered case analysis
function analyzeCase(request: EnhancedCaseAnalysisRequest): EnhancedCaseAnalysis {
  const { description, product, category, severity, attachmentCount = 0, attachmentTypes = [] } = request;
  
  if (!description || description.trim().length < 10) {
    return {
      analyzerRecommendations: [],
      caseComplexity: {
        level: 'Simple',
        factors: ['Insufficient information provided'],
        estimatedResolutionTime: 'Cannot estimate without details',
        requiredExpertise: ['Basic technical knowledge'],
        similarCasePatterns: []
      },
      requiredInformation: ['Detailed problem description', 'Environment details', 'Reproduction steps'],
      suggestedActions: ['Provide more detailed description', 'Include error messages', 'Add system information'],
      potentialRootCauses: [],
      troubleshootingPriority: [],
      knowledgeBaseReferences: [],
      escalationTriggers: ['Insufficient information for analysis']
    };
  }
  
  const descriptionLower = description.toLowerCase();
  
  // Analyze for appropriate analyzers
  const analyzerRecommendations = getAnalyzerRecommendations(descriptionLower, product, category, attachmentTypes);
  
  // Assess case complexity
  const caseComplexity = assessCaseComplexity(descriptionLower, product, category, severity);
  
  // Identify missing information
  const requiredInformation = identifyRequiredInformation(descriptionLower, product, attachmentCount);
  
  // Generate suggested actions
  const suggestedActions = generateSuggestedActions(descriptionLower, product, category, analyzerRecommendations);
  
  // Analyze potential root causes
  const potentialRootCauses = analyzePotentialRootCauses(descriptionLower, product);
  
  // Prioritize troubleshooting steps
  const troubleshootingPriority = prioritizeTroubleshooting(descriptionLower, product, caseComplexity);
  
  // Find relevant knowledge base references
  const knowledgeBaseReferences = findKnowledgeBaseReferences(descriptionLower, product, category);
  
  // Identify escalation triggers
  const escalationTriggers = identifyEscalationTriggers(descriptionLower, severity, caseComplexity);
  
  return {
    analyzerRecommendations,
    caseComplexity,
    requiredInformation,
    suggestedActions,
    potentialRootCauses,
    troubleshootingPriority,
    knowledgeBaseReferences,
    escalationTriggers
  };
}

function getAnalyzerRecommendations(description: string, product: string, category: string, attachmentTypes: string[]): AnalyzerRecommendation[] {
  const recommendations: AnalyzerRecommendation[] = [];
  
  // Deep Security specific analyzers
  if (product.toLowerCase().includes('deep security')) {
    
    // AMSP Analyzer
    if (description.includes('amsp') || description.includes('anti-malware') || 
        description.includes('scan') || description.includes('malware')) {
      recommendations.push({
        analyzerId: 'amsp_analyzer',
        analyzerName: 'AMSP Performance Analyzer',
        confidence: 0.92,
        reasoning: 'Description mentions AMSP/anti-malware components or scanning issues',
        icon: '🛡️',
        priority: 1,
        estimatedAnalysisTime: '5-10 minutes',
        requiredFiles: ['AMSP logs', 'Diagnostic package', 'Performance counters']
      });
    }
    
    // Conflict Analyzer
    if (description.includes('conflict') || description.includes('incompatible') ||
        description.includes('third party') || description.includes('antivirus')) {
      recommendations.push({
        analyzerId: 'conflict_analyzer', 
        analyzerName: 'Conflict Detection Analyzer',
        confidence: 0.88,
        reasoning: 'Potential software conflicts or compatibility issues detected',
        icon: '⚠️',
        priority: 1,
        estimatedAnalysisTime: '3-7 minutes',
        requiredFiles: ['System logs', 'Installed software list', 'DS Agent logs']
      });
    }
    
    // Resource Analyzer
    if (description.includes('performance') || description.includes('slow') ||
        description.includes('cpu') || description.includes('memory') ||
        description.includes('disk') || description.includes('resource')) {
      recommendations.push({
        analyzerId: 'resource_analyzer',
        analyzerName: 'Resource Usage Analyzer',
        confidence: 0.85,
        reasoning: 'Performance or resource utilization issues identified',
        icon: '📊',
        priority: 2,
        estimatedAnalysisTime: '7-12 minutes',
        requiredFiles: ['Performance logs', 'System resource data', 'Process monitor logs']
      });
    }
    
    // DS Agent Log Analyzer - REMOVED FROM FRONTEND
    // DS Agent Log analysis is handled backend-only
    
    // DS Agent Offline Analyzer
    if (description.includes('offline') || description.includes('heartbeat') ||
        description.includes('not reporting') || description.includes('disconnect')) {
      recommendations.push({
        analyzerId: 'ds_agent_offline_analyzer',
        analyzerName: 'DS Agent Offline Diagnosis',
        confidence: 0.87,
        reasoning: 'Agent offline or reporting issues identified',
        icon: '📡',
        priority: 1,
        estimatedAnalysisTime: '5-9 minutes',
        requiredFiles: ['Agent status logs', 'Network diagnostics', 'Heartbeat logs']
      });
    }
    
    // Diagnostic Package Analyzer
    if (attachmentTypes.includes('application/zip') || 
        attachmentTypes.includes('application/x-zip-compressed') ||
        description.includes('diagnostic') || description.includes('support package')) {
      recommendations.push({
        analyzerId: 'diagnostic_package_analyzer',
        analyzerName: 'Comprehensive Diagnostic Analyzer',
        confidence: 0.95,
        reasoning: 'Diagnostic package or comprehensive logs available for analysis',
        icon: '🔍',
        priority: 1,
        estimatedAnalysisTime: '10-15 minutes',
        requiredFiles: ['Complete diagnostic package']
      });
    }
  }
  
  // Vision One specific analyzers
  if (product.toLowerCase().includes('vision one')) {
    if (description.includes('connector') || description.includes('api') ||
        description.includes('integration') || description.includes('endpoint')) {
      recommendations.push({
        analyzerId: 'v1_connector_analyzer',
        analyzerName: 'Vision One Connector Analyzer',
        confidence: 0.89,
        reasoning: 'Vision One connector or integration issues detected',
        icon: '🔌',
        priority: 1,
        estimatedAnalysisTime: '6-10 minutes',
        requiredFiles: ['Connector logs', 'API response logs', 'Configuration files']
      });
    }
  }
  
  // Apex One specific analyzers  
  if (product.toLowerCase().includes('apex one')) {
    if (description.includes('security agent') || description.includes('scan engine') ||
        description.includes('web console') || description.includes('policy')) {
      recommendations.push({
        analyzerId: 'apex_analyzer',
        analyzerName: 'Apex One Component Analyzer',
        confidence: 0.86,
        reasoning: 'Apex One component or policy issues identified',
        icon: '🏔️',
        priority: 1,
        estimatedAnalysisTime: '5-8 minutes',
        requiredFiles: ['Security Agent logs', 'Web Console logs', 'Policy deployment logs']
      });
    }
  }
  
  // Sort by confidence and priority
  return recommendations
    .sort((a, b) => b.confidence - a.confidence || a.priority - b.priority)
    .slice(0, 3); // Return top 3 recommendations
}

function assessCaseComplexity(description: string, product: string, category: string, severity?: string): CaseComplexityAnalysis {
  let complexityScore = 0;
  const factors: string[] = [];
  const requiredExpertise: string[] = [];
  const similarPatterns: string[] = [];
  
  // Technical complexity indicators
  if (description.includes('cluster') || description.includes('load balancer') ||
      description.includes('high availability')) {
    complexityScore += 25;
    factors.push('Enterprise architecture involved');
    requiredExpertise.push('Infrastructure expertise');
  }
  
  if (description.includes('custom') || description.includes('api') ||
      description.includes('integration') || description.includes('script')) {
    complexityScore += 20;
    factors.push('Custom integration or scripting');
    requiredExpertise.push('Development/API expertise');
  }
  
  if (description.includes('database') || description.includes('sql') ||
      description.includes('corruption') || description.includes('backup')) {
    complexityScore += 20;
    factors.push('Database or data integrity issues');
    requiredExpertise.push('Database administration');
  }
  
  // Multi-system complexity
  const systemCount = (description.match(/\d+\s+(server|system|machine|host)/gi) || []).length;
  if (systemCount > 0) {
    complexityScore += Math.min(systemCount * 5, 25);
    factors.push(`Multiple systems affected (${systemCount})`);
    requiredExpertise.push('Large-scale deployment expertise');
  }
  
  // Network complexity
  if (description.includes('firewall') || description.includes('proxy') ||
      description.includes('network') || description.includes('vlan')) {
    complexityScore += 15;
    factors.push('Network configuration involved');
    requiredExpertise.push('Network administration');
  }
  
  // Security complexity
  if (description.includes('security') || description.includes('breach') ||
      description.includes('malware') || description.includes('threat')) {
    complexityScore += 15;
    factors.push('Security implications');
    requiredExpertise.push('Security expertise');
  }
  
  // Determine complexity level
  let level: 'Simple' | 'Moderate' | 'Complex' | 'Expert-Level';
  let estimatedTime: string;
  
  if (complexityScore >= 60) {
    level = 'Expert-Level';
    estimatedTime = '3-7 days';
    similarPatterns.push('Enterprise architecture issues', 'Multi-system failures', 'Complex integrations');
  } else if (complexityScore >= 35) {
    level = 'Complex';
    estimatedTime = '1-3 days';
    similarPatterns.push('Configuration issues', 'Network problems', 'Performance optimization');
  } else if (complexityScore >= 15) {
    level = 'Moderate';
    estimatedTime = '4-8 hours';
    similarPatterns.push('Service issues', 'Installation problems', 'Policy deployment');
  } else {
    level = 'Simple';
    estimatedTime = '1-4 hours';
    similarPatterns.push('Basic configuration', 'User guidance', 'Simple troubleshooting');
  }
  
  // Adjust for severity
  if (severity === 'Critical' && level !== 'Expert-Level') {
    estimatedTime = estimatedTime.replace(/\d+-\d+/, (match) => {
      const [min, max] = match.split('-').map(Number);
      return `${Math.ceil(min * 0.5)}-${Math.ceil(max * 0.7)}`;
    });
  }
  
  return {
    level,
    factors,
    estimatedResolutionTime: estimatedTime,
    requiredExpertise: requiredExpertise.length > 0 ? requiredExpertise : ['General technical knowledge'],
    similarCasePatterns: similarPatterns
  };
}

function identifyRequiredInformation(description: string, product: string, attachmentCount: number): string[] {
  const required: string[] = [];
  
  // Basic information requirements
  if (!description.includes('version') && !description.includes('build')) {
    required.push('Product version and build number');
  }
  
  if (!description.includes('windows') && !description.includes('linux') && 
      !description.includes('centos') && !description.includes('ubuntu')) {
    required.push('Operating system details');
  }
  
  if (!description.includes('error') && !description.includes('message')) {
    required.push('Exact error messages or codes');
  }
  
  if (attachmentCount === 0) {
    required.push('Relevant log files or diagnostic data');
  }
  
  // Product-specific requirements
  if (product.toLowerCase().includes('deep security')) {
    if (!description.includes('agent') && !description.includes('manager')) {
      required.push('Specify if issue is with Agent, Manager, or both');
    }
    
    if (description.includes('policy') && !description.includes('rule')) {
      required.push('Specific policy rules or modules affected');
    }
  }
  
  // Environment details
  if (!description.includes('production') && !description.includes('test') && 
      !description.includes('staging')) {
    required.push('Environment type (production, test, staging)');
  }
  
  return required.slice(0, 5); // Limit to top 5 requirements
}

function generateSuggestedActions(description: string, product: string, category: string, recommendations: AnalyzerRecommendation[]): string[] {
  const actions: string[] = [];
  
  // Immediate actions based on description
  if (description.includes('error') || description.includes('fail')) {
    actions.push('Collect and review error logs from the time of failure');
    actions.push('Check system event logs for related entries');
  }
  
  if (description.includes('performance') || description.includes('slow')) {
    actions.push('Monitor system resource usage during the issue');
    actions.push('Baseline performance metrics for comparison');
  }
  
  // Product-specific actions
  if (product.toLowerCase().includes('deep security')) {
    if (description.includes('agent')) {
      actions.push('Verify agent-manager communication status');
      actions.push('Check agent heartbeat and last communication time');
    }
    
    if (description.includes('scan')) {
      actions.push('Review scan configuration and exclusions');
      actions.push('Test manual scan to isolate the issue');
    }
  }
  
  // Analyzer-specific actions
  if (recommendations.length > 0) {
    const topAnalyzer = recommendations[0];
    actions.push(`Run ${topAnalyzer.analyzerName} for detailed insights`);
    if (topAnalyzer.requiredFiles && topAnalyzer.requiredFiles.length > 0) {
      actions.push(`Collect: ${topAnalyzer.requiredFiles.join(', ')}`);
    }
  }
  
  // General troubleshooting actions
  actions.push('Document exact reproduction steps if issue is reproducible');
  actions.push('Note any recent changes to the environment or configuration');
  
  return actions.slice(0, 6); // Limit to top 6 actions
}

function analyzePotentialRootCauses(description: string, product: string): string[] {
  const causes: string[] = [];
  
  // Common root cause patterns
  if (description.includes('after') && (description.includes('update') || description.includes('upgrade'))) {
    causes.push('Software update or upgrade compatibility issue');
    causes.push('Configuration changes during update process');
  }
  
  if (description.includes('suddenly') || description.includes('stopped working')) {
    causes.push('Service or process crash');
    causes.push('External dependency failure');
    causes.push('Resource exhaustion');
  }
  
  if (description.includes('network') || description.includes('connection')) {
    causes.push('Network connectivity issues');
    causes.push('Firewall or proxy configuration changes');
    causes.push('DNS resolution problems');
  }
  
  if (description.includes('certificate') || description.includes('ssl') || description.includes('tls')) {
    causes.push('SSL/TLS certificate expiration or misconfiguration');
    causes.push('Certificate trust chain issues');
  }
  
  // Product-specific root causes
  if (product.toLowerCase().includes('deep security')) {
    if (description.includes('policy') || description.includes('rule')) {
      causes.push('Policy inheritance or assignment issues');
      causes.push('Conflicting security rules');
    }
    
    if (description.includes('database') || description.includes('db')) {
      causes.push('Database connection or performance issues');
      causes.push('Database schema or corruption problems');
    }
  }
  
  return causes.slice(0, 5); // Return top 5 potential causes
}

function prioritizeTroubleshooting(description: string, product: string, complexity: CaseComplexityAnalysis): string[] {
  const steps: string[] = [];
  
  // High-priority immediate checks
  steps.push('Verify service status and recent restarts');
  steps.push('Check system resources (CPU, memory, disk space)');
  steps.push('Review recent error logs and event entries');
  
  // Product-specific priority steps
  if (product.toLowerCase().includes('deep security')) {
    steps.push('Confirm agent-manager communication');
    steps.push('Validate policy assignment and inheritance');
    steps.push('Check database connectivity and performance');
  }
  
  // Complexity-based prioritization
  if (complexity.level === 'Expert-Level') {
    steps.push('Engage senior technical resources');
    steps.push('Plan for extended troubleshooting session');
  } else if (complexity.level === 'Complex') {
    steps.push('Schedule dedicated troubleshooting time');
    steps.push('Prepare for configuration changes or restarts');
  }
  
  // Issue-specific steps
  if (description.includes('performance')) {
    steps.splice(1, 0, 'Establish performance baseline and monitoring');
  }
  
  if (description.includes('security') || description.includes('malware')) {
    steps.splice(0, 0, 'Isolate affected systems as security precaution');
  }
  
  return steps.slice(0, 8); // Return top 8 prioritized steps
}

function findKnowledgeBaseReferences(description: string, product: string, category: string): string[] {
  const references: string[] = [];
  
  // Product-specific knowledge base articles
  if (product.toLowerCase().includes('deep security')) {
    if (description.includes('installation') || description.includes('install')) {
      references.push('Deep Security Installation and Upgrade Guide');
      references.push('System Requirements and Compatibility Matrix');
    }
    
    if (description.includes('policy') || description.includes('rule')) {
      references.push('Policy Management Best Practices');
      references.push('Security Module Configuration Guide');
    }
    
    if (description.includes('agent')) {
      references.push('Agent Deployment and Management');
      references.push('Agent Communication Troubleshooting');
    }
  }
  
  // Category-specific references
  if (category.toLowerCase().includes('how to')) {
    references.push('Product Documentation and User Guides');
    references.push('Configuration Examples and Templates');
  }
  
  if (category.toLowerCase().includes('product issue')) {
    references.push('Known Issues and Workarounds');
    references.push('Troubleshooting and Diagnostic Tools');
  }
  
  // General references
  references.push('Support Knowledge Base Search');
  references.push('Community Forums and Discussions');
  
  return references.slice(0, 5); // Return top 5 references
}

function identifyEscalationTriggers(description: string, severity?: string, complexity?: CaseComplexityAnalysis): string[] {
  const triggers: string[] = [];
  
  // Automatic escalation triggers
  if (severity === 'Critical') {
    triggers.push('Critical severity requires immediate escalation');
  }
  
  if (complexity?.level === 'Expert-Level') {
    triggers.push('Expert-level complexity requires specialized resources');
  }
  
  // Content-based triggers
  if (description.includes('data loss') || description.includes('corruption')) {
    triggers.push('Data integrity issues require immediate expert attention');
  }
  
  if (description.includes('security') && description.includes('breach')) {
    triggers.push('Security incident requires security team involvement');
  }
  
  if (description.includes('outage') || description.includes('down')) {
    triggers.push('Service outage requires rapid response team');
  }
  
  // Scale-based triggers
  const affectedCount = description.match(/(\d+)\s+(server|system|user|client)/gi);
  if (affectedCount && affectedCount.some(match => parseInt(match) > 50)) {
    triggers.push('Large-scale impact requires management awareness');
  }
  
  return triggers;
}

// Enhanced Claude AI integration for comprehensive analysis
async function enhanceWithClaude(analysis: EnhancedCaseAnalysis, request: EnhancedCaseAnalysisRequest): Promise<EnhancedCaseAnalysis> {
  const claudeApiKey = process.env.OPENAI_API_KEY;
  
  if (!claudeApiKey) {
    return analysis;
  }
  
  try {
    const prompt = `Analyze this technical support case comprehensively:

Product: ${request.product}
Category: ${request.category}
Severity: ${request.severity || 'Not specified'}
Description: "${request.description}"
Attachments: ${request.attachmentCount} files

Current AI Analysis:
- Complexity: ${analysis.caseComplexity.level}
- Top Analyzer: ${analysis.analyzerRecommendations[0]?.analyzerName || 'None'}

As a ${request.product} expert, provide enhanced analysis:
1. Validate analyzer recommendations and suggest additional tools
2. Refine root cause analysis with product-specific insights
3. Enhance troubleshooting priority with proven methodologies
4. Add specific knowledge base references and documentation
5. Identify any missed escalation triggers

Focus on actionable, specific recommendations for ${request.product} support teams.

Respond in JSON format matching the EnhancedCaseAnalysis interface.`;

    const response = await fetch(process.env.OPENAI_BASE_URL || 'https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${claudeApiKey}`,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'claude-4-sonnet',
        max_tokens: 2000,
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
        analyzerRecommendations: [
          ...analysis.analyzerRecommendations,
          ...(enhancedAnalysis.analyzerRecommendations || [])
        ].slice(0, 4),
        caseComplexity: {
          ...analysis.caseComplexity,
          estimatedResolutionTime: enhancedAnalysis.caseComplexity?.estimatedResolutionTime || analysis.caseComplexity.estimatedResolutionTime
        },
        requiredInformation: [
          ...analysis.requiredInformation,
          ...(enhancedAnalysis.requiredInformation || [])
        ].slice(0, 6),
        suggestedActions: [
          ...analysis.suggestedActions,
          ...(enhancedAnalysis.suggestedActions || [])
        ].slice(0, 8),
        potentialRootCauses: [
          ...analysis.potentialRootCauses,
          ...(enhancedAnalysis.potentialRootCauses || [])
        ].slice(0, 6),
        troubleshootingPriority: enhancedAnalysis.troubleshootingPriority || analysis.troubleshootingPriority,
        knowledgeBaseReferences: [
          ...analysis.knowledgeBaseReferences,
          ...(enhancedAnalysis.knowledgeBaseReferences || [])
        ].slice(0, 7),
        escalationTriggers: [
          ...analysis.escalationTriggers,
          ...(enhancedAnalysis.escalationTriggers || [])
        ]
      };
    }
  } catch {
    console.log('Claude enhancement not available, using local analysis');
  }
  
  return analysis;
}

export async function POST(request: NextRequest) {
  try {
    const body: EnhancedCaseAnalysisRequest = await request.json();
    
    // Validate required fields
    if (!body.description || !body.product || !body.category) {
      return NextResponse.json(
        { error: 'Description, product, and category are required' },
        { status: 400 }
      );
    }
    
    // Generate comprehensive case analysis
    let analysis = analyzeCase(body);
    
    // Enhance with Claude if available
    analysis = await enhanceWithClaude(analysis, body);
    
    return NextResponse.json(analysis);
    
  } catch (error) {
    console.error('Error performing enhanced case analysis:', error);
    return NextResponse.json(
      { error: 'Failed to perform enhanced case analysis' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Enhanced Case Analysis Service is running',
    capabilities: [
      'Multi-dimensional analyzer recommendations',
      'Case complexity assessment with expert-level detection',
      'Comprehensive root cause analysis',
      'Prioritized troubleshooting roadmaps',
      'Knowledge base integration and references',
      'Escalation trigger identification',
      'Product-specific expertise (Deep Security, Vision One, Apex One)',
      'Claude AI enhancement for expert-level insights'
    ],
    supportedProducts: [
      'Deep Security (AMSP, Conflict, Resource, Agent analyzers)',
      'Vision One (Connector, API, Integration analyzers)', 
      'Apex One (Security Agent, Policy analyzers)',
      'Service Gateway',
      'Other Trend Micro products'
    ],
    complexityLevels: {
      'Simple': '1-4 hours - Basic configuration and user guidance',
      'Moderate': '4-8 hours - Service issues and policy deployment',
      'Complex': '1-3 days - Network problems and performance optimization',
      'Expert-Level': '3-7 days - Enterprise architecture and multi-system issues'
    }
  });
}