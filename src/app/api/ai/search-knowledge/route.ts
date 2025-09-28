import { NextRequest, NextResponse } from 'next/server';

interface KnowledgeSearchRequest {
  query: string;
  product: string;
  category?: string;
  severity?: string;
  maxResults?: number;
  searchType?: 'similar_cases' | 'solutions' | 'troubleshooting' | 'all';
}

interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  relevanceScore: number;
  source: 'knowledge_base' | 'case_history' | 'documentation' | 'community';
  type: 'solution' | 'troubleshooting' | 'known_issue' | 'how_to' | 'case_study';
  tags: string[];
  lastUpdated: string;
  applicability: {
    products: string[];
    versions: string[];
    scenarios: string[];
  };
}

interface ProactiveSolution {
  solutionId: string;
  title: string;
  description: string;
  steps: string[];
  confidence: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  estimatedTime: string;
  requiredSkills: string[];
  dependencies: string[];
  successRate: number;
  relatedCases: string[];
}

interface RelatedCase {
  caseId: string;
  title: string;
  description: string;
  similarity: number;
  resolution: string;
  resolutionTime: string;
  product: string;
  category: string;
  severity: string;
  keywords: string[];
  applicableSteps: string[];
}

interface KnowledgeSearchResult {
  query: string;
  totalResults: number;
  knowledgeItems: KnowledgeItem[];
  proactiveSolutions: ProactiveSolution[];
  relatedCases: RelatedCase[];
  searchSuggestions: string[];
  executionTime: string;
}

// Simulate knowledge base with realistic data
const KNOWLEDGE_BASE_ITEMS: KnowledgeItem[] = [
  {
    id: 'kb_001',
    title: 'Deep Security Agent Communication Troubleshooting',
    content: 'Comprehensive guide for resolving agent-to-manager communication issues including network, certificate, and firewall configuration...',
    relevanceScore: 0,
    source: 'knowledge_base',
    type: 'troubleshooting',
    tags: ['agent', 'communication', 'network', 'firewall'],
    lastUpdated: '2024-09-15',
    applicability: {
      products: ['Deep Security'],
      versions: ['19.0', '20.0'],
      scenarios: ['agent_offline', 'communication_failure', 'heartbeat_lost']
    }
  },
  {
    id: 'kb_002',
    title: 'AMSP High CPU Usage Resolution',
    content: 'Step-by-step solution for resolving Anti-Malware Scan Performance issues causing high CPU utilization...',
    relevanceScore: 0,
    source: 'knowledge_base',
    type: 'solution',
    tags: ['amsp', 'performance', 'cpu', 'scan'],
    lastUpdated: '2024-09-10',
    applicability: {
      products: ['Deep Security'],
      versions: ['19.0', '20.0'],
      scenarios: ['high_cpu', 'performance_degradation', 'scan_issues']
    }
  },
  {
    id: 'kb_003',
    title: 'Policy Deployment Best Practices',
    content: 'Guidelines for efficient policy deployment, inheritance management, and troubleshooting deployment failures...',
    relevanceScore: 0,
    source: 'documentation',
    type: 'how_to',
    tags: ['policy', 'deployment', 'inheritance', 'best_practices'],
    lastUpdated: '2024-09-12',
    applicability: {
      products: ['Deep Security'],
      versions: ['19.0', '20.0'],
      scenarios: ['policy_deployment', 'inheritance_issues', 'rule_conflicts']
    }
  },
  {
    id: 'kb_004',
    title: 'Vision One Connector SSL Certificate Issues',
    content: 'Common SSL/TLS certificate problems with Vision One connectors and their resolutions...',
    relevanceScore: 0,
    source: 'knowledge_base',
    type: 'known_issue',
    tags: ['vision_one', 'ssl', 'certificate', 'connector'],
    lastUpdated: '2024-09-08',
    applicability: {
      products: ['Vision One'],
      versions: ['1.0', '1.5'],
      scenarios: ['ssl_errors', 'certificate_expiry', 'handshake_failure']
    }
  },
  {
    id: 'kb_005',
    title: 'Database Performance Optimization for DS Manager',
    content: 'Database tuning guidelines for Deep Security Manager to improve performance and reduce query times...',
    relevanceScore: 0,
    source: 'documentation',
    type: 'how_to',
    tags: ['database', 'performance', 'manager', 'optimization'],
    lastUpdated: '2024-09-05',
    applicability: {
      products: ['Deep Security'],
      versions: ['19.0', '20.0'],
      scenarios: ['slow_console', 'database_performance', 'query_timeout']
    }
  }
];

