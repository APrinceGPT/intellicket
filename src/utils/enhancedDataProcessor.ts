// Simplified interfaces for enhanced data processor
interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  type: string;
  category?: string;
  estimated_effort?: string;
}

interface AnalysisData {
  summary: Summary;
  details: Detail[];
  recommendations: Recommendation[];
  componentAnalysis: Record<string, ComponentInfo>;
  rawResults: string;
}

interface Summary {
  totalFiles: number;
  totalLines: number;
  criticalIssues: number;
  errors: number;
  warnings: number;
  healthScore: number;
  status: string;
}

interface Detail {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  component: string;
  count: number;
}

interface ComponentInfo {
  name: string;
  status: string;
  health_score: string | number;
  details: string;
  issues?: string[];
  recommendations?: string[];
  totalEntries?: number;
  errors?: number;
  warnings?: number;
  healthScore?: number;
}

export class RichDataProcessor {
  /**
   * Process backend results and extract structured data
   */
  static processBackendResults(backendData: Record<string, unknown>): AnalysisData | null {
    try {
      console.log('🔍 Processing backend data:', Object.keys(backendData));
      
      // Handle current backend format
      if (backendData.raw_results && typeof backendData.raw_results === 'string') {
        return this.parseRawResults(backendData);
      }
      
      // Handle enhanced format (when backend is upgraded)
      if (backendData.analysis_result || backendData.standardized_results) {
        return this.parseEnhancedFormat(backendData);
      }
      
      // Fallback to HTML parsing
      if (backendData.results && typeof backendData.results === 'string') {
        return this.parseHTMLResults(backendData);
      }
      
      console.warn('⚠️ No compatible data format found');
      return null;
      
    } catch (error) {
      console.error('❌ Error processing backend results:', error);
      return null;
    }
  }
  
  /**
   * Parse raw_results string format (current backend)
   */
  private static parseRawResults(backendData: Record<string, unknown>): AnalysisData {
    const rawText = backendData.raw_results as string;
    console.log('📄 Parsing raw results:', rawText.substring(0, 200) + '...');
    
    // Extract structured data from raw text
    const summary = this.extractSummaryFromRaw(rawText);
    const details = this.extractDetailsFromRaw(rawText);
    const recommendations = this.extractRecommendationsFromRaw(rawText);
    const componentAnalysis = this.extractComponentAnalysisFromHTML((backendData.results as string) || '');
    
    return {
      summary,
      details,
      recommendations,
      componentAnalysis,
      rawResults: rawText
    };
  }
  
  /**
   * Extract summary data from raw text
   */
  private static extractSummaryFromRaw(rawText: string): Summary {
    // Parse metrics from raw text
    const totalLinesMatch = rawText.match(/Total Lines:\s*(\d+)/i);
    const errorsMatch = rawText.match(/Errors Found:\s*(\d+)/i);
    const warningsMatch = rawText.match(/Warnings Found:\s*(\d+)/i);
    const criticalMatch = rawText.match(/Critical Issues:\s*(\d+)/i);
    
    return {
      totalFiles: 1,
      totalLines: totalLinesMatch ? parseInt(totalLinesMatch[1]) : 0,
      criticalIssues: criticalMatch ? parseInt(criticalMatch[1]) : 0,
      errors: errorsMatch ? parseInt(errorsMatch[1]) : 0,
      warnings: warningsMatch ? parseInt(warningsMatch[1]) : 0,
      healthScore: this.calculateHealthScore(
        errorsMatch ? parseInt(errorsMatch[1]) : 0,
        warningsMatch ? parseInt(warningsMatch[1]) : 0
      ),
      status: this.determineStatus(
        criticalMatch ? parseInt(criticalMatch[1]) : 0,
        errorsMatch ? parseInt(errorsMatch[1]) : 0
      )
    };
  }
  
