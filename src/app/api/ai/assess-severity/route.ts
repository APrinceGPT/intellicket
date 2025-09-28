import { NextRequest, NextResponse } from 'next/server';

interface SeverityAssessmentRequest {
  description: string;
  product: string;
  category: string;
  currentSeverity?: string;
  businessImpact?: string;
  affectedUsers?: string;
}

interface SeverityAnalysis {
  recommendedSeverity: 'Low' | 'Medium' | 'High' | 'Critical';
  confidence: number;
  reasoning: string;
  businessImpactAnalysis: string;
  urgencyFactors: string[];
  riskLevel: 'Low' | 'Medium' | 'High';
  escalationRecommended: boolean;
}

// AI-powered severity assessment
function assessSeverity(request: SeverityAssessmentRequest): SeverityAnalysis {
  const { description, product, businessImpact, affectedUsers } = request;
  
  if (!description || description.trim().length < 10) {
    return {
      recommendedSeverity: 'Low',
      confidence: 30,
      reasoning: 'Insufficient information to properly assess severity',
      businessImpactAnalysis: 'Cannot determine business impact without more details',
      urgencyFactors: ['Insufficient information provided'],
      riskLevel: 'Low',
      escalationRecommended: false
    };
  }
  
  const descriptionLower = description.toLowerCase();
  
  // Analyze critical indicators
  const criticalFactors = analyzeCriticalFactors(descriptionLower, product);
  const securityFactors = analyzeSecurityFactors(descriptionLower);
  const availabilityFactors = analyzeAvailabilityFactors(descriptionLower);
  const performanceFactors = analyzePerformanceFactors(descriptionLower);
  const scaleFactors = analyzeScaleFactors(descriptionLower, affectedUsers);
  const businessFactors = analyzeBusinessFactors(descriptionLower, businessImpact);
  
  // Calculate severity score
  const severityScore = calculateSeverityScore({
    critical: criticalFactors.score,
    security: securityFactors.score,
    availability: availabilityFactors.score,
    performance: performanceFactors.score,
    scale: scaleFactors.score,
    business: businessFactors.score
  });
  
  // Determine severity level
  const recommendedSeverity = determineSeverityLevel(severityScore);
  
  // Calculate confidence based on information quality
  const confidence = calculateConfidence(description, businessImpact, affectedUsers);
  
  // Generate reasoning and analysis
  const reasoning = generateReasoning(recommendedSeverity, {
    criticalFactors,
    securityFactors,
    availabilityFactors,
    performanceFactors,
    scaleFactors,
    businessFactors
  });
  
  const businessImpactAnalysis = generateBusinessImpactAnalysis(recommendedSeverity);
  
  const urgencyFactors = collectUrgencyFactors({
    criticalFactors,
    securityFactors,
    availabilityFactors,
    performanceFactors,
    scaleFactors,
    businessFactors
  });
  
  const riskLevel = assessRiskLevel(severityScore, securityFactors, criticalFactors);
  const escalationRecommended = shouldEscalate(recommendedSeverity, confidence, urgencyFactors.length);
  
  return {
    recommendedSeverity,
    confidence,
    reasoning,
    businessImpactAnalysis,
    urgencyFactors,
    riskLevel,
    escalationRecommended
  };
}

function analyzeCriticalFactors(description: string, product: string) {
  let score = 0;
  const indicators: string[] = [];
  
  // System failure indicators
  const failureTerms = ['down', 'crashed', 'failed', 'stopped', 'not working', 'broken', 'offline'];
  failureTerms.forEach(term => {
    if (description.includes(term)) {
      score += 15;
      indicators.push(`System failure: ${term}`);
    }
  });
  
  // Data loss indicators
  const dataLossTerms = ['data loss', 'corrupted', 'deleted', 'missing data', 'lost files'];
  dataLossTerms.forEach(term => {
    if (description.includes(term)) {
      score += 25;
      indicators.push(`Data integrity issue: ${term}`);
    }
  });
  
  // Service unavailability
  const unavailableTerms = ['unavailable', 'inaccessible', 'cannot access', 'service down'];
  unavailableTerms.forEach(term => {
    if (description.includes(term)) {
      score += 20;
      indicators.push(`Service unavailability: ${term}`);
    }
  });
  
  // Product-specific critical issues
  if (product.toLowerCase().includes('deep security')) {
    const dsCritical = ['agent offline', 'manager down', 'policy not applied', 'scan failed'];
    dsCritical.forEach(term => {
      if (description.includes(term)) {
        score += 15;
        indicators.push(`DS critical: ${term}`);
      }
    });
  }
  
  return { score: Math.min(score, 100), indicators };
}