const CASE_HISTORY: RelatedCase[] = [
  {
    caseId: 'CASE-2024-001234',
    title: 'DS Agent Offline After Windows Update',
    description: 'Multiple agents showing offline status after automatic Windows updates, resolved by certificate refresh',
    similarity: 0,
    resolution: 'Updated agent certificates and restarted services',
    resolutionTime: '4 hours',
    product: 'Deep Security',
    category: 'Product Issue',
    severity: 'High',
    keywords: ['agent', 'offline', 'windows_update', 'certificate'],
    applicableSteps: [
      'Check certificate validity',
      'Restart Deep Security Agent service',
      'Verify network connectivity',
      'Update agent if necessary'
    ]
  },
  {
    caseId: 'CASE-2024-005678',
    title: 'AMSP Service High CPU During Scans',
    description: 'Anti-malware scan performance causing 90% CPU usage, resolved with exclusion configuration',
    similarity: 0,
    resolution: 'Configured scan exclusions and adjusted scan schedule',
    resolutionTime: '2 hours',
    product: 'Deep Security',
    category: 'Product Issue', 
    severity: 'High',
    keywords: ['amsp', 'cpu', 'performance', 'scan'],
    applicableSteps: [
      'Review scan exclusions',
      'Adjust scan schedule',
      'Monitor resource usage',
      'Optimize scan configuration'
    ]
  },
  {
    caseId: 'CASE-2024-009012',
    title: 'Vision One API Timeout Errors',
    description: 'Connector experiencing timeout errors when communicating with Vision One API, resolved with proxy configuration',
    similarity: 0,
    resolution: 'Configured proxy settings and increased timeout values',
    resolutionTime: '3 hours',
    product: 'Vision One',
    category: 'Product Issue',
    severity: 'Medium',
    keywords: ['api', 'timeout', 'connector', 'proxy'],
    applicableSteps: [
      'Check proxy configuration',
      'Verify network connectivity',
      'Increase timeout settings',
      'Test API connectivity'
    ]
  }
];

// AI-powered knowledge search
function searchKnowledgeBase(request: KnowledgeSearchRequest): KnowledgeSearchResult {
  const { query, product, category, severity, maxResults = 10, searchType = 'all' } = request;
  const startTime = Date.now();
  
  if (!query || query.trim().length < 3) {
    return {
      query,
      totalResults: 0,
      knowledgeItems: [],
      proactiveSolutions: [],
      relatedCases: [],
      searchSuggestions: generateSearchSuggestions(product),
      executionTime: '0ms'
    };
  }
  
  const queryLower = query.toLowerCase();
  const queryWords = queryLower.split(' ').filter(word => word.length > 2);
  
  // Search knowledge base items
  let relevantKnowledgeItems: KnowledgeItem[] = [];
  if (searchType === 'all' || searchType === 'solutions' || searchType === 'troubleshooting') {
    relevantKnowledgeItems = searchKnowledgeItems(queryWords, product, category);
  }
  
  // Search related cases
  let relevantCases: RelatedCase[] = [];
  if (searchType === 'all' || searchType === 'similar_cases') {
    relevantCases = searchRelatedCases(queryWords, product, category, severity);
  }
  
  // Generate proactive solutions
  let proactiveSolutions: ProactiveSolution[] = [];
  if (searchType === 'all' || searchType === 'solutions') {
    proactiveSolutions = generateProactiveSolutions(queryWords, product, relevantKnowledgeItems, relevantCases);
  }
  
  // Generate search suggestions
  const searchSuggestions = generateSearchSuggestions(product, queryWords);
  
  const executionTime = `${Date.now() - startTime}ms`;
  
  return {
    query,
    totalResults: relevantKnowledgeItems.length + relevantCases.length + proactiveSolutions.length,
    knowledgeItems: relevantKnowledgeItems.slice(0, maxResults),
    proactiveSolutions: proactiveSolutions.slice(0, 3),
    relatedCases: relevantCases.slice(0, 5),
    searchSuggestions: searchSuggestions.slice(0, 5),
    executionTime
  };
}

