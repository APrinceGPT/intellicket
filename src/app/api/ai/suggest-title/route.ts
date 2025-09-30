import { NextRequest, NextResponse } from 'next/server';

interface TitleSuggestionRequest {
  description: string;
  product: string;
  category: string;
  severity?: string;
}

interface TitleSuggestion {
  suggestedTitle: string;
  confidence: number;
  reasoning: string;
  keywords: string[];
}

interface TitleSuggestionResponse {
  suggestions: TitleSuggestion[];
  fallbackTitle?: string;
}

// AI-powered title generation using Claude-like analysis
function generateSmartTitle(request: TitleSuggestionRequest): TitleSuggestionResponse {
  const { description, product, category, severity } = request;
  
  if (!description || description.trim().length < 10) {
    return {
      suggestions: [],
      fallbackTitle: `${product} ${category} - Please provide more details`
    };
  }

  const descriptionLower = description.toLowerCase();
  
  // Extract key technical terms and components
  const technicalTerms = extractTechnicalTerms(descriptionLower);
  const symptoms = extractSymptoms(descriptionLower);
  const components = extractComponents(descriptionLower, product);
  const errorTypes = extractErrorTypes(descriptionLower);
  
  // Generate multiple title suggestions
  const suggestions: TitleSuggestion[] = [];
  
  // Pattern 1: Connectivity/Offline Issues (HIGHEST PRIORITY)
  if (hasConnectivityIssues(descriptionLower)) {
    const connectivityType = getConnectivityIssueType(descriptionLower);
    const component = components[0] || 'Agent';
    const baseTitle = `${component} ${connectivityType}${symptoms.length > 0 && !symptoms[0].includes('offline') ? ` - ${capitalizeFirst(symptoms[0])}` : ''}`;
    
    suggestions.push({
      suggestedTitle: formatTitleWithProduct(baseTitle, product, severity),
      confidence: 0.95,
      reasoning: `Detected connectivity/offline issue requiring immediate investigation${severity === 'Critical' || severity === 'High' ? ` (Marked as ${severity} priority)` : ''}`,
      keywords: [connectivityType.toLowerCase(), component.toLowerCase(), ...technicalTerms.slice(0, 2)]
    });
  }
  
  // Pattern 2: Component + Issue + Symptom
  if (components.length > 0 && symptoms.length > 0) {
    const component = components[0];
    const symptom = symptoms[0];
    const baseTitle = `${component} ${getIssueTypeFromSymptom(symptom)} - ${capitalizeFirst(symptom)}`;
    
    suggestions.push({
      suggestedTitle: formatTitleWithProduct(baseTitle, product, severity),
      confidence: 0.9,
      reasoning: `Identified main component (${component}) and primary symptom (${symptom})${severity === 'Critical' || severity === 'High' ? ` (Marked as ${severity} priority)` : ''}`,
      keywords: [component, symptom, ...technicalTerms.slice(0, 2)]
    });
  }
  
  // Pattern 2: Error-focused title
  if (errorTypes.length > 0) {
    const errorType = errorTypes[0];
    const contextComponent = components[0] || product;
    const baseTitle = `${contextComponent} ${errorType} Error${symptoms.length > 0 ? ` - ${capitalizeFirst(symptoms[0])}` : ''}`;
    
    suggestions.push({
      suggestedTitle: formatTitleWithProduct(baseTitle, product, severity),
      confidence: 0.85,
      reasoning: `Focused on primary error type (${errorType}) with context${severity === 'Critical' || severity === 'High' ? ` (Marked as ${severity} priority)` : ''}`,
      keywords: [errorType, contextComponent]
    });
  }
  
  // Pattern 3: Symptom + Product + Category
  if (symptoms.length > 0) {
    const primarySymptom = symptoms[0];
    const baseTitle = `${product} ${capitalizeFirst(primarySymptom)} Issue${components.length > 0 ? ` - ${components[0]} Related` : ''}`;
    
    suggestions.push({
      suggestedTitle: formatTitleWithProduct(baseTitle, product, severity),
      confidence: 0.75,
      reasoning: `Based on primary symptom and product context${severity === 'Critical' || severity === 'High' ? ` (Marked as ${severity} priority)` : ''}`,
      keywords: [primarySymptom, product]
    });
  }
  
  // Pattern 4: Performance-focused title
  if (hasPerformanceIssues(descriptionLower)) {
    const perfType = getPerformanceIssueType(descriptionLower);
    const component = components[0] || product;
    const baseTitle = `${component} Performance Issue - ${perfType}`;
    
    suggestions.push({
      suggestedTitle: formatTitleWithProduct(baseTitle, product, severity),
      confidence: 0.8,
      reasoning: `Detected performance-related issue requiring optimization${severity === 'Critical' || severity === 'High' ? ` (Marked as ${severity} priority)` : ''}`,
      keywords: [perfType, 'performance']
    });
  }
  
  // Pattern 5: Security-focused title (only if no connectivity issues detected)
  if (!hasConnectivityIssues(descriptionLower) && hasSecurityIssues(descriptionLower)) {
    const securityType = getSecurityIssueType(descriptionLower);
    const component = components[0] || product;
    const baseTitle = `${component} Security ${securityType}${components.length > 0 ? ` - ${components[0]}` : ''}`;
    
    suggestions.push({
      suggestedTitle: formatTitleWithProduct(baseTitle, product, severity),
      confidence: 0.85,
      reasoning: `Security-related issue requiring immediate attention${severity === 'Critical' || severity === 'High' ? ` (Marked as ${severity} priority)` : ''}`,
      keywords: [securityType, 'security']
    });
  }
  
  // Sort by confidence and return top 3
  suggestions.sort((a, b) => b.confidence - a.confidence);
  
  return {
    suggestions: suggestions.slice(0, 3),
    fallbackTitle: suggestions.length === 0 ? generateFallbackTitle(description, product, category) : undefined
  };
}