function analyzeSecurityFactors(description: string) {
  let score = 0;
  const indicators: string[] = [];
  
  // Security breach indicators
  const breachTerms = ['breach', 'compromised', 'hacked', 'unauthorized access', 'malware detected'];
  breachTerms.forEach(term => {
    if (description.includes(term)) {
      score += 30;
      indicators.push(`Security breach: ${term}`);
    }
  });
  
  // Vulnerability indicators
  const vulnTerms = ['vulnerability', 'exploit', 'attack', 'threat detected', 'suspicious activity'];
  vulnTerms.forEach(term => {
    if (description.includes(term)) {
      score += 25;
      indicators.push(`Security vulnerability: ${term}`);
    }
  });
  
  // Security service failures
  const secServiceTerms = ['antivirus failed', 'firewall down', 'protection disabled', 'scan blocked'];
  secServiceTerms.forEach(term => {
    if (description.includes(term)) {
      score += 20;
      indicators.push(`Security service failure: ${term}`);
    }
  });
  
  return { score: Math.min(score, 100), indicators };
}

function analyzeAvailabilityFactors(description: string) {
  let score = 0;
  const indicators: string[] = [];
  
  // Downtime indicators
  const downtimeTerms = ['downtime', 'outage', 'unavailable', 'service interruption'];
  downtimeTerms.forEach(term => {
    if (description.includes(term)) {
      score += 20;
      indicators.push(`Availability issue: ${term}`);
    }
  });
  
  // Production impact
  const prodTerms = ['production', 'live environment', 'customer facing', 'business critical'];
  prodTerms.forEach(term => {
    if (description.includes(term)) {
      score += 15;
      indicators.push(`Production impact: ${term}`);
    }
  });
  
  // Time-sensitive indicators
  if (description.includes('urgent') || description.includes('asap') || description.includes('immediately')) {
    score += 15;
    indicators.push('Time-sensitive request');
  }
  
  return { score: Math.min(score, 100), indicators };
}

function analyzePerformanceFactors(description: string) {
  let score = 0;
  const indicators: string[] = [];
  
  // Performance degradation
  const perfTerms = ['slow', 'performance', 'degraded', 'timeout', 'latency', 'bottleneck'];
  perfTerms.forEach(term => {
    if (description.includes(term)) {
      score += 10;
      indicators.push(`Performance issue: ${term}`);
    }
  });
  
  // Resource issues
  const resourceTerms = ['high cpu', 'memory leak', 'disk full', 'out of memory'];
  resourceTerms.forEach(term => {
    if (description.includes(term)) {
      score += 15;
      indicators.push(`Resource issue: ${term}`);
    }
  });
  
  return { score: Math.min(score, 100), indicators };
}

function analyzeScaleFactors(description: string, affectedUsers?: string) {
  let score = 0;
  const indicators: string[] = [];
  
  // Quantitative impact
  const scalePatterns = [
    { pattern: /all\s+(\d+)/i, multiplier: 3 },
    { pattern: /(\d+)\s+servers?/i, multiplier: 2 },
    { pattern: /(\d+)\s+users?/i, multiplier: 1.5 },
    { pattern: /multiple/i, multiplier: 1.5 },
    { pattern: /entire/i, multiplier: 3 },
    { pattern: /company.wide/i, multiplier: 3 }
  ];
  
  scalePatterns.forEach(({ pattern, multiplier }) => {
    const match = description.match(pattern);
    if (match) {
      const number = parseInt(match[1]) || 10;
      score += Math.min(number * multiplier, 30);
      indicators.push(`Scale impact: ${match[0]}`);
    }
  });
  
  // Affected users analysis
  if (affectedUsers) {
    const userCount = parseInt(affectedUsers);
    if (userCount > 100) {
      score += 25;
      indicators.push(`Large user impact: ${userCount} users`);
    } else if (userCount > 10) {
      score += 15;
      indicators.push(`Moderate user impact: ${userCount} users`);
    }
  }
  
  return { score: Math.min(score, 100), indicators };
}