  /**
   * Extract details from raw text
   */
  private static extractDetailsFromRaw(rawText: string): Detail[] {
    const details: Detail[] = [];
    
    // Use fallback regex patterns for better compatibility
    const detailsSection = rawText.match(/Details \((\d+) items\):(.*?)(?=\n\nRecommendations|\n\nDebug|$)/);
    
    if (detailsSection && detailsSection[2]) {
      const lines = detailsSection[2].split('\n').filter(line => line.trim());
      
      lines.forEach((line, index) => {
        const cleanLine = line.trim();
        if (cleanLine && !cleanLine.startsWith('---')) {
          details.push({
            id: `detail_${index + 1}`,
            title: this.extractIssueTitle(cleanLine),
            description: cleanLine,
            severity: this.determineSeverity(cleanLine),
            component: this.extractComponent(cleanLine),
            count: this.extractCount(cleanLine)
          });
        }
      });
    }
    
    return details;
  }
  
  /**
   * Extract recommendations from raw text
   */
  private static extractRecommendationsFromRaw(rawText: string): Recommendation[] {
    const recommendations: Recommendation[] = [];
    
    // Use fallback regex patterns for better compatibility  
    const recSection = rawText.match(/Recommendations \((\d+) items\):(.*?)(?=\n\nDebug|$)/);
    
    if (recSection && recSection[2]) {
      const lines = recSection[2].split('\n').filter(line => line.trim());
      
      lines.forEach((line, index) => {
        const cleanLine = line.trim();
        if (cleanLine && !cleanLine.startsWith('---')) {
          recommendations.push({
            id: `rec_${index + 1}`,
            title: this.extractRecommendationTitle(cleanLine),
            description: cleanLine,
            priority: this.extractPriority(cleanLine),
            type: 'action_item',
            category: this.categorizeRecommendation(cleanLine),
            estimated_effort: '15-30 minutes'
          });
        }
      });
    }
    
    return recommendations;
  }
  
  /**
   * Extract component analysis from HTML results
   */
  private static extractComponentAnalysisFromHTML(htmlResults: string): Record<string, ComponentInfo> {
    const components: Record<string, ComponentInfo> = {};
    
    // Use fallback regex patterns for better compatibility
    const tableMatches = htmlResults.match(/<tr[^>]*>.*?<td[^>]*><strong>(.*?)<\/strong>.*?<td[^>]*>(\d+).*?<td[^>]*>(\d+).*?<td[^>]*>(\d+).*?<td[^>]*>.*?>(.*?)<\/.*?<\/tr>/g);
    
    if (tableMatches) {
      tableMatches.forEach((match) => {
        const parts = match.match(/<strong>(.*?)<\/strong>.*?<td[^>]*>(\d+).*?<td[^>]*>(\d+).*?<td[^>]*>(\d+).*?<td[^>]*>.*?>(.*?)</);
        
        if (parts && parts.length >= 5) {
          const [, name, totalEntries, errors, warnings, status] = parts;
          const componentName = name.trim();
          
          components[componentName] = {
            name: componentName,
            status: this.parseComponentStatus(status),
            health_score: this.calculateComponentHealth(parseInt(errors), parseInt(warnings)),
            details: `${totalEntries} total entries, ${errors} errors, ${warnings} warnings`,
            totalEntries: parseInt(totalEntries),
            errors: parseInt(errors),
            warnings: parseInt(warnings),
            healthScore: this.calculateComponentHealth(parseInt(errors), parseInt(warnings))
          };
        }
      });
    }
    
    return components;
  }
  
  private static parseEnhancedFormat(backendData: Record<string, unknown>): AnalysisData {
    // Future implementation for enhanced backend format
    return {
      summary: { totalFiles: 0, totalLines: 0, criticalIssues: 0, errors: 0, warnings: 0, healthScore: 0, status: 'unknown' },
      details: [],
      recommendations: [],
      componentAnalysis: {},
      rawResults: JSON.stringify(backendData)
    };
  }
  
