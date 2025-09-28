'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';

// Simple icon component fallback
interface IconProps {
  className?: string;
}

const SimpleIcon: React.FC<IconProps> = ({ className = "w-4 h-4" }) => (
  <div className={`inline-block ${className}`} 
       style={{ 
         width: '1rem', 
         height: '1rem', 
         backgroundColor: 'currentColor',
         borderRadius: '2px'
       }} 
  />
);

// Icon components - using simple fallbacks for compatibility
const Loader2: React.FC<IconProps> = ({ className }) => <SimpleIcon className={`${className} animate-spin`} />;
const Lightbulb: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const Search: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const FileText: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const AlertTriangle: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const Clock: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const TrendingUp: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const Brain: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const Zap: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;
const Target: React.FC<IconProps> = ({ className }) => <SimpleIcon className={className} />;

interface AnalyzerInfo {
  name: string;
  description: string;
}

interface AIInsight {
  id: string;
  type: 'suggestion' | 'warning' | 'optimization' | 'knowledge' | 'prediction';
  title: string;
  content: string;
  confidence: number;
  relevance: number;
  actionable: boolean;
  implementation?: {
    steps: string[];
    effort: 'Low' | 'Medium' | 'High';
    riskLevel: 'Low' | 'Medium' | 'High';
    estimatedTime: string;
  };
}

interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  relevanceScore: number;
  source: string;
  type: string;
  tags: string[];
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
  successRate: number;
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

interface AICaseAssistantProps {
  caseData: {
    title?: string;
    description?: string;
    product?: string;
    category?: string;
    severity?: string;
    attachedFiles?: Array<{
      name: string;
      size: number;
      type: string;
      content?: string;
    }>;
  };
  onSuggestionApplied?: (suggestion: AIInsight) => void;
  onKnowledgeSelected?: (knowledge: KnowledgeItem) => void;
  onSolutionSelected?: (solution: ProactiveSolution) => void;
  className?: string;
}

type TabType = 'insights' | 'knowledge' | 'solutions' | 'cases';