// Helper functions for content analysis
function extractTechnicalTerms(description: string): string[] {
  const patterns = [
    /(?:ds\s*agent|deep\s*security\s*agent)/gi,
    // /(?:amsp|anti-malware)/gi, // AMSP patterns disabled
    /(?:dsm|deep\s*security\s*manager)/gi,
    /(?:notifier|notification)/gi,
    /(?:web\s*reputation|trendx)/gi,
    /(?:ips|intrusion\s*prevention)/gi,
    /(?:fim|file\s*integrity)/gi,
    /(?:real-time\s*scan|ors)/gi,
    /(?:scheduled\s*scan)/gi,
    /(?:quarantine)/gi
  ];
  
  const terms: string[] = [];
  patterns.forEach(pattern => {
    const matches = description.match(pattern);
    if (matches) {
      matches.forEach(match => {
        const normalized = normalizeComponent(match.trim());
        if (normalized && !terms.includes(normalized)) {
          terms.push(normalized);
        }
      });
    }
  });
  
  return terms;
}

function extractSymptoms(description: string): string[] {
  const symptomPatterns = [
    // Connectivity/Offline issues (high priority)
    /(?:offline|disconnected|not\s*connected|connection\s*lost)/gi,
    /(?:agent\s*(?:is\s*)?offline|agent\s*disconnected)/gi,
    /(?:communication\s*(?:failed|lost|error)|cannot\s*communicate)/gi,
    /(?:not\s*reporting|status\s*unknown|heartbeat\s*lost)/gi,
    
    // Service/Startup issues
    /(?:not\s*(?:starting|working|responding)|fails?\s*to\s*start)/gi,
    /(?:service\s*(?:stopped|stopping|not\s*running|failed))/gi,
    /(?:startup\s*(?:failed|error)|failed\s*to\s*(?:start|launch))/gi,
    
    // Performance issues
    /(?:high\s*cpu|cpu\s*usage|consuming\s*cpu)/gi,
    /(?:memory\s*leak|high\s*memory|memory\s*usage)/gi,
    /(?:slow|sluggish|performance\s*issue)/gi,
    
    // Stability issues
    /(?:crashing|crashes|crash)/gi,
    /(?:hanging|frozen|freeze)/gi,
    /(?:timeout|timed?\s*out)/gi,
    /(?:error|exception|fault)/gi
  ];
  
  const symptoms: string[] = [];
  symptomPatterns.forEach(pattern => {
    const matches = description.match(pattern);
    if (matches) {
      matches.forEach(match => {
        const normalized = normalizeSymptom(match.trim());
        if (normalized && !symptoms.includes(normalized)) {
          symptoms.push(normalized);
        }
      });
    }
  });
  
  return symptoms;
}

