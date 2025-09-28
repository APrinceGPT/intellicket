'use client';

import { useState, useEffect } from 'react';

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

interface SmartTitleSuggestionProps {
  description: string;
  product: string;
  category: string;
  severity: string;
  currentTitle: string;
  onTitleSelect: (title: string) => void;
  onTitleChange: (title: string) => void;
}

export default function SmartTitleSuggestion({
  description,
  product,
  category,
  severity,
  currentTitle,
  onTitleSelect,
  onTitleChange
}: SmartTitleSuggestionProps) {
  const [suggestions, setSuggestions] = useState<TitleSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateTitleSuggestions = async () => {
    if (!description.trim() || description.trim().length < 20) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/ai/suggest-title', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          product,
          category,
          severity
        }),
      });

      if (response.ok) {
        const data: TitleSuggestionResponse = await response.json();
        setSuggestions(data.suggestions || []);
        setShowSuggestions(data.suggestions.length > 0);
        
        // Auto-select the highest confidence suggestion if no meaningful title is set
        if (!currentTitle.trim() && data.suggestions.length > 0 && data.suggestions[0].confidence > 0.8) {
          console.log('Auto-selecting title:', data.suggestions[0].suggestedTitle);
          onTitleSelect(data.suggestions[0].suggestedTitle);
          // Keep suggestions visible even after auto-selection so user can see other options
          setShowSuggestions(true);
        }
      } else {
        setError('Failed to generate title suggestions');
        // Fallback to basic title generation
        if (!currentTitle.trim()) {
          const basicTitle = generateBasicTitle(description, product, category, severity);
          if (basicTitle) {
            console.log('Using fallback title:', basicTitle);
            onTitleSelect(basicTitle);
          }
        }
      }
    } catch (error) {
      console.error('Error generating title suggestions:', error);
      setError('AI service temporarily unavailable - using fallback');
      
      // Fallback to basic title generation
      if (!currentTitle) {
        const basicTitle = generateBasicTitle(description, product, category, severity);
        if (basicTitle) {
          onTitleSelect(basicTitle);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Fallback title generation when AI is unavailable
  const generateBasicTitle = (desc: string, prod: string, cat: string, sev: string): string => {
    const words = desc.toLowerCase().split(' ');
    const keyTerms = words.filter(word => 
      word.length > 4 && 
      !['with', 'when', 'that', 'this', 'they', 'have', 'been', 'will', 'from'].includes(word)
    ).slice(0, 3);
    
    const severityPrefix = sev ? `[${sev}] ` : '';
    const productPrefix = prod.includes('Deep Security') ? 'DS ' : prod.substring(0, 10) + ' ';
    
    return `${severityPrefix}${productPrefix}${cat} - ${keyTerms.join(' ')}`;
  };

  // Trigger AI analysis when description changes (with debounce)
  useEffect(() => {
    console.log('SmartTitleSuggestion: Description changed:', {
      description: description.substring(0, 50) + (description.length > 50 ? '...' : ''),
      length: description.length,
      currentTitle: currentTitle,
      product,
      category,
      severity
    });

    if (!description || description.trim().length < 20) {
      console.log('SmartTitleSuggestion: Description too short, clearing suggestions');
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    console.log('SmartTitleSuggestion: Setting debounce timer for title generation');
    const debounceTimer = setTimeout(() => {
      console.log('SmartTitleSuggestion: Debounce timer triggered, generating title suggestions');
      generateTitleSuggestions();
    }, 1500); // Wait for user to finish typing

    return () => {
      console.log('SmartTitleSuggestion: Clearing debounce timer');
      clearTimeout(debounceTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [description, product, category, severity]);

  const handleSuggestionSelect = (suggestion: TitleSuggestion) => {
    onTitleSelect(suggestion.suggestedTitle);
    setShowSuggestions(false);
  };

  const handleManualGenerate = () => {
    if (description.trim().length >= 20) {
      setShowSuggestions(false); // Clear previous suggestions first
      generateTitleSuggestions();
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-50';
    if (confidence >= 0.8) return 'text-blue-600 bg-blue-50';
    if (confidence >= 0.7) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.9) return 'Excellent Match';
    if (confidence >= 0.8) return 'Good Match';
    if (confidence >= 0.7) return 'Fair Match';
    return 'Basic Match';
  };

  return (
    <div className="space-y-4">
      {/* Main Title Input */}
      <div>
        <label className="block text-sm font-medium text-black mb-2">
          <span className="text-red-500">*</span>Case Title
        </label>
        <div className="relative">
          <input
            type="text"
            value={currentTitle}
            onChange={(e) => onTitleChange(e.target.value)}
            className="w-full px-3 py-2 pr-24 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black bg-white placeholder-gray-500"
            placeholder="Brief title describing your issue"
          />
          
          {/* AI Generate Button */}
          <button
            type="button"
            onClick={handleManualGenerate}
            disabled={isLoading || description.trim().length < 20}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 text-xs bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-md hover:from-purple-600 hover:to-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
          >
            {isLoading ? (
              <>
                <svg className="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>AI</span>
              </>
            ) : (
              <>
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span>AI</span>
              </>
            )}
          </button>
        </div>
        
        {/* Help Text */}
        <div className="mt-1 flex items-center text-xs text-gray-500">
          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {description.trim().length < 20 
            ? 'Provide more description details to enable AI title suggestions'
            : 'AI will suggest titles based on your description'
          }
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <svg className="w-5 h-5 animate-spin text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <div>
              <div className="text-blue-800 font-medium">AI is analyzing your case...</div>
              <div className="text-blue-600 text-sm">Generating intelligent title suggestions</div>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-800 text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* AI Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-3">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h4 className="font-semibold text-purple-800">Smart Title Suggestions</h4>
            <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded-full">
              AI Powered
            </span>
          </div>
          
          <div className="space-y-3">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-lg p-3 hover:border-purple-300 transition-colors cursor-pointer group"
                onClick={() => handleSuggestionSelect(suggestion)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h5 className="font-medium text-gray-900 group-hover:text-purple-700 transition-colors">
                        {suggestion.suggestedTitle}
                      </h5>
                      <span className={`px-2 py-1 text-xs rounded-full ${getConfidenceColor(suggestion.confidence)}`}>
                        {getConfidenceLabel(suggestion.confidence)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{suggestion.reasoning}</p>
                    {suggestion.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {suggestion.keywords.map((keyword, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button className="ml-3 px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-md hover:bg-purple-200 transition-colors group-hover:bg-purple-600 group-hover:text-white">
                    Use This
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-3 pt-3 border-t border-purple-200">
            <button
              onClick={() => setShowSuggestions(false)}
              className="text-sm text-purple-600 hover:text-purple-800 flex items-center space-x-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Dismiss suggestions</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
