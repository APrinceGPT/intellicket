import { NextRequest, NextResponse } from 'next/server';

interface CaseAnalysisRequest {
  description: string;
  caseTitle?: string; // Add case title for better context
  product: string;
  issueCategory: string; // Kept for frontend compatibility but not used in scoring
  severity: string; // Kept for frontend compatibility but not used in scoring
  attachmentCount: number; // Kept for frontend compatibility but not used in scoring
  attachmentTypes: string[]; // Kept for frontend compatibility but not used in scoring
}

interface AnalyzerRecommendation {
  analyzerId: string;
  analyzerName: string;
  confidence: number;
  reasoning: string;
  icon: string;
}

// Analyzer definitions
const ANALYZERS = {
  ds_agent_offline: {
    id: 'ds_agent_offline',
    name: 'DS Agent Offline',
    icon: '🔴',
    keywords: ['offline', 'agent', 'connectivity', 'heartbeat', 'communication', 'manager', 'not responding', 'disconnected', 'unreachable', 'service', 'daemon', 'connect', 'network', 'timeout', 'down'],
    categories: ['Product Issue', 'Connectivity Issue'],
    products: ['Deep Security']
  },
  amsp_logs: {
    id: 'amsp_logs',
    name: 'AMSP Analysis',
    icon: '🦠',
    keywords: ['anti-malware', 'amsp', 'scan', 'quarantine', 'threat', 'detection', 'virus', 'malware', 'infected', 'suspicious', 'blocked', 'real-time', 'protection', 'scanning', 'engine'],
    categories: ['Product Issue', 'Threat Issue'],
    products: ['Deep Security', 'Apex One']
  },
  av_conflicts: {
    id: 'av_conflicts',
    name: 'AV Conflicts',
    icon: '⚠️',
    keywords: ['conflict', 'antivirus', 'performance', 'slow', 'cpu', 'memory', 'third-party', 'interference', 'compatibility', 'blocking', 'interfering', 'competing', 'overlapping'],
    categories: ['Product Issue'],
    products: ['Deep Security', 'Apex One']
  },
  resource_analysis: {
    id: 'resource_analysis',
    name: 'Resource Analysis',
    icon: '📈',
    keywords: ['memory', 'cpu', 'performance', 'slow', 'resource', 'utilization', 'system', 'optimization', 'high usage', 'lag', 'freezing', 'responsiveness', 'disk', 'i/o'],
    categories: ['Product Issue'],
    products: ['Deep Security', 'Apex One']
  },
  diagnostic_package: {
    id: 'diagnostic_package',
    name: 'Diagnostic Package',
    icon: '📦',
    keywords: ['diagnostic', 'package', 'multiple', 'comprehensive', 'logs', 'complex', 'correlation', 'zip', 'bundle', 'complete', 'full analysis', 'troubleshooting'],
    categories: ['Product Issue', 'Comprehensive Analysis'],
    products: ['Deep Security', 'Apex One']
  }
};

function analyzeCase(request: CaseAnalysisRequest): AnalyzerRecommendation {
  const { description, caseTitle, product } = request;
  
  // Combine case title and description for better analysis
  const combinedText = [caseTitle || '', description].filter(Boolean).join(' ').toLowerCase();
  const scores: { [key: string]: number } = {};
  
  // Calculate scores for each analyzer
  Object.values(ANALYZERS).forEach(analyzer => {
    let score = 0;
    
    // Keyword matching (70% weight) - Primary scoring factor
    const keywordMatches = analyzer.keywords.filter(keyword => 
      combinedText.includes(keyword.toLowerCase())
    );
    score += (keywordMatches.length / analyzer.keywords.length) * 0.7;
    
    // Product matching (30% weight)
    if (analyzer.products.includes(product)) {
      score += 0.3;
    }
    
    // Boost score for exact phrase matches in title/description
    if (caseTitle && analyzer.id === 'ds_agent_offline' && /offline|agent.*offline|ds.*agent.*offline/i.test(caseTitle)) {
      score += 0.4; // Strong boost for title matches
    }
    
    // Note: Removed severity bonus and attachment type bonus to focus on keyword matching
    // Note: Removed category matching to simplify scoring
    
    scores[analyzer.id] = Math.min(score, 1.0); // Cap at 1.0
  });
  
  // Find the best match
  const bestAnalyzerId = Object.entries(scores).reduce((a, b) => 
    scores[a[0]] > scores[b[0]] ? a : b
  )[0];
  
  const bestAnalyzer = ANALYZERS[bestAnalyzerId as keyof typeof ANALYZERS];
  const confidence = scores[bestAnalyzerId];
  
  // Generate reasoning
  let reasoning = '';
  
  const matchedKeywords = bestAnalyzer.keywords.filter(keyword => 
    combinedText.includes(keyword.toLowerCase())
  );
  
  if (matchedKeywords.length > 0) {
    reasoning += `Based on keywords "${matchedKeywords.slice(0, 3).join('", "')}" in your case details, `;
  } else {
    reasoning += `Based on your "${product}" product selection, `;
  }
  
  reasoning += `the ${bestAnalyzer.name} analyzer is recommended. `;
  
  if (confidence > 0.8) {
    reasoning += 'Strong keyword matches indicate this is the ideal analyzer for your issue.';
  } else if (confidence > 0.6) {
    reasoning += 'Good keyword matches suggest this analyzer fits your reported problem.';
  } else {
    reasoning += 'This analyzer appears most suitable, though you may consider alternatives if needed.';
  }
  
  return {
    analyzerId: bestAnalyzer.id,
    analyzerName: bestAnalyzer.name,
    confidence: Math.max(confidence, 0.5), // Minimum 50% confidence
    reasoning,
    icon: bestAnalyzer.icon
  };
}

export async function POST(request: NextRequest) {
  try {
    const body: CaseAnalysisRequest = await request.json();
    
    // Validate required fields
    if (!body.description || !body.product) {
      return NextResponse.json(
        { error: 'Description and product are required' },
        { status: 400 }
      );
    }
    
    // Analyze the case and get recommendation
    const recommendation = analyzeCase(body);
    
    // Add some artificial delay to simulate AI processing
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return NextResponse.json(recommendation);
    
  } catch (error) {
    console.error('Error analyzing case:', error);
    return NextResponse.json(
      { error: 'Failed to analyze case' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'AI Case Analysis Service is running',
    analyzers: Object.values(ANALYZERS).map(analyzer => ({
      id: analyzer.id,
      name: analyzer.name,
      icon: analyzer.icon
    }))
  });
}