function extractComponents(description: string, product: string): string[] {
  const componentMap: { [key: string]: string[] } = {
    'Deep Security': [
      'DS Agent', /*'AMSP',*/ 'DSM', 'Notifier', 'Web Reputation', 
      'IPS', 'File Integrity', 'Real-time Scan', 'Scheduled Scan'
    ],
    'Apex One': [
      'Apex Agent', 'Security Server', 'Web Console', 'Pattern Update',
      'Real-time Scan', 'Scheduled Scan', 'Behavior Monitoring'
    ]
  };
  
  const components = componentMap[product] || [];
  const found: string[] = [];
  
  components.forEach(component => {
    const pattern = new RegExp(component.replace(/\s+/g, '\\s*'), 'gi');
    if (pattern.test(description)) {
      found.push(component);
    }
  });
  
  return found;
}

function extractErrorTypes(description: string): string[] {
  const errorPatterns = [
    /connection\s*error/gi,
    /authentication\s*(?:error|failed)/gi,
    /certificate\s*(?:error|invalid|expired)/gi,
    /permission\s*(?:denied|error)/gi,
    /file\s*not\s*found/gi,
    /access\s*denied/gi,
    /installation\s*(?:error|failed)/gi,
    /update\s*(?:error|failed)/gi,
    /configuration\s*error/gi,
    /database\s*(?:error|connection)/gi
  ];
  
  const errors: string[] = [];
  errorPatterns.forEach(pattern => {
    const matches = description.match(pattern);
    if (matches) {
      matches.forEach(match => {
        const normalized = normalizeErrorType(match.trim());
        if (normalized && !errors.includes(normalized)) {
          errors.push(normalized);
        }
      });
    }
  });
  
  return errors;
}

function getIssueTypeFromSymptom(symptom: string): string {
  // Connectivity/Communication issues (priority handling)
  if (symptom.includes('offline') || symptom.includes('disconnected') || 
      symptom.includes('not connected') || symptom.includes('communication failed') ||
      symptom.includes('not reporting') || symptom.includes('heartbeat lost')) {
    return 'Connectivity Issue';
  }
  
  // Service/Startup issues
  if (symptom.includes('not starting') || symptom.includes('service stopped') ||
      symptom.includes('startup failed') || symptom.includes('service failed')) {
    return 'Service Issue';
  }
  
  // Performance issues
  if (symptom.includes('high cpu') || symptom.includes('memory') || 
      symptom.includes('slow') || symptom.includes('performance')) {
    return 'Performance Issue';
  }
  
  // Stability issues
  if (symptom.includes('crash') || symptom.includes('hanging') || 
      symptom.includes('frozen') || symptom.includes('timeout')) {
    return 'Stability Issue';
  }
  
  // Connection issues (network-level)
  if (symptom.includes('connection') || symptom.includes('timeout')) {
    return 'Connection Issue';
  }
  
  // Error-related issues
  if (symptom.includes('error') || symptom.includes('exception') || 
      symptom.includes('fault')) {
    return 'Error Condition';
  }
  
  return 'Functionality Issue';
}

function hasPerformanceIssues(description: string): boolean {
  return /(?:slow|performance|cpu|memory|lag|freeze|hang|resource)/i.test(description);
}