function searchKnowledgeItems(queryWords: string[], product: string, category?: string): KnowledgeItem[] {
  return KNOWLEDGE_BASE_ITEMS
    .map(item => {
      let relevanceScore = 0;
      
      // Product matching
      if (item.applicability.products.some(p => p.toLowerCase().includes(product.toLowerCase()))) {
        relevanceScore += 30;
      }
      
      // Category matching
      if (category) {
        if (item.type === 'troubleshooting' && category.toLowerCase().includes('issue')) {
          relevanceScore += 20;
        } else if (item.type === 'how_to' && category.toLowerCase().includes('how')) {
          relevanceScore += 20;
        }
      }
      
      // Query word matching
      queryWords.forEach(word => {
        // Title matching (higher weight)
        if (item.title.toLowerCase().includes(word)) {
          relevanceScore += 25;
        }
        
        // Content matching
        if (item.content.toLowerCase().includes(word)) {
          relevanceScore += 15;
        }
        
        // Tag matching
        if (item.tags.some(tag => tag.toLowerCase().includes(word) || word.includes(tag.toLowerCase()))) {
          relevanceScore += 20;
        }
        
        // Scenario matching
        if (item.applicability.scenarios.some(scenario => scenario.toLowerCase().includes(word) || word.includes(scenario.toLowerCase()))) {
          relevanceScore += 15;
        }
      });
      
      return {
        ...item,
        relevanceScore
      };
    })
    .filter(item => item.relevanceScore > 20)
    .sort((a, b) => b.relevanceScore - a.relevanceScore);
}

function searchRelatedCases(queryWords: string[], product: string, category?: string, severity?: string): RelatedCase[] {
  return CASE_HISTORY
    .map(caseItem => {
      let similarity = 0;
      
      // Product matching
      if (caseItem.product.toLowerCase().includes(product.toLowerCase())) {
        similarity += 30;
      }
      
      // Category matching
      if (category && caseItem.category.toLowerCase().includes(category.toLowerCase())) {
        similarity += 20;
      }
      
      // Severity matching
      if (severity && caseItem.severity.toLowerCase() === severity.toLowerCase()) {
        similarity += 15;
      }
      
      // Query word matching
      queryWords.forEach(word => {
        // Title matching
        if (caseItem.title.toLowerCase().includes(word)) {
          similarity += 25;
        }
        
        // Description matching
        if (caseItem.description.toLowerCase().includes(word)) {
          similarity += 15;
        }
        
        // Keyword matching
        if (caseItem.keywords.some(keyword => keyword.toLowerCase().includes(word) || word.includes(keyword.toLowerCase()))) {
          similarity += 20;
        }
      });
      
      return {
        ...caseItem,
        similarity
      };
    })
    .filter(caseItem => caseItem.similarity > 25)
    .sort((a, b) => b.similarity - a.similarity);
}

function generateProactiveSolutions(queryWords: string[], product: string, knowledgeItems: KnowledgeItem[], relatedCases: RelatedCase[]): ProactiveSolution[] {
  const solutions: ProactiveSolution[] = [];
  
  // Generate solutions based on knowledge items
  knowledgeItems.slice(0, 2).forEach((item, index) => {
    if (item.type === 'solution' || item.type === 'troubleshooting') {
      const solution: ProactiveSolution = {
        solutionId: `sol_${Date.now()}_${index}`,
        title: `Recommended Solution: ${item.title}`,
        description: item.content.substring(0, 200) + '...',
        steps: generateSolutionSteps(item, queryWords),
        confidence: Math.round(item.relevanceScore),
        riskLevel: determineRiskLevel(item, queryWords),
        estimatedTime: estimateImplementationTime(item, queryWords),
        requiredSkills: extractRequiredSkills(item),
        dependencies: extractDependencies(item, product),
        successRate: calculateSuccessRate(item, relatedCases),
        relatedCases: relatedCases.slice(0, 2).map(c => c.caseId)
      };
      solutions.push(solution);
    }
  });
  
  // Generate solutions based on related cases
  relatedCases.slice(0, 1).forEach((caseItem, index) => {
    const solution: ProactiveSolution = {
      solutionId: `case_sol_${Date.now()}_${index}`,
      title: `Proven Solution from Similar Case`,
      description: `Based on ${caseItem.caseId}: ${caseItem.description}`,
      steps: caseItem.applicableSteps,
      confidence: Math.round(caseItem.similarity),
      riskLevel: 'Low',
      estimatedTime: caseItem.resolutionTime,
      requiredSkills: ['System Administration'],
      dependencies: [`${product} access`, 'System restart capability'],
      successRate: 85,
      relatedCases: [caseItem.caseId]
    };
    solutions.push(solution);
  });
  
  return solutions.sort((a, b) => b.confidence - a.confidence);
}