export function AICaseAssistant({
  caseData,
  onSuggestionApplied,
  onKnowledgeSelected,
  onSolutionSelected,
  className = ''
}: AICaseAssistantProps) {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [knowledgeResults, setKnowledgeResults] = useState<KnowledgeSearchResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('insights');
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const analysisRef = useRef<NodeJS.Timeout | null>(null);

  const generateAIInsights = useCallback(async () => {
    try {
      const caseAnalysisResponse = await fetch('/api/ai/analyze-case-enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: caseData.title || '',
          description: caseData.description || '',
          product: caseData.product || 'Deep Security',
          category: caseData.category || 'Product Issue',
          severity: caseData.severity || 'Medium',
          attachedFiles: caseData.attachedFiles || []
        }),
      });

      if (caseAnalysisResponse.ok) {
        const analysis = await caseAnalysisResponse.json();
        const newInsights: AIInsight[] = [];

        if (analysis.complexity) {
          newInsights.push({
            id: `complexity_${Date.now()}`,
            type: 'prediction',
            title: `Case Complexity Assessment: ${analysis.complexity.level}`,
            content: `This case is assessed as ${analysis.complexity.level.toLowerCase()} complexity with ${analysis.complexity.factors.length} contributing factors. Expected resolution effort: ${analysis.complexity.estimatedEffort}.`,
            confidence: 85,
            relevance: 90,
            actionable: true,
            implementation: {
              steps: analysis.complexity.factors.slice(0, 3),
              effort: analysis.complexity.level as 'Low' | 'Medium' | 'High',
              riskLevel: 'Low',
              estimatedTime: analysis.complexity.estimatedEffort
            }
          });
        }

        if (analysis.recommendedAnalyzers) {
          newInsights.push({
            id: `analyzers_${Date.now()}`,
            type: 'suggestion',
            title: 'Recommended Analysis Tools',
            content: `Based on case symptoms, ${analysis.recommendedAnalyzers.length} specialized analyzers are recommended for deep investigation.`,
            confidence: 90,
            relevance: 95,
            actionable: true,
            implementation: {
              steps: analysis.recommendedAnalyzers.map((analyzer: AnalyzerInfo) => 
                `Run ${analyzer.name}: ${analyzer.description}`
              ),
              effort: 'Medium',
              riskLevel: 'Low',
              estimatedTime: '30-60 minutes'
            }
          });
        }

        setInsights(newInsights);
      }
    } catch (error) {
      console.error('Error generating AI insights:', error);
    }
  }, [caseData]);

  const searchKnowledgeBase = useCallback(async () => {
    if (!caseData.title && !caseData.description) return;
    
    try {
      const searchQuery = [caseData.title, caseData.description]
        .filter(Boolean)
        .join(' ')
        .slice(0, 200);

      const response = await fetch('/api/ai/search-knowledge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          product: caseData.product || 'Deep Security',
          category: caseData.category,
          severity: caseData.severity,
          maxResults: 10,
          searchType: 'all'
        }),
      });

      if (response.ok) {
        const knowledgeData: KnowledgeSearchResult = await response.json();
        setKnowledgeResults(knowledgeData);
      }
    } catch (error) {
      console.error('Error searching knowledge base:', error);
    }
  }, [caseData]);

  const performComprehensiveAnalysis = useCallback(async () => {
    if (!caseData.title && !caseData.description) return;
    
    setIsAnalyzing(true);
    try {
      await Promise.all([
        generateAIInsights(),
        searchKnowledgeBase()
      ]);
    } catch (error) {
      console.error('Error during comprehensive analysis:', error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [caseData, generateAIInsights, searchKnowledgeBase]);

  useEffect(() => {
    if (autoRefresh && (caseData.title || caseData.description || caseData.attachedFiles?.length)) {
      if (analysisRef.current) {
        clearTimeout(analysisRef.current);
      }
      
      analysisRef.current = setTimeout(() => {
        performComprehensiveAnalysis();
      }, 1000);
    }
    
    return () => {
      if (analysisRef.current) {
        clearTimeout(analysisRef.current);
      }
    };
  }, [caseData, autoRefresh, performComprehensiveAnalysis]);

  const toggleExpanded = (id: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedItems(newExpanded);
  };

  const applySuggestion = (insight: AIInsight) => {
    onSuggestionApplied?.(insight);
    
    const successInsight: AIInsight = {
      id: `applied_${Date.now()}`,
      type: 'optimization',
      title: 'AI Suggestion Applied',
      content: `Successfully applied: ${insight.title}`,
      confidence: 100,
      relevance: 100,
      actionable: false
    };
    
    setInsights(prev => [successInsight, ...prev]);
  };

  const getInsightIcon = (type: AIInsight['type']) => {
    switch (type) {
      case 'suggestion': return <Lightbulb className="w-4 h-4 text-yellow-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'optimization': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'knowledge': return <FileText className="w-4 h-4 text-blue-500" />;
      case 'prediction': return <Brain className="w-4 h-4 text-purple-500" />;
      default: return <Zap className="w-4 h-4 text-gray-500" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600 bg-green-50';
    if (confidence >= 75) return 'text-yellow-600 bg-yellow-50';
    if (confidence >= 60) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'Low': return 'text-green-600 bg-green-50';
      case 'Medium': return 'text-yellow-600 bg-yellow-50';
      case 'High': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">AI Case Assistant</h3>
            {isAnalyzing && <Loader2 className="w-4 h-4 animate-spin text-blue-600" />}
          </div>
          
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-gray-600">Auto-analyze</span>
            </label>
            
            <button
              onClick={performComprehensiveAnalysis}
              disabled={isAnalyzing}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        <div className="flex space-x-4 mt-3">
          {[
            { id: 'insights', label: 'AI Insights', count: insights.length },
            { id: 'knowledge', label: 'Knowledge Base', count: knowledgeResults?.knowledgeItems.length || 0 },
            { id: 'solutions', label: 'Solutions', count: knowledgeResults?.proactiveSolutions.length || 0 },
            { id: 'cases', label: 'Related Cases', count: knowledgeResults?.relatedCases.length || 0 }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`px-3 py-1 text-sm rounded-md ${
                activeTab === tab.id
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-gray-100 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="p-4 max-h-96 overflow-y-auto">
        {activeTab === 'insights' && (
          <div className="space-y-3">
            {insights.length === 0 && !isAnalyzing && (
              <div className="text-center py-6 text-gray-500">
                <Brain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No AI insights yet. Start typing case details to get intelligent assistance.</p>
              </div>
            )}
            
            {insights.map(insight => (
              <div
                key={insight.id}
                className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-2 flex-1">
                    {getInsightIcon(insight.type)}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-900">{insight.title}</h4>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getConfidenceColor(insight.confidence)}`}>
                          {insight.confidence}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{insight.content}</p>
                      
                      {insight.implementation && expandedItems.has(insight.id) && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-md">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Implementation Details</span>
                            <div className="flex space-x-2">
                              <span className={`px-2 py-0.5 text-xs rounded-full ${getRiskLevelColor(insight.implementation.riskLevel)}`}>
                                {insight.implementation.riskLevel} Risk
                              </span>
                              <span className="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-600">
                                {insight.implementation.estimatedTime}
                              </span>
                            </div>
                          </div>
                          <ol className="text-sm text-gray-600 space-y-1">
                            {insight.implementation.steps.map((step, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <span className="text-gray-400 font-mono">{index + 1}.</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-1 ml-2">
                    {insight.implementation && (
                      <button
                        onClick={() => toggleExpanded(insight.id)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title={expandedItems.has(insight.id) ? 'Hide details' : 'Show details'}
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                    )}
                    
                    {insight.actionable && (
                      <button
                        onClick={() => applySuggestion(insight)}
                        className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                        title="Apply this suggestion"
                      >
                        Apply
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'knowledge' && (
          <div className="space-y-3">
            {!knowledgeResults?.knowledgeItems.length && !isAnalyzing && (
              <div className="text-center py-6 text-gray-500">
                <Search className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No knowledge base results yet. Case analysis will automatically search for relevant articles.</p>
              </div>
            )}
            
            {knowledgeResults?.knowledgeItems.map(item => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900">{item.title}</h4>
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getConfidenceColor(item.relevanceScore)}`}>
                        {item.relevanceScore}% relevant
                      </span>
                      <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                        {item.source}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{item.content.substring(0, 200)}...</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {item.tags.slice(0, 4).map(tag => (
                        <span key={tag} className="px-2 py-0.5 text-xs bg-blue-50 text-blue-600 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => onKnowledgeSelected?.(item)}
                    className="ml-2 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Use
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'solutions' && (
          <div className="space-y-3">
            {!knowledgeResults?.proactiveSolutions.length && !isAnalyzing && (
              <div className="text-center py-6 text-gray-500">
                <Target className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No proactive solutions generated yet. Complete case analysis will provide tailored solutions.</p>
              </div>
            )}
            
            {knowledgeResults?.proactiveSolutions.map(solution => (
              <div key={solution.solutionId} className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900">{solution.title}</h4>
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getConfidenceColor(solution.confidence)}`}>
                        {solution.confidence}% confidence
                      </span>
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getRiskLevelColor(solution.riskLevel)}`}>
                        {solution.riskLevel} risk
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{solution.description}</p>
                  </div>
                  
                  <button
                    onClick={() => onSolutionSelected?.(solution)}
                    className="ml-2 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'cases' && (
          <div className="space-y-3">
            {!knowledgeResults?.relatedCases.length && !isAnalyzing && (
              <div className="text-center py-6 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No related cases found yet. Case analysis will find similar resolved cases.</p>
              </div>
            )}
            
            {knowledgeResults?.relatedCases.map(caseItem => (
              <div key={caseItem.caseId} className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900">{caseItem.title}</h4>
                      <span className={`px-2 py-0.5 text-xs rounded-full ${getConfidenceColor(caseItem.similarity)}`}>
                        {caseItem.similarity}% similar
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{caseItem.description}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>Product: {caseItem.product}</span>
                      <span>Severity: {caseItem.severity}</span>
                      <span>Resolved in: {caseItem.resolutionTime}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}