function getPerformanceIssueType(description: string): string {
  if (/high\s*cpu|cpu\s*usage/i.test(description)) return 'High CPU Usage';
  if (/memory\s*leak|high\s*memory/i.test(description)) return 'Memory Issues';
  if (/slow|sluggish/i.test(description)) return 'Slow Performance';
  if (/hang|freeze|frozen/i.test(description)) return 'System Hanging';
  return 'Performance Degradation';
}

function hasSecurityIssues(description: string): boolean {
  return /(?:malware|virus|threat|quarantine|blocked|security|attack|breach)/i.test(description);
}

function getSecurityIssueType(description: string): string {
  if (/malware|virus/i.test(description)) return 'Malware Detection';
  if (/quarantine/i.test(description)) return 'Quarantine Issue';
  if (/blocked|blocking/i.test(description)) return 'Blocking Issue';
  if (/threat|attack/i.test(description)) return 'Threat Detection';
  return 'Security Event';
}

// Connectivity/Offline detection functions
function hasConnectivityIssues(description: string): boolean {
  return /(?:offline|disconnected|not\s*connected|connection\s*lost|communication\s*(?:failed|lost|error)|cannot\s*communicate|not\s*reporting|status\s*unknown|heartbeat\s*lost|agent\s*(?:is\s*)?offline|manager\s*communication|policy\s*deployment\s*(?:failed|blocked)|cannot\s*(?:reach|contact)|unreachable)/i.test(description);
}

function getConnectivityIssueType(description: string): string {
  if (/agent\s*(?:is\s*)?offline|show\s*as\s*offline|showing\s*offline/i.test(description)) return 'Offline Status';
  if (/disconnected|not\s*connected|connection\s*lost/i.test(description)) return 'Connection Lost';
  if (/communication\s*(?:failed|lost|error)|cannot\s*communicate|fails?\s*to\s*communicate/i.test(description)) return 'Communication Failure';
  if (/not\s*reporting|status\s*unknown/i.test(description)) return 'Reporting Issue';
  if (/heartbeat\s*lost/i.test(description)) return 'Heartbeat Lost';
  if (/policy\s*deployment\s*(?:failed|blocked)|preventing\s*policy/i.test(description)) return 'Policy Deployment Issue';
  if (/cannot\s*(?:reach|contact)|unreachable/i.test(description)) return 'Unreachable';
  return 'Connectivity Issue';
}

// Normalization functions
function normalizeComponent(component: string): string {
  const normalizations: { [key: string]: string } = {
    'ds agent': 'DS Agent',
    'deep security agent': 'DS Agent',
    // 'amsp': 'AMSP', // AMSP normalization disabled
    // 'anti-malware': 'AMSP', // AMSP normalization disabled
    'dsm': 'DSM',
    'deep security manager': 'DSM',
    'notifier': 'Notifier',
    'web reputation': 'Web Reputation',
    'trendx': 'Web Reputation',
    'ips': 'IPS',
    'intrusion prevention': 'IPS',
    'fim': 'File Integrity',
    'file integrity': 'File Integrity'
  };
  
  return normalizations[component.toLowerCase()] || component;
}

function normalizeSymptom(symptom: string): string {
  const normalizations: { [key: string]: string } = {
    // Connectivity/Offline issues
    'offline': 'offline status',
    'agent is offline': 'agent offline',
    'agent offline': 'agent offline',
    'disconnected': 'disconnected',
    'not connected': 'connection lost',
    'connection lost': 'connection lost',
    'communication failed': 'communication failure',
    'cannot communicate': 'communication failure',
    'not reporting': 'not reporting status',
    'status unknown': 'status unknown',
    'heartbeat lost': 'heartbeat lost',
    
    // Service/Startup issues
    'not starting': 'service not starting',
    'not working': 'not functioning properly',
    'fails to start': 'service startup failure',
    'service stopped': 'service stopped unexpectedly',
    'service failed': 'service failure',
    'startup failed': 'startup failure',
    
    // Performance issues
    'high cpu': 'high CPU usage',
    'cpu usage': 'high CPU usage',
    'memory leak': 'memory leak detected',
    'high memory': 'high memory usage',
    'slow': 'slow performance',
    'sluggish': 'slow performance',
    'performance issue': 'performance degradation',
    
    // Connection issues
    'connection failed': 'connection failure',
    'timeout': 'timeout error',
    'timed out': 'timeout error',
    
    // Stability issues
    'crash': 'application crash',
    'crashing': 'frequent crashes',
    'hanging': 'system hanging',
    'frozen': 'system frozen',
    'freeze': 'system freeze'
  };
  
  return normalizations[symptom.toLowerCase()] || symptom.toLowerCase();
}