function analyzeBusinessFactors(description: string, businessImpact?: string) {
  let score = 0;
  const indicators: string[] = [];
  
  // Business impact keywords
  const businessTerms = ['revenue', 'customer', 'compliance', 'regulatory', 'audit', 'sla'];
  businessTerms.forEach(term => {
    if (description.includes(term)) {
      score += 15;
      indicators.push(`Business impact: ${term}`);
    }
  });
  
  // Financial impact
  const financialTerms = ['cost', 'loss', 'money', 'billing', 'payment'];
  financialTerms.forEach(term => {
    if (description.includes(term)) {
      score += 20;
      indicators.push(`Financial impact: ${term}`);
    }
  });
  
  // Business impact description analysis
  if (businessImpact) {
    if (businessImpact.toLowerCase().includes('critical') || businessImpact.toLowerCase().includes('severe')) {
      score += 25;
      indicators.push('Critical business impact stated');
    } else if (businessImpact.toLowerCase().includes('significant') || businessImpact.toLowerCase().includes('major')) {
      score += 15;
      indicators.push('Significant business impact stated');
    }
  }
  
  return { score: Math.min(score, 100), indicators };
}

function calculateSeverityScore(factors: Record<string, number>): number {
  const weights = {
    critical: 0.3,
    security: 0.25,
    availability: 0.2,
    performance: 0.1,
    scale: 0.1,
    business: 0.05
  };
  
  return Object.entries(factors).reduce((total, [key, value]) => {
    return total + (value * (weights[key as keyof typeof weights] || 0));
  }, 0);
}

function determineSeverityLevel(score: number): 'Low' | 'Medium' | 'High' | 'Critical' {
  if (score >= 75) return 'Critical';
  if (score >= 50) return 'High';
  if (score >= 25) return 'Medium';
  return 'Low';
}

function calculateConfidence(description: string, businessImpact?: string, affectedUsers?: string): number {
  let confidence = 50;
  
  // Information completeness
  if (description.length > 100) confidence += 20;
  if (businessImpact) confidence += 15;
  if (affectedUsers) confidence += 10;
  
  // Specific details
  if (description.includes('error') || description.includes('code')) confidence += 10;
  if (/\d+/.test(description)) confidence += 5;
  
  return Math.min(confidence, 100);
}

interface FactorAnalysis {
  score: number;
  indicators: string[];
}

interface AllFactors {
  criticalFactors: FactorAnalysis;
  securityFactors: FactorAnalysis;
  availabilityFactors: FactorAnalysis;
  performanceFactors: FactorAnalysis;
  scaleFactors: FactorAnalysis;
  businessFactors: FactorAnalysis;
}

function generateReasoning(severity: string, factors: AllFactors): string {
  const reasons: string[] = [];
  
  if (factors.criticalFactors.score > 50) {
    reasons.push('Critical system functionality is affected');
  }
  
  if (factors.securityFactors.score > 50) {
    reasons.push('Security-related issues pose significant risk');
  }
  
  if (factors.availabilityFactors.score > 50) {
    reasons.push('Service availability is compromised');
  }
  
  if (factors.scaleFactors.score > 30) {
    reasons.push('Multiple systems or users are affected');
  }
  
  if (factors.businessFactors.score > 30) {
    reasons.push('Business operations are impacted');
  }
  
  if (reasons.length === 0) {
    reasons.push('Based on issue description and impact assessment');
  }
  
  return `${severity} severity recommended because: ${reasons.join(', ')}.`;
}

function generateBusinessImpactAnalysis(severity: string): string {
  if (severity === 'Critical') {
    return 'Immediate business impact with potential for significant operational disruption, financial loss, or security compromise.';
  } else if (severity === 'High') {
    return 'Substantial impact on business operations with degraded functionality affecting productivity or service delivery.';
  } else if (severity === 'Medium') {
    return 'Moderate impact on business operations with workarounds available but reduced efficiency.';
  } else {
    return 'Minimal impact on business operations with no significant disruption to core functionality.';
  }
}