  private static parseHTMLResults(backendData: Record<string, unknown>): AnalysisData {
    // Fallback HTML parsing implementation
    return {
      summary: { totalFiles: 0, totalLines: 0, criticalIssues: 0, errors: 0, warnings: 0, healthScore: 0, status: 'unknown' },
      details: [],
      recommendations: [],
      componentAnalysis: {},
      rawResults: backendData.results as string || ''
    };
  }
  
  // Helper methods
  private static calculateHealthScore(errors: number, warnings: number): number {
    if (errors > 0) return Math.max(10, 50 - (errors * 5));
    if (warnings > 20) return Math.max(60, 80 - Math.floor(warnings / 10));
    if (warnings > 0) return Math.max(75, 90 - warnings);
    return 95;
  }
  
  private static determineStatus(criticalIssues: number, errors: number): string {
    if (criticalIssues > 0) return 'CRITICAL';
    if (errors > 0) return 'WARNING';
    return 'HEALTHY';
  }
  
  private static extractIssueTitle(text: string): string {
    const titleMatch = text.match(/^([^:]+)/);
    return titleMatch ? titleMatch[1].trim() : text.substring(0, 50);
  }
  
  private static determineSeverity(text: string): 'critical' | 'high' | 'medium' | 'low' {
    if (text.toLowerCase().includes('critical') || text.toLowerCase().includes('error')) return 'critical';
    if (text.toLowerCase().includes('warning')) return 'medium';
    return 'low';
  }
  
  private static extractComponent(text: string): string {
    const componentMatch = text.match(/\b(AMSP|Agent|Web Reputation|Device Control|Firewall|Anti[- ]?Malware)\b/i);
    return componentMatch ? componentMatch[1] : 'General';
  }
  
  private static extractCount(text: string): number {
    const countMatch = text.match(/\((\d+)\s+occurrences?\)/i);
    return countMatch ? parseInt(countMatch[1]) : 1;
  }
  
  private static extractRecommendationTitle(text: string): string {
    // Extract emoji and first part as title
    const titleMatch = text.match(/^((?:[🎯📊🤖⚠️✅❓]|\<i[^>]*\>.*?\<\/i\>)?\s*[^.!?]*)/);
    return titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '').trim() : text.substring(0, 60);
  }
  
  private static extractPriority(text: string): 'critical' | 'high' | 'medium' | 'low' {
    if (text.toLowerCase().includes('critical') || text.toLowerCase().includes('immediate')) return 'critical';
    if (text.toLowerCase().includes('high') || text.includes('🔴')) return 'high';
    if (text.toLowerCase().includes('medium') || text.includes('⚠️')) return 'medium';
    return 'low';
  }
  
  private static categorizeRecommendation(text: string): string {
    if (text.includes('Component Health') || text.includes('Agent Health')) return 'Health';
    if (text.includes('automation') || text.includes('🤖')) return 'Automation';
    if (text.includes('configuration') || text.includes('policy')) return 'Configuration';
    if (text.includes('troubleshooting') || text.includes('🎯')) return 'Troubleshooting';
    return 'General';
  }
  
  private static parseComponentStatus(statusHtml: string): 'healthy' | 'warning' | 'error' | 'critical' {
    if (statusHtml.includes('text-success') || statusHtml.includes('Healthy')) return 'healthy';
    if (statusHtml.includes('text-warning') || statusHtml.includes('warning')) return 'warning';
    if (statusHtml.includes('text-danger') || statusHtml.includes('error')) return 'error';
    return 'healthy';
  }
  
  private static calculateComponentHealth(errors: number, warnings: number): number {
    if (errors > 0) return Math.max(15, 50 - (errors * 10));
    if (warnings > 10) return Math.max(60, 80 - Math.floor(warnings / 5));
    if (warnings > 0) return Math.max(75, 90 - warnings);
    return 95;
  }
}