function normalizeErrorType(errorType: string): string {
  const normalizations: { [key: string]: string } = {
    'connection error': 'Connection',
    'authentication error': 'Authentication',
    'certificate error': 'Certificate',
    'permission denied': 'Permission',
    'file not found': 'File Not Found',
    'installation error': 'Installation',
    'configuration error': 'Configuration'
  };
  
  return normalizations[errorType.toLowerCase()] || errorType;
}

function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Product initials mapping for standardized case title formatting
function getProductInitials(product: string): string {
  const productInitials: { [key: string]: string } = {
    'Deep Security': 'DS',
    'Apex One': 'AO',
    'Vision One': 'V1',
    'Service Gateway': 'SG',
    'Cloud Conformity': 'CC',
    'Cloud One': 'C1',
    'Worry-Free Business Security': 'WFBS',
    'ServerProtect': 'SP',
    'ScanMail': 'SM',
    'InterScan': 'IS',
    'TippingPoint': 'TP',
    'Email Security': 'ES',
    'Deep Discovery': 'DD'
  };
  
  return productInitials[product] || product.substring(0, 2).toUpperCase();
}

// Apply product initials and severity formatting to title
function formatTitleWithProduct(title: string, product: string, severity?: string): string {
  const productInitials = getProductInitials(product);
  
  // Remove existing product name if it exists in the title
  let formattedTitle = title;
  const productNames = [product, productInitials];
  productNames.forEach(name => {
    const regex = new RegExp(`^${name}\\s*`, 'i');
    formattedTitle = formattedTitle.replace(regex, '');
  });
  
  // Remove existing severity prefix if it exists
  formattedTitle = formattedTitle.replace(/^\[(?:Critical|High|Medium|Low)\]\s*/i, '');
  
  // Build the final formatted title
  let finalTitle = `[${productInitials}] ${formattedTitle}`;
  
  // Add severity prefix if provided and it's Critical or High
  if (severity === 'Critical' || severity === 'High') {
    finalTitle = `[${severity}] ${finalTitle}`;
  }
  
  return finalTitle;
}

function generateFallbackTitle(description: string, product: string, category: string): string {
  // Extract first meaningful phrase (up to 50 characters)
  const firstSentence = description.split(/[.!?]/)[0];
  const shortDesc = firstSentence.length > 50 
    ? firstSentence.substring(0, 47) + '...'
    : firstSentence;
  
  return `${product} ${category} - ${capitalizeFirst(shortDesc)}`;
}

export async function POST(request: NextRequest) {
  try {
    const body: TitleSuggestionRequest = await request.json();
    
    // Validate required fields
    if (!body.description || !body.product || !body.category) {
      return NextResponse.json(
        { error: 'Description, product, and category are required' },
        { status: 400 }
      );
    }
    
    // Generate smart title suggestions
    const result = generateSmartTitle(body);
    
    // Add artificial delay to simulate AI processing
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return NextResponse.json(result);
    
  } catch (error) {
    console.error('Error generating title suggestions:', error);
    return NextResponse.json(
      { error: 'Failed to generate title suggestions' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Smart Title Suggestion Service is running',
    capabilities: [
      'Component-based title generation',
      'Symptom extraction and analysis', 
      'Error type detection',
      'Performance issue identification',
      'Security issue recognition',
      'Severity-aware suggestions'
    ]
  });
}