function collectUrgencyFactors(factors: AllFactors): string[] {
  const urgencyFactors: string[] = [];
  
  factors.criticalFactors.indicators.forEach((indicator: string) => urgencyFactors.push(indicator));
  factors.securityFactors.indicators.forEach((indicator: string) => urgencyFactors.push(indicator));
  factors.availabilityFactors.indicators.forEach((indicator: string) => urgencyFactors.push(indicator));
  factors.scaleFactors.indicators.forEach((indicator: string) => urgencyFactors.push(indicator));
  
  return urgencyFactors.slice(0, 5); // Return top 5 urgency factors
}

function assessRiskLevel(severityScore: number, securityFactors: FactorAnalysis, criticalFactors: FactorAnalysis): 'Low' | 'Medium' | 'High' {
  if (securityFactors.score > 50 || criticalFactors.score > 70) return 'High';
  if (severityScore > 50) return 'Medium';
  return 'Low';
}

function shouldEscalate(severity: string, confidence: number, urgencyFactorCount: number): boolean {
  return severity === 'Critical' || 
         (severity === 'High' && confidence > 70) ||
         urgencyFactorCount >= 3;
}

// Enhanced Claude AI integration for severity assessment
async function enhanceWithClaude(assessment: SeverityAnalysis, request: SeverityAssessmentRequest): Promise<SeverityAnalysis> {
  const claudeApiKey = process.env.OPENAI_API_KEY;
  
  if (!claudeApiKey) {
    return assessment;
  }
  
  try {
    const prompt = `Analyze this technical support case for severity assessment:

Product: ${request.product}
Category: ${request.category}
Description: "${request.description}"
Business Impact: ${request.businessImpact || 'Not specified'}
Affected Users: ${request.affectedUsers || 'Not specified'}

Current AI Assessment: ${assessment.recommendedSeverity} (${assessment.confidence}% confidence)

As a technical support expert, provide:
1. Severity validation with specific reasoning
2. Additional urgency factors I might have missed  
3. Business impact refinement
4. Escalation recommendations

Consider industry standards and best practices for ${request.product} support.

Respond in JSON format matching the SeverityAnalysis interface.`;

    const response = await fetch(process.env.OPENAI_BASE_URL || 'https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${claudeApiKey}`,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'claude-4-sonnet',
        max_tokens: 1000,
        messages: [{
          role: 'user',
          content: prompt
        }]
      })
    });
    
    if (response.ok) {
      const claudeResult = await response.json();
      const enhancedAnalysis = JSON.parse(claudeResult.content[0].text);
      
      return {
        ...assessment,
        confidence: Math.max(assessment.confidence, 90),
        reasoning: enhancedAnalysis.reasoning || assessment.reasoning,
        businessImpactAnalysis: enhancedAnalysis.businessImpactAnalysis || assessment.businessImpactAnalysis,
        urgencyFactors: [
          ...assessment.urgencyFactors,
          ...(enhancedAnalysis.urgencyFactors || [])
        ].slice(0, 6),
        escalationRecommended: enhancedAnalysis.escalationRecommended ?? assessment.escalationRecommended
      };
    }
  } catch {
    console.log('Claude enhancement not available, using local analysis');
  }
  
  return assessment;
}

export async function POST(request: NextRequest) {
  try {
    const body: SeverityAssessmentRequest = await request.json();
    
    // Validate required fields
    if (!body.description || !body.product || !body.category) {
      return NextResponse.json(
        { error: 'Description, product, and category are required' },
        { status: 400 }
      );
    }
    
    // Generate severity assessment
    let assessment = assessSeverity(body);
    
    // Enhance with Claude if available
    assessment = await enhanceWithClaude(assessment, body);
    
    return NextResponse.json(assessment);
    
  } catch (error) {
    console.error('Error assessing severity:', error);
    return NextResponse.json(
      { error: 'Failed to assess severity' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Severity Assessment Service is running',
    capabilities: [
      'Multi-factor severity analysis',
      'Business impact assessment',
      'Security risk evaluation',
      'Scale and availability analysis',
      'Escalation recommendations',
      'Claude AI enhancement (when available)'
    ],
    severityLevels: {
      'Critical': 'Immediate response required - system down, security breach, or data loss',
      'High': 'Urgent response needed - significant functionality impaired',
      'Medium': 'Timely response expected - moderate impact with workarounds',
      'Low': 'Standard response - minor issues or enhancement requests'
    }
  });
}