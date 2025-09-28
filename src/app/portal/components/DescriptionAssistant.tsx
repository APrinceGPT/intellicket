'use client';

import { useState, useEffect } from 'react';

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
}

interface QualityImprovement {
  area: string;
  suggestion: string;
  impact: 'High' | 'Medium' | 'Low';
  exampleText?: string;
  completed: boolean;
}

interface DescriptionAssistantProps {
  description: string;
  product: string;
  category: string;
  severity: string;
  caseTitle: string; // Add current case title
  onDescriptionChange: (description: string) => void;
}

export default function DescriptionAssistant({
  description,
  product,
  category,
  severity,
  caseTitle,
  onDescriptionChange
}: DescriptionAssistantProps) {
  const [assessment, setAssessment] = useState<QualityAssessment | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAssistant, setShowAssistant] = useState(false);
  const [expandedSuggestion, setExpandedSuggestion] = useState<number | null>(null);

  // Analyze description quality when it changes
  useEffect(() => {
    if (description.trim().length > 10) {
      const debounceTimer = setTimeout(() => {
        analyzeDescription();
      }, 1000);

      return () => clearTimeout(debounceTimer);
    } else {
      setAssessment(null);
      setShowAssistant(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [description, product, category, severity, caseTitle]); // Include caseTitle in dependencies

  const analyzeDescription = async () => {
    if (description.trim().length < 10) return;

    setIsAnalyzing(true);

    try {
      const response = await fetch('/api/ai/analyze-description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          product,
          category,
          severity,
          caseTitle // Include current case title for context
        }),
      });

      if (response.ok) {
        const analysisResult: QualityAssessment = await response.json();
        setAssessment(analysisResult);
        setShowAssistant(true);
      } else {
        // Fallback to local analysis if API fails
        const fallbackAssessment = performLocalAnalysis(description, product, category, severity);
        setAssessment(fallbackAssessment);
        setShowAssistant(true);
      }
    } catch (error) {
      console.error('Error analyzing description:', error);
      // Fallback to local analysis
      const fallbackAssessment = performLocalAnalysis(description, product, category, severity);
      setAssessment(fallbackAssessment);
      setShowAssistant(true);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const performLocalAnalysis = (desc: string, prod: string, cat: string, sev: string): QualityAssessment => {
    const text = desc.toLowerCase();
    const wordCount = desc.trim().split(/\s+/).length;
    
    // Analyze completeness factors
    const completeness = {
      basicInfo: calculateBasicInfoScore(text, wordCount),
      technicalDetails: calculateTechnicalDetailsScore(text),
      reproductionSteps: calculateReproductionStepsScore(text),
      environmentInfo: calculateEnvironmentInfoScore(text, prod),
      errorMessages: calculateErrorMessagesScore(text)
    };

    // Calculate overall score
    const weights = { basicInfo: 0.2, technicalDetails: 0.25, reproductionSteps: 0.2, environmentInfo: 0.15, errorMessages: 0.2 };
    const overallScore = Math.round(
      Object.entries(completeness).reduce((sum, [key, value]) => {
        return sum + (value * weights[key as keyof typeof weights]);
      }, 0)
    );

    // Generate suggestions
    const suggestions = generateSuggestions(completeness, text, prod, cat, sev);

    // Determine readiness
    const readinessForSubmission = overallScore >= 70 && suggestions.filter(s => s.impact === 'High').length === 0;

    // Estimate resolution time
    const estimatedResolutionTime = estimateResolutionTime(overallScore, sev, text);

    return {
      overallScore,
      completeness,
      suggestions,
      readinessForSubmission,
      estimatedResolutionTime
    };
  };

  const calculateBasicInfoScore = (text: string, wordCount: number): number => {
    let score = 0;
    
    // Word count factor (20-200 words is good)
    if (wordCount >= 20 && wordCount <= 200) score += 40;
    else if (wordCount >= 10 && wordCount < 20) score += 20;
    else if (wordCount > 200) score += 30; // Verbose but informative
    
    // Problem description clarity
    if (/(?:issue|problem|error|fail|not work)/i.test(text)) score += 20;
    if (/(?:when|while|during|after)/i.test(text)) score += 20; // Context
    if (/(?:expect|should|want|need)/i.test(text)) score += 20; // Expected behavior
    
    return Math.min(score, 100);
  };

  const calculateTechnicalDetailsScore = (text: string): number => {
    let score = 0;
    
    // Version numbers
    if (/\d+\.\d+(?:\.\d+)?/g.test(text)) score += 20;
    
    // Error codes or IDs
    if (/(?:error|code|id)[\s:]*\w+\d+/gi.test(text)) score += 25;
    
    // Log file references
    if (/\.log|\.txt|\.xml/gi.test(text)) score += 15;
    
    // Technical components
    if (/(?:service|agent|manager|server|database)/gi.test(text)) score += 20;
    
    // Network/System details
    if (/(?:port|ip|url|path|registry|cpu|memory)/gi.test(text)) score += 20;
    
    return Math.min(score, 100);
  };

  const calculateReproductionStepsScore = (text: string): number => {
    let score = 0;
    
    // Step indicators
    const stepWords = ['step', 'first', 'then', 'next', 'finally', 'after'];
    stepWords.forEach(word => {
      if (new RegExp(word, 'gi').test(text)) score += 15;
    });
    
    // Sequence indicators
    if (/\d+\./g.test(text)) score += 25; // Numbered steps
    if (/(?:reproduce|replicate|recreate)/gi.test(text)) score += 20;
    
    return Math.min(score, 100);
  };

  const calculateEnvironmentInfoScore = (text: string, product: string): number => {
    let score = 20; // Base score for product selection
    
    // Operating system
    if (/(?:windows|linux|centos|ubuntu|rhel|server)/gi.test(text)) score += 25;
    
    // Environment type
    if (/(?:production|development|staging|test)/gi.test(text)) score += 20;
    
    // Infrastructure details
    if (/(?:virtual|vm|container|cloud|aws|azure)/gi.test(text)) score += 15;
    
    // Product-specific components
    if (product.toLowerCase().includes('deep security')) {
      if (/(?:agent|manager|dsm|amsp)/gi.test(text)) score += 20;
    }
    
    return Math.min(score, 100);
  };

  const calculateErrorMessagesScore = (text: string): number => {
    let score = 0;
    
    // Quoted error messages
    if (/"[^"]*error[^"]*"/gi.test(text)) score += 40;
    if (/'[^']*error[^']*'/gi.test(text)) score += 35;
    
    // Error keywords
    if (/(?:failed|exception|timeout|refused|denied)/gi.test(text)) score += 20;
    
    // Stack traces or detailed errors
    if (/(?:stack trace|at line|exception in)/gi.test(text)) score += 30;
    
    // Event log references
    if (/(?:event log|event id|event viewer)/gi.test(text)) score += 15;
    
    return Math.min(score, 100);
  };

  const generateSuggestions = (completeness: QualityAssessment['completeness'], text: string, product: string, category: string, severity: string): QualityImprovement[] => {
    const suggestions: QualityImprovement[] = [];

    if (completeness.basicInfo < 70) {
      suggestions.push({
        area: 'Problem Description',
        suggestion: 'Provide more details about what exactly is happening and what you expected to happen',
        impact: 'High',
        exampleText: 'Example: "The AMSP service stops responding during scheduled scans, causing the scan to fail. I expected the scan to complete successfully."',
        completed: false
      });
    }

    if (completeness.technicalDetails < 60) {
      suggestions.push({
        area: 'Technical Information',
        suggestion: `Include specific version numbers, error codes, and ${product} component details`,
        impact: 'High',
        exampleText: 'Example: "Deep Security Agent 20.0.1.2345, Error Code: DS-40001, AMSP service version 12.5.678"',
        completed: false
      });
    }

    if (completeness.reproductionSteps < 50) {
      suggestions.push({
        area: 'Reproduction Steps',
        suggestion: 'Add step-by-step instructions on how to reproduce this issue',
        impact: 'Medium',
        exampleText: 'Example: "1. Navigate to Administration > System Settings, 2. Click Update Now, 3. Error appears after 30 seconds"',
        completed: false
      });
    }

    if (completeness.environmentInfo < 60) {
      suggestions.push({
        area: 'Environment Details',
        suggestion: 'Include operating system, environment type (production/test), and infrastructure details',
        impact: 'Medium',
        exampleText: 'Example: "Windows Server 2019, Production environment, VMware vSphere 7.0"',
        completed: false
      });
    }

    if (completeness.errorMessages < 40) {
      suggestions.push({
        area: 'Error Messages',
        suggestion: 'Include exact error messages, event log entries, or screenshots of the error',
        impact: severity === 'Critical' || severity === 'High' ? 'High' : 'Medium',
        exampleText: 'Example: "Error message: \'Connection to DSM failed: timeout after 30 seconds\' (Event ID: 1234)"',
        completed: false
      });
    }

    // Additional contextual suggestions
    if (text.includes('slow') || text.includes('performance')) {
      suggestions.push({
        area: 'Performance Context',
        suggestion: 'Include CPU/memory usage details and timeline of when performance issues started',
        impact: 'Low',
        exampleText: 'Example: "CPU usage increased to 80% starting 3 days ago, coinciding with last policy update"',
        completed: false
      });
    }

    return suggestions;
  };

  const estimateResolutionTime = (score: number, severity: string, text: string): string => {
    let baseTime = 48; // hours
    
    // Adjust based on quality
    if (score >= 80) baseTime *= 0.6;
    else if (score >= 60) baseTime *= 0.8;
    else if (score < 40) baseTime *= 1.5;
    
    // Adjust based on severity
    const severityMultiplier = {
      'Critical': 0.25,
      'High': 0.5,
      'Medium': 1.0,
      'Low': 1.5
    };
    
    baseTime *= severityMultiplier[severity as keyof typeof severityMultiplier] || 1.0;
    
    // Adjust based on complexity indicators
    if (text.includes('multiple') || text.includes('various') || text.includes('several')) {
      baseTime *= 1.3;
    }
    
    const hours = Math.round(baseTime);
    if (hours < 24) return `${hours} hours`;
    return `${Math.round(hours / 24)} days`;
  };

  const applySuggestion = (index: number, suggestion: QualityImprovement) => {
    if (suggestion.exampleText) {
      const newDescription = description + '\n\n' + suggestion.exampleText;
      onDescriptionChange(newDescription);
      
      // Mark suggestion as completed
      if (assessment) {
        const updatedSuggestions = [...assessment.suggestions];
        updatedSuggestions[index].completed = true;
        setAssessment({
          ...assessment,
          suggestions: updatedSuggestions
        });
      }
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Needs Improvement';
    return 'Incomplete';
  };

  return (
    <div className="space-y-4">
      {/* Description Input */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-black">
            <span className="text-red-500">*</span>Description
          </label>
          {assessment && (
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(assessment.overallScore)}`}>
                Quality Score: {assessment.overallScore}/100 ({getScoreLabel(assessment.overallScore)})
              </span>
              {assessment.readinessForSubmission && (
                <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                  ✓ Ready for Submission
                </span>
              )}
            </div>
          )}
        </div>
        
        <div className="relative">
          <textarea
            value={description}
            onChange={(e) => onDescriptionChange(e.target.value)}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black bg-white placeholder-gray-500"
            placeholder="Please enter the details of your request, detection name and the steps you have taken to address your concern. Be as specific as possible for better AI analysis."
          />
          
          {isAnalyzing && (
            <div className="absolute bottom-2 right-2">
              <div className="flex items-center space-x-2 bg-blue-50 px-2 py-1 rounded-md">
                <svg className="w-4 h-4 animate-spin text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="text-xs text-blue-600">AI analyzing...</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quality Assessment */}
      {showAssistant && assessment && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h4 className="font-semibold text-blue-800">AI Quality Assessment</h4>
            </div>
            {assessment.estimatedResolutionTime && (
              <span className="text-sm text-blue-600">
                Est. Resolution: {assessment.estimatedResolutionTime}
              </span>
            )}
          </div>

          {/* Quality Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
            {Object.entries(assessment.completeness).map(([key, value]) => (
              <div key={key} className="bg-white rounded-lg p-2 text-center">
                <div className={`text-lg font-bold ${getScoreColor(value)}`}>
                  {value}%
                </div>
                <div className="text-xs text-gray-600 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
              </div>
            ))}
          </div>

          {/* Suggestions */}
          {assessment.suggestions.length > 0 && (
            <div>
              <h5 className="font-medium text-blue-800 mb-2">Improvement Suggestions:</h5>
              <div className="space-y-2">
                {assessment.suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className={`bg-white border rounded-lg p-3 ${suggestion.completed ? 'opacity-50' : ''}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-gray-900">{suggestion.area}</span>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            suggestion.impact === 'High' ? 'bg-red-100 text-red-700' :
                            suggestion.impact === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {suggestion.impact} Impact
                          </span>
                          {suggestion.completed && (
                            <span className="text-green-600 text-xs">✓ Applied</span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{suggestion.suggestion}</p>
                        
                        {expandedSuggestion === index && suggestion.exampleText && (
                          <div className="mt-2 p-2 bg-gray-50 rounded border text-sm text-gray-700">
                            <strong>Example:</strong> {suggestion.exampleText}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-col space-y-1 ml-3">
                        {suggestion.exampleText && (
                          <button
                            onClick={() => setExpandedSuggestion(expandedSuggestion === index ? null : index)}
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                          >
                            {expandedSuggestion === index ? 'Hide' : 'Example'}
                          </button>
                        )}
                        {suggestion.exampleText && !suggestion.completed && (
                          <button
                            onClick={() => applySuggestion(index, suggestion)}
                            className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                          >
                            Apply
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {assessment.readinessForSubmission && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-green-800 font-medium">
                  Your case description is comprehensive and ready for submission!
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