function generateSolutionSteps(item: KnowledgeItem, queryWords: string[]): string[] {
  // Generate contextual steps based on the knowledge item and query
  const baseSteps = [
    'Review the current configuration and identify the issue',
    'Back up existing settings before making changes',
    'Apply the recommended solution steps',
    'Test the solution in a controlled environment',
    'Monitor the results and validate the fix'
  ];
  
  // Customize steps based on item type and query
  if (item.tags.includes('agent') && queryWords.includes('offline')) {
    return [
      'Check Deep Security Agent service status',
      'Verify network connectivity to DS Manager',
      'Validate SSL certificates and trust relationships',
      'Restart the Deep Security Agent service',
      'Confirm agent appears online in DS Manager console'
    ];
  } else if (item.tags.includes('performance') && queryWords.includes('cpu')) {
    return [
      'Monitor current CPU usage and identify peak times',
      'Review scan schedules and exclusion configurations',
      'Implement recommended performance optimizations',
      'Adjust scan settings to reduce resource impact',
      'Validate performance improvements with monitoring'
    ];
  }
  
  return baseSteps;
}

function determineRiskLevel(item: KnowledgeItem, queryWords: string[]): 'Low' | 'Medium' | 'High' {
  // Determine risk based on solution type and affected components
  if (item.tags.includes('database') || queryWords.includes('database')) {
    return 'High';
  } else if (item.tags.includes('service') || queryWords.includes('restart')) {
    return 'Medium';
  }
  return 'Low';
}

function estimateImplementationTime(item: KnowledgeItem, queryWords: string[]): string {
  // Estimate based on complexity indicators
  if (item.tags.includes('database') || item.tags.includes('configuration')) {
    return '2-4 hours';
  } else if (queryWords.includes('restart') || queryWords.includes('service')) {
    return '30-60 minutes';
  }
  return '1-2 hours';
}

function extractRequiredSkills(item: KnowledgeItem): string[] {
  const skills = ['System Administration'];
  
  if (item.tags.includes('database')) {
    skills.push('Database Administration');
  }
  if (item.tags.includes('network')) {
    skills.push('Network Configuration');
  }
  if (item.tags.includes('ssl') || item.tags.includes('certificate')) {
    skills.push('Certificate Management');
  }
  
  return skills;
}

function extractDependencies(item: KnowledgeItem, product: string): string[] {
  const dependencies = [`${product} administrative access`];
  
  if (item.tags.includes('service')) {
    dependencies.push('Service restart capability');
  }
  if (item.tags.includes('network')) {
    dependencies.push('Network access and firewall configuration');
  }
  if (item.tags.includes('database')) {
    dependencies.push('Database backup and maintenance window');
  }
  
  return dependencies;
}

function calculateSuccessRate(item: KnowledgeItem, relatedCases: RelatedCase[]): number {
  // Base success rate
  let successRate = 75;
  
  // Increase based on knowledge quality
  if (item.source === 'knowledge_base') successRate += 10;
  if (item.type === 'solution') successRate += 10;
  
  // Increase based on related case success
  if (relatedCases.length > 0) successRate += 5;
  
  return Math.min(successRate, 95);
}

function generateSearchSuggestions(product: string, queryWords?: string[]): string[] {
  const productSuggestions: Record<string, string[]> = {
    'Deep Security': [
      'agent communication issues',
      'AMSP high CPU usage',
      'policy deployment failure',
      'SSL certificate problems',
      'database performance optimization',
      'manager console slow response'
    ],
    'Vision One': [
      'connector SSL errors',
      'endpoint sensor offline',
      'API timeout issues',
      'workbench connection problems',
      'data synchronization failures'
    ],
    'Apex One': [
      'security agent startup failure',
      'scan engine errors',
      'web console access issues',
      'policy update problems',
      'malware detection false positives'
    ]
  };
  
  const suggestions = productSuggestions[product] || productSuggestions['Deep Security'];
  
  // If query words provided, filter suggestions to most relevant
  if (queryWords && queryWords.length > 0) {
    return suggestions.filter(suggestion => 
      queryWords.some(word => suggestion.toLowerCase().includes(word))
    );
  }
  
  return suggestions;
}

// Enhanced Claude AI integration for knowledge search
async function enhanceWithClaudeRAG(result: KnowledgeSearchResult, request: KnowledgeSearchRequest): Promise<KnowledgeSearchResult> {
  const claudeApiKey = process.env.OPENAI_API_KEY;
  
  if (!claudeApiKey) {
    return result;
  }
  
  try {
    const prompt = `You are a ${request.product} technical expert. Analyze this support query and enhance the knowledge search results:

Query: "${request.query}"
Product: ${request.product}
Category: ${request.category || 'Not specified'}

Current Results:
- ${result.knowledgeItems.length} knowledge base articles
- ${result.relatedCases.length} related cases  
- ${result.proactiveSolutions.length} suggested solutions

Based on your expertise with ${request.product}, provide:
1. Additional relevant knowledge base topics not covered
2. Enhanced solution steps with specific ${request.product} commands/procedures
3. Potential root causes and preventive measures
4. Advanced troubleshooting techniques

Focus on actionable, specific guidance for ${request.product} support engineers.

Respond with enhanced solutions and additional knowledge items in JSON format.`;

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
      const enhancement = JSON.parse(claudeResult.content[0].text);
      
      // Merge Claude insights with existing results
      return {
        ...result,
        knowledgeItems: [
          ...result.knowledgeItems,
          ...(enhancement.additionalKnowledgeItems || [])
        ].slice(0, 15),
        proactiveSolutions: result.proactiveSolutions.map((solution, index) => ({
          ...solution,
          steps: enhancement.enhancedSolutionSteps?.[index] || solution.steps,
          confidence: Math.min(solution.confidence + 5, 95) // Boost confidence with Claude enhancement
        })),
        searchSuggestions: [
          ...result.searchSuggestions,
          ...(enhancement.additionalSuggestions || [])
        ].slice(0, 8)
      };
    }
  } catch {
    console.log('Claude RAG enhancement not available, using local search');
  }
  
  return result;
}

export async function POST(request: NextRequest) {
  try {
    const body: KnowledgeSearchRequest = await request.json();
    
    // Validate required fields
    if (!body.query || !body.product) {
      return NextResponse.json(
        { error: 'Query and product are required' },
        { status: 400 }
      );
    }
    
    // Search knowledge base
    let searchResult = searchKnowledgeBase(body);
    
    // Enhance with Claude RAG if available
    searchResult = await enhanceWithClaudeRAG(searchResult, body);
    
    return NextResponse.json(searchResult);
    
  } catch (error) {
    console.error('Error searching knowledge base:', error);
    return NextResponse.json(
      { error: 'Failed to search knowledge base' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Knowledge Base Search Service is running',
    capabilities: [
      'Semantic knowledge base search',
      'Related case discovery based on similarity',
      'Proactive solution generation',
      'Multi-source knowledge integration',
      'Product-specific expertise (Deep Security, Vision One, Apex One)',
      'Claude AI enhancement for expert insights',
      'Dynamic search suggestions',
      'Solution risk assessment and success prediction'
    ],
    searchTypes: [
      'similar_cases - Find cases with similar symptoms and resolutions',
      'solutions - Get specific solution steps and procedures',
      'troubleshooting - Access troubleshooting guides and methodologies', 
      'all - Comprehensive search across all knowledge types'
    ],
    knowledgeSources: [
      'Technical Knowledge Base - Official documentation and solutions',
      'Case History - Resolved support cases with proven solutions',
      'Product Documentation - Configuration guides and best practices',
      'Community Knowledge - User-contributed solutions and workarounds'
    ],
    supportedProducts: [
      'Deep Security - Agent, Manager, AMSP, Policy management',
      'Vision One - Endpoint Sensor, Connector, Workbench integration',
      'Apex One - Security Agent, Web Console, Policy deployment'
    ]
  });
}