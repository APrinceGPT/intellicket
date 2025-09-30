'use client'

import React, { useState, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  FileText, 
  Upload, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Network, 
  Shield, 
  Settings,
  Brain,
  Target,
  Wrench,
  Info,
  AlertCircle,
  XCircle,
  X,
  ArrowLeft
} from 'lucide-react'

interface KeyFindingsCard {
  last_successful_heartbeat: {
    timestamp: string | null
    time_ago: string | null
    status: string
  }
  communication_method: {
    primary_method: string
    detected_method: string
    ports_detected: Array<{port: string, description: string}>
    protocols_found: string[]
  }
  proxy_server_analysis: {
    proxy_detected: boolean
    proxy_details: Array<{host: string, port: string, line: string}>
    proxy_issues: string[]
  }
  handshake_failures: {
    failures_detected: boolean
    failure_count: number
    failure_details: string[]
  }
  certificate_issues: {
    cert_problems_found: boolean
    cert_issues_count: number
    cert_problem_details: string[]
  }
  network_communication_failures: {
    network_failures_found: boolean
    failure_count: number
    network_failure_details: string[]
  }
  port_failures: {
    port_issues_found: boolean
    failed_ports: string[]
    listening_failures: string[]
    receiving_failures: string[]
  }
}

interface RootCauseAnalysisCard {
  primary_root_cause: string
  contributing_factors: string[]
  severity_assessment: string
  offline_duration_impact: string
  correlation_analysis: string[]
  ai_confidence_score: number
}

interface TroubleshootingRecommendationsCard {
  troubleshooting_steps: string[]
}

interface DSAgentOfflineAnalysisResult {
  key_findings_card: KeyFindingsCard
  root_cause_analysis_card: RootCauseAnalysisCard
  troubleshooting_recommendations_card: TroubleshootingRecommendationsCard
}

export default function DSAgentOfflineAnalyzerPage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<DSAgentOfflineAnalysisResult | null>(null)
  const [, setSessionId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (files) {
      const fileArray = Array.from(files)
      setSelectedFiles(prev => [...prev, ...fileArray])
    }
  }, [])

  const removeFile = useCallback((index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  const handleAnalysis = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one DS Agent log file')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      // Upload files
      const formData = new FormData()
      selectedFiles.forEach(file => {
        formData.append('files', file)
      })

      const uploadResponse = await fetch('/api/csdai/ds-agent-offline/upload', {
        method: 'POST',
        body: formData
      })

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload files')
      }

      const uploadResult = await uploadResponse.json()
      const newSessionId = uploadResult.session_id
      setSessionId(newSessionId)

      // Poll for results
      let attempts = 0
      const maxAttempts = 60 // 2 minutes with 2-second intervals

      const pollResults = async () => {
        try {
          const statusResponse = await fetch(`/api/csdai/ds-agent-offline/status/${newSessionId}`)
          const statusResult = await statusResponse.json()

          if (statusResult.status === 'completed') {
            const resultsResponse = await fetch(`/api/csdai/ds-agent-offline/results/${newSessionId}`)
            const results = await resultsResponse.json()
            
            // Ensure the results have the expected structure
            const processedResults = {
              key_findings_card: results.key_findings_card || {
                last_successful_heartbeat: { status: 'Not found in logs', timestamp: null, time_ago: null },
                communication_method: { primary_method: 'Unknown', detected_method: 'Unknown', ports_detected: [], protocols_found: [] },
                proxy_server_analysis: { proxy_detected: false, proxy_details: [], proxy_issues: [] },
                handshake_failures: { failures_detected: false, failure_count: 0, failure_details: [] },
                certificate_issues: { cert_problems_found: false, cert_issues_count: 0, cert_problem_details: [] },
                network_communication_failures: { network_failures_found: false, failure_count: 0, network_failure_details: [] },
                port_failures: { port_issues_found: false, failed_ports: [], listening_failures: [], receiving_failures: [] }
              },
              root_cause_analysis_card: results.root_cause_analysis_card || {
                primary_root_cause: 'Analysis completed - please review the key findings above',
                contributing_factors: [],
                severity_assessment: 'Unknown',
                offline_duration_impact: 'Cannot determine from available logs',
                correlation_analysis: [],
                ai_confidence_score: 0
              },
              troubleshooting_recommendations_card: results.troubleshooting_recommendations_card || {
                troubleshooting_steps: ['No troubleshooting steps available']
              }
            }
            
            setAnalysisResult(processedResults)
            setIsAnalyzing(false)
          } else if (statusResult.status === 'error') {
            throw new Error(statusResult.error || 'Analysis failed')
          } else if (attempts < maxAttempts) {
            attempts++
            setTimeout(pollResults, 2000)
          } else {
            throw new Error('Analysis timeout')
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Unknown error occurred')
          setIsAnalyzing(false)
        }
      }

      pollResults()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
      setIsAnalyzing(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'critical - agent completely offline':
      case 'critical - agent status unknown':
        return 'bg-red-500/20 text-red-300 border-red-500/30'
      case 'high':
      case 'high - authentication system compromised':
      case 'high - network infrastructure problems':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/30'
      case 'medium':
      case 'medium - configuration issues':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
      case 'low':
      case 'low - monitoring recommended':
        return 'bg-green-500/20 text-green-300 border-green-500/30'
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'text-green-400'
    if (score >= 75) return 'text-yellow-400'
    return 'text-red-400'
  }

  // Define products array for footer
  const products = [
    { id: 'deep-security', name: 'Deep Security', icon: '🛡️' },
    { id: 'apex-one', name: 'Apex One', icon: '🔒' },
    { id: 'vision-one', name: 'Vision One', icon: '👁️' },
    { id: 'service-gateway', name: 'Service Gateway', icon: '🌐' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/10 to-gray-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-15">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-orange-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-red-500/30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
              >
                <Image 
                  src="/trendlogo.png" 
                  alt="Trend Micro Logo" 
                  width={40}
                  height={40}
                  className="h-10 w-auto"
                />
                <div className="border-l border-white/30 pl-3">
                  <div className="text-xl font-bold text-red-400">Intellicket</div>
                  <div className="text-xs text-gray-400">AI Support Platform</div>
                </div>
              </Link>
              <span className="text-gray-500">→</span>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🛡️</span>
                <span className="text-white font-semibold">Deep Security</span>
              </div>
              <span className="text-gray-500">→</span>
              <div className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-purple-400" />
                <span className="text-gray-300 font-medium">DS Agent Offline Analyzer</span>
              </div>
            </div>
            <Link
              href="/products/deep-security"
              className="bg-red-500/20 text-red-300 px-6 py-2 rounded-xl hover:bg-red-500/30 transition-all duration-300 border border-red-500/30 flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Analyzers
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        {/* Enhanced Header with AI Capabilities Showcase */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-4 mb-6">
            <Link href="/products/deep-security" className="transition-transform hover:scale-105">
              <Image
                src="/trendlogo.png"
                alt="Trend Micro"
                width={60}
                height={60}
                className="drop-shadow-2xl"
              />
            </Link>
            <div className="h-12 w-px bg-gradient-to-b from-transparent via-red-500/50 to-transparent" />
            <div className="relative">
              <Shield className="h-12 w-12 text-red-500 drop-shadow-lg" />
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center animate-pulse">
                <Brain className="h-3 w-3 text-white" />
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-gray-200 to-red-300 bg-clip-text text-transparent mb-2">
              DS Agent Offline Analyzer
            </h1>
            <div className="flex items-center justify-center gap-2 mb-4">
              <Badge className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border-blue-500/30 px-3 py-1">
                <Brain className="h-3 w-3 mr-1" />
                AI-Powered
              </Badge>
              <Badge className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-300 border-purple-500/30 px-3 py-1">
                <Target className="h-3 w-3 mr-1" />
                ML-Enhanced
              </Badge>
              <Badge className="bg-gradient-to-r from-green-500/20 to-teal-500/20 text-green-300 border-green-500/30 px-3 py-1">
                <Shield className="h-3 w-3 mr-1" />
                Enterprise-Grade
              </Badge>
            </div>
          </div>
          
          <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-8">
            Advanced AI-powered diagnostic analysis for Deep Security Agent offline scenarios. 
            Leveraging Machine Learning, RAG (Retrieval-Augmented Generation), and intelligent pattern recognition 
            to provide comprehensive troubleshooting for communication failures, connectivity issues, and agent health assessment.
          </p>

          {/* AI Confidence Score Preview */}
          <div className="flex items-center justify-center gap-4 text-sm text-gray-400 mb-2">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>90%+ AI Confidence</span>
            </div>
            <div className="h-4 w-px bg-gray-600"></div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-100"></div>
              <span>Real-time Analysis</span>
            </div>
            <div className="h-4 w-px bg-gray-600"></div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-200"></div>
              <span>Expert Recommendations</span>
            </div>
          </div>
        </div>

        {/* Enhanced AI Capabilities Showcase */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-3">Powered by Advanced AI Technologies</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our analyzer combines cutting-edge AI technologies to deliver unparalleled diagnostic accuracy and actionable insights
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-blue-500/40 transition-all duration-500 group transform hover:scale-105">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-3xl mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mx-auto">
                  <Brain className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center animate-bounce">
                  <span className="text-xs font-bold text-white">RAG</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-blue-300 transition-colors text-center">RAG System</h3>
              <p className="text-gray-300 text-center leading-relaxed">
                Retrieval-Augmented Generation with dynamic knowledge base integration. 
                Accesses comprehensive Deep Security documentation and expert knowledge for context-aware analysis.
              </p>
              <div className="mt-4 flex items-center justify-center">
                <Badge variant="outline" className="border-blue-500/30 text-blue-300 bg-blue-500/10">
                  Knowledge-Driven
                </Badge>
              </div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-purple-500/40 transition-all duration-500 group transform hover:scale-105">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-700 rounded-3xl mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mx-auto">
                  <Target className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-pink-400 to-purple-500 rounded-full flex items-center justify-center animate-bounce delay-100">
                  <span className="text-xs font-bold text-white">ML</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors text-center">ML Engine</h3>
              <p className="text-gray-300 text-center leading-relaxed">
                Advanced Machine Learning algorithms for pattern recognition, anomaly detection, and predictive analysis. 
                Learns from historical data to identify communication failures and network issues.
              </p>
              <div className="mt-4 flex items-center justify-center">
                <Badge variant="outline" className="border-purple-500/30 text-purple-300 bg-purple-500/10">
                  Pattern Recognition
                </Badge>
              </div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-green-500/40 transition-all duration-500 group transform hover:scale-105">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-700 rounded-3xl mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mx-auto">
                  <Shield className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-emerald-400 to-green-500 rounded-full flex items-center justify-center animate-bounce delay-200">
                  <span className="text-xs font-bold text-white">AI</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-green-300 transition-colors text-center">AI Insights</h3>
              <p className="text-gray-300 text-center leading-relaxed">
                Intelligent diagnostic insights with confidence scoring and automated root cause analysis. 
                Provides expert-level troubleshooting recommendations with step-by-step guidance.
              </p>
              <div className="mt-4 flex items-center justify-center">
                <Badge variant="outline" className="border-green-500/30 text-green-300 bg-green-500/10">
                  Expert Analysis
                </Badge>
              </div>
            </div>
          </div>

          {/* Core Technology Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-blue-400 mb-1">90%+</div>
              <div className="text-xs text-gray-400">AI Confidence</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-purple-400 mb-1">&lt;30s</div>
              <div className="text-xs text-gray-400">Analysis Time</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-green-400 mb-1">50+</div>
              <div className="text-xs text-gray-400">Error Patterns</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-red-400 mb-1">24/7</div>
              <div className="text-xs text-gray-400">Availability</div>
            </div>
          </div>
        </div>

        {/* Usage Instructions */}
        <div className="mb-16">
          <div className="bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-green-500/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Info className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-3">How to Use DS Agent Offline Analyzer</h2>
              <p className="text-gray-300 max-w-2xl mx-auto">
                Follow these simple steps to perform comprehensive diagnostic analysis of your Deep Security Agent
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl mx-auto flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Upload className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-6 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    1
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Upload Log Files</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Select and upload your DS Agent log files. The analyzer accepts ds_agent.log (required), 
                  ds_agent-err.log (optional), and ds_agent-connect.log (optional) files.
                </p>
              </div>

              <div className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl mx-auto flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Brain className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-6 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    2
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">AI Analysis</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Our AI engines automatically analyze your logs using RAG system, ML pattern recognition, 
                  and expert knowledge base to identify issues and root causes.
                </p>
              </div>

              <div className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mx-auto flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Target className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-6 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    3
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Get Results</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Receive comprehensive analysis results with key findings, root cause analysis, 
                  confidence scores, and step-by-step troubleshooting recommendations.
                </p>
              </div>
            </div>

            {/* What You'll Get */}
            <div className="mt-8 pt-8 border-t border-white/10">
              <h3 className="text-xl font-bold text-white mb-4 text-center">What You&apos;ll Get</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                  <span className="text-sm text-gray-300">Root Cause Analysis</span>
                </div>
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                  <span className="text-sm text-gray-300">AI Confidence Score</span>
                </div>
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                  <span className="text-sm text-gray-300">Step-by-step Fixes</span>
                </div>
                <div className="flex items-center gap-2 p-3 bg-white/5 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                  <span className="text-sm text-gray-300">Expert Recommendations</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Streamlined File Upload Section */}
        {!analysisResult && (
          <div className="space-y-12">
            {/* Simple File Requirements */}
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-4">Select Your Log Files</h2>
                <p className="text-gray-400 text-sm">Choose the DS Agent log files you want to analyze</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="text-center p-4 bg-white/5 rounded-xl border border-green-500/20 hover:border-green-500/40 transition-colors">
                  <FileText className="h-8 w-8 text-green-400 mx-auto mb-2" />
                  <div className="font-semibold text-white text-sm">ds_agent.log</div>
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30 text-xs mt-1">Required</Badge>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-xl border border-blue-500/20 hover:border-blue-500/40 transition-colors">
                  <AlertTriangle className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                  <div className="font-semibold text-white text-sm">ds_agent-err.log</div>
                  <Badge variant="outline" className="border-gray-500/30 text-gray-400 text-xs mt-1">Optional</Badge>
                </div>
                <div className="text-center p-4 bg-white/5 rounded-xl border border-purple-500/20 hover:border-purple-500/40 transition-colors">
                  <Network className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                  <div className="font-semibold text-white text-sm">ds_agent-connect.log</div>
                  <Badge variant="outline" className="border-gray-500/30 text-gray-400 text-xs mt-1">Optional</Badge>
                </div>
              </div>
            </div>

            {/* Clean Upload Area */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <label className="block w-full cursor-pointer group">
                  <div className="relative bg-white/5 backdrop-blur-sm border-2 border-dashed border-gray-600 rounded-3xl p-12 hover:border-red-500/50 hover:bg-red-500/5 transition-all duration-500 group">
                    {/* Background Animation */}
                    <div className="absolute inset-0 bg-gradient-to-br from-red-500/0 to-red-500/0 group-hover:from-red-500/5 group-hover:to-red-500/10 rounded-3xl transition-all duration-500"></div>
                    
                    {/* Content */}
                    <div className="relative text-center">
                      <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-700 group-hover:from-red-500 group-hover:to-red-600 rounded-2xl mx-auto mb-6 flex items-center justify-center transition-all duration-500 group-hover:scale-110">
                        <Upload className="h-10 w-10 text-white" />
                      </div>
                      
                      <div className="space-y-2">
                        <h3 className="text-2xl font-bold text-white group-hover:text-red-200 transition-colors">
                          <span className="text-red-400 group-hover:text-red-300">Drag & Drop</span> or <span className="text-red-400 group-hover:text-red-300">Click to Select</span>
                        </h3>
                        <p className="text-gray-400 group-hover:text-gray-300 transition-colors">
                          DS Agent log files for AI-powered analysis
                        </p>
                      </div>
                      
                      <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span>.log</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span>.txt</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                          <span>.zip</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <input
                    type="file"
                    className="hidden"
                    multiple
                    accept=".log,.txt,.zip"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    id="file-upload"
                  />
                </label>
              </div>

              {/* Selected Files Display */}
              {selectedFiles.length > 0 && (
                <div className="mt-8 max-w-2xl mx-auto">
                  <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Selected Files</h3>
                      <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                        {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
                      </Badge>
                    </div>
                    
                    <div className="space-y-3">
                      {Array.from(selectedFiles).map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                              <FileText className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <div className="font-medium text-white">{file.name}</div>
                              <div className="text-sm text-gray-400">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                              </div>
                            </div>
                          </div>
                          <button
                            onClick={() => removeFile(index)}
                            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                            title="Remove file"
                          >
                            <X className="h-4 w-4 text-gray-400 group-hover:text-red-400" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Analysis Button */}
              {selectedFiles.length > 0 && (
                <div className="text-center mt-8">
                  <button
                    onClick={handleAnalysis}
                    disabled={isAnalyzing}
                    className="group relative inline-flex items-center justify-center px-12 py-4 text-lg font-semibold text-white bg-gradient-to-r from-red-600 to-red-700 rounded-2xl hover:from-red-500 hover:to-red-600 focus:outline-none focus:ring-4 focus:ring-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-xl hover:shadow-red-500/25"
                  >
                    <div className="relative flex items-center gap-3">
                      {isAnalyzing ? (
                        <>
                          <div className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full"></div>
                          <span>Analyzing with AI...</span>
                        </>
                      ) : (
                        <>
                          <Brain className="h-6 w-6" />
                          <span>Start AI Analysis</span>
                        </>
                      )}
                    </div>
                  </button>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className="mt-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-400" />
                    <span className="text-red-300 font-medium">Analysis Error</span>
                  </div>
                  <p className="text-red-200 mt-1">{error}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Enhanced Analysis Results */}
        {analysisResult && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center">
                  <CheckCircle className="h-8 w-8 text-white" />
                </div>
                <div className="h-12 w-px bg-gradient-to-b from-transparent via-green-500/50 to-transparent" />
                <div className="flex flex-col items-start">
                  <div className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-blue-400" />
                    <Target className="h-4 w-4 text-purple-400" />
                    <Shield className="h-4 w-4 text-green-400" />
                  </div>
                  <span className="text-sm text-gray-400">AI Analysis Complete</span>
                </div>
              </div>
              
              <h2 className="text-4xl font-bold bg-gradient-to-r from-white via-green-200 to-green-400 bg-clip-text text-transparent mb-3">
                Analysis Results
              </h2>
              
              <div className="flex items-center justify-center gap-4 mb-4">
                <Badge className="bg-green-500/20 text-green-300 border-green-500/30 px-4 py-2">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Analysis Complete
                </Badge>
                {analysisResult.root_cause_analysis_card?.ai_confidence_score && (
                  <Badge className={`px-4 py-2 ${getConfidenceColor(analysisResult.root_cause_analysis_card.ai_confidence_score)} bg-opacity-20 border-opacity-30`}>
                    <Brain className="h-4 w-4 mr-2" />
                    {analysisResult.root_cause_analysis_card.ai_confidence_score}% AI Confidence
                  </Badge>
                )}
              </div>
              
              <p className="text-gray-300 max-w-3xl mx-auto">
                Comprehensive DS Agent offline diagnostic analysis powered by AI, ML, and RAG technologies. 
                Results include root cause identification, expert recommendations, and confidence scoring.
              </p>
            </div>

            {/* Card 1: Key Findings */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-blue-500/40 transition-all duration-300">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center">
                    <Info className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-white text-xl">Key Findings</CardTitle>
                    <CardDescription className="text-gray-300">Critical status overview</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Heartbeat Status */}
                  <div className="space-y-3">
                    <h4 className="font-semibold flex items-center gap-2 text-white">
                      <Clock className="h-4 w-4 text-blue-400" />
                      Last Successful Heartbeat
                    </h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-2 mb-2">
                        {analysisResult.key_findings_card?.last_successful_heartbeat?.status === 'Found in logs' ? (
                          <CheckCircle className="h-4 w-4 text-green-400" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-400" />
                        )}
                        <span className="font-medium text-white">
                          {analysisResult.key_findings_card?.last_successful_heartbeat?.status || 'Status unknown'}
                        </span>
                      </div>
                      {analysisResult.key_findings_card?.last_successful_heartbeat?.timestamp && (
                        <div className="text-sm text-gray-300">
                          <p><strong>Timestamp:</strong> {analysisResult.key_findings_card.last_successful_heartbeat.timestamp}</p>
                          <p><strong>Time Ago:</strong> {analysisResult.key_findings_card.last_successful_heartbeat.time_ago}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Communication Method */}
                  <div className="space-y-3">
                    <h4 className="font-semibold flex items-center gap-2 text-white">
                      <Network className="h-4 w-4 text-purple-400" />
                      Communication Method
                    </h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <div className="space-y-2 text-gray-300">
                        <p><strong className="text-white">Method:</strong> {analysisResult.key_findings_card?.communication_method?.detected_method || 'Unknown'}</p>
                        <p><strong className="text-white">Primary:</strong> {analysisResult.key_findings_card?.communication_method?.primary_method || 'Unknown'}</p>
                        {analysisResult.key_findings_card?.communication_method?.ports_detected?.length > 0 && (
                          <div>
                            <strong className="text-white">Ports Detected:</strong>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {analysisResult.key_findings_card.communication_method.ports_detected.map((port, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs border-purple-500/30 text-purple-300">
                                  {port.port}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Proxy Server Analysis */}
                  <div className="space-y-3">
                    <h4 className="font-semibold flex items-center gap-2 text-white">
                      <Settings className="h-4 w-4 text-green-400" />
                      Proxy Server Analysis
                    </h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-2 mb-2">
                        {analysisResult.key_findings_card?.proxy_server_analysis?.proxy_detected ? (
                          <AlertTriangle className="h-4 w-4 text-yellow-400" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-400" />
                        )}
                        <span className="font-medium text-white">
                          {analysisResult.key_findings_card?.proxy_server_analysis?.proxy_detected ? 'Proxy Detected' : 'No Proxy Detected'}
                        </span>
                      </div>
                      {analysisResult.key_findings_card?.proxy_server_analysis?.proxy_issues?.length > 0 && (
                        <div className="mt-2">
                          <strong className="text-white">Issues:</strong>
                          <ul className="list-disc list-inside text-sm text-gray-300 mt-1">
                            {analysisResult.key_findings_card.proxy_server_analysis.proxy_issues.slice(0, 3).map((issue, idx) => (
                              <li key={idx}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Network Failures */}
                  <div className="space-y-3">
                    <h4 className="font-semibold flex items-center gap-2 text-white">
                      <AlertTriangle className="h-4 w-4 text-yellow-400" />
                      Network Communication Failures
                    </h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-2 mb-2">
                        {analysisResult.key_findings_card?.network_communication_failures?.network_failures_found ? (
                          <XCircle className="h-4 w-4 text-red-400" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-400" />
                        )}
                        <span className="font-medium text-white">
                          {analysisResult.key_findings_card?.network_communication_failures?.network_failures_found 
                            ? `${analysisResult.key_findings_card.network_communication_failures.failure_count || 0} failures detected`
                            : 'No network failures detected'
                          }
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Certificate Issues */}
                  <div className="space-y-3">
                    <h4 className="font-semibold flex items-center gap-2 text-white">
                      <Shield className="h-4 w-4 text-red-400" />
                      Certificate Issues
                    </h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-2 mb-2">
                        {analysisResult.key_findings_card?.certificate_issues?.cert_problems_found ? (
                          <XCircle className="h-4 w-4 text-red-400" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-400" />
                        )}
                        <span className="font-medium text-white">
                          {analysisResult.key_findings_card?.certificate_issues?.cert_problems_found 
                            ? `${analysisResult.key_findings_card.certificate_issues.cert_issues_count || 0} certificate issues found`
                            : 'No certificate issues detected'
                          }
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Port Failures */}
                  <div className="space-y-3">
                    <h4 className="font-semibold flex items-center gap-2 text-white">
                      <Settings className="h-4 w-4 text-orange-400" />
                      Port Failures
                    </h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-2 mb-2">
                        {analysisResult.key_findings_card?.port_failures?.port_issues_found ? (
                          <XCircle className="h-4 w-4 text-red-400" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-400" />
                        )}
                        <span className="font-medium text-white">
                          {analysisResult.key_findings_card?.port_failures?.port_issues_found 
                            ? `Port issues on: ${analysisResult.key_findings_card.port_failures.failed_ports?.join(', ') || 'unknown ports'}`
                            : 'No port issues detected'
                          }
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Card 2: Root Cause Analysis */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-yellow-500/40 transition-all duration-300">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-white text-xl">Root Cause Analysis</CardTitle>
                    <CardDescription className="text-gray-300">AI-powered diagnosis of DS Agent offline issues</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Primary Root Cause */}
                  <div>
                    <h4 className="font-semibold mb-3 text-white">Primary Root Cause</h4>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <p className="text-gray-300 font-medium">{analysisResult.root_cause_analysis_card?.primary_root_cause || 'Root cause analysis in progress...'}</p>
                    </div>
                  </div>

                  {/* Severity and Confidence */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-3 text-white">Severity Assessment</h4>
                      <Badge className={`${getSeverityColor(analysisResult.root_cause_analysis_card?.severity_assessment || 'unknown')} bg-white/10 border-white/20`}>
                        {analysisResult.root_cause_analysis_card?.severity_assessment || 'Unknown'}
                      </Badge>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3 text-white">AI Confidence Score</h4>
                      <span className={`text-2xl font-bold ${getConfidenceColor(analysisResult.root_cause_analysis_card?.ai_confidence_score || 0)}`}>
                        {analysisResult.root_cause_analysis_card?.ai_confidence_score || 0}%
                      </span>
                    </div>
                  </div>

                  {/* Contributing Factors */}
                  <div>
                    <h4 className="font-semibold mb-3 text-white">Contributing Factors</h4>
                    <div className="space-y-2">
                      {analysisResult.root_cause_analysis_card?.contributing_factors?.length > 0 ? (
                        analysisResult.root_cause_analysis_card.contributing_factors.map((factor, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                            <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                            {factor}
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-400 text-sm">No contributing factors identified</p>
                      )}
                    </div>
                  </div>

                  {/* Offline Duration Impact */}
                  <div>
                    <h4 className="font-semibold mb-3 text-white">Offline Duration Impact</h4>
                    <div className="bg-yellow-500/20 border border-yellow-500/30 rounded-lg p-4">
                      <p className="text-yellow-200">{analysisResult.root_cause_analysis_card?.offline_duration_impact || 'Cannot determine offline duration from available logs'}</p>
                    </div>
                  </div>

                  {/* Correlation Analysis */}
                  <div>
                    <h4 className="font-semibold mb-3 text-white">Correlation Analysis</h4>
                    <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                      <ul className="space-y-1 text-sm">
                        {analysisResult.root_cause_analysis_card?.correlation_analysis?.length > 0 ? (
                          analysisResult.root_cause_analysis_card.correlation_analysis.map((item, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-gray-300">
                              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                              {item}
                            </li>
                          ))
                        ) : (
                          <li className="text-gray-400">No correlation data available</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Card 3: Troubleshooting Recommendations */}
            <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-green-500/40 transition-all duration-300">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-700 rounded-xl flex items-center justify-center">
                    <Wrench className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-white text-xl">Troubleshooting Recommendations</CardTitle>
                    <CardDescription className="text-gray-300">Direct technical support instructions from Trend Micro Deep Security experts</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-br from-green-500/20 to-blue-500/20 border border-green-500/30 rounded-lg p-6">
                  <div className="space-y-3">
                    {analysisResult.troubleshooting_recommendations_card?.troubleshooting_steps?.length > 0 ? (
                      analysisResult.troubleshooting_recommendations_card.troubleshooting_steps.map((step: string, idx: number) => (
                        <div key={idx} className="text-gray-300 leading-relaxed">
                          {step.trim() === '' ? (
                            <div className="h-2"></div>
                          ) : step.startsWith('🚨') || step.startsWith('⚠️') || step.startsWith('📋') ? (
                            <div className="font-semibold text-white bg-red-500/30 px-4 py-2 rounded-lg border border-red-500/40">
                              {step}
                            </div>
                          ) : step.startsWith('Root Cause:') ? (
                            <div className="font-medium text-orange-300 bg-orange-500/20 px-4 py-2 rounded-lg border border-orange-500/30">
                              {step}
                            </div>
                          ) : step.startsWith('AI Confidence:') ? (
                            <div className="font-medium text-blue-300 bg-blue-500/20 px-4 py-2 rounded-lg border border-blue-500/30">
                              {step}
                            </div>
                          ) : step.startsWith('TREND MICRO TECHNICAL SUPPORT') ? (
                            <div className="font-bold text-white bg-gradient-to-r from-red-600 to-red-700 px-4 py-3 rounded-lg border border-red-500/40 text-center">
                              {step}
                            </div>
                          ) : step.startsWith('🔧') || step.startsWith('🌐') || step.startsWith('🔐') || step.startsWith('🤝') || step.startsWith('🚪') || step.startsWith('🔄') ? (
                            <div className="font-semibold text-yellow-300 bg-yellow-500/20 px-4 py-2 rounded-lg border border-yellow-500/30 mt-4">
                              {step}
                            </div>
                          ) : step.startsWith('📋 VERIFICATION STEPS:') ? (
                            <div className="font-semibold text-green-300 bg-green-500/20 px-4 py-2 rounded-lg border border-green-500/30 mt-4">
                              {step}
                            </div>
                          ) : step.startsWith('📞') ? (
                            <div className="font-medium text-purple-300 bg-purple-500/20 px-4 py-2 rounded-lg border border-purple-500/30">
                              {step}
                            </div>
                          ) : step.match(/^\d+\./) ? (
                            <div className="ml-6 flex items-start gap-3">
                              <span className="bg-green-600 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-0.5 font-medium">
                                {step.match(/^(\d+)\./)?.[1]}
                              </span>
                              <span className="text-gray-200">{step.replace(/^\d+\.\s*/, '')}</span>
                            </div>
                          ) : step.startsWith('•') ? (
                            <div className="ml-4 flex items-start gap-2">
                              <span className="text-green-400 mt-1">•</span>
                              <span className="text-gray-200">{step.replace(/^•\s*/, '')}</span>
                            </div>
                          ) : (
                            <div className={step.startsWith('✅') ? 'text-green-300 font-medium' : 'text-gray-300'}>
                              {step}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-gray-400 py-8">
                        <Wrench className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p>No troubleshooting recommendations available</p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Reset Button */}
            <div className="text-center">
              <Button 
                onClick={() => {
                  setAnalysisResult(null)
                  setSelectedFiles([])
                  setSessionId(null)
                  setError(null)
                }}
                variant="outline"
                className="bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/30 transition-all duration-300"
              >
                Analyze New Files
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 bg-black/40 backdrop-blur-sm border-t border-white/10 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-4 mb-4">
                <Image 
                  src="/trendlogo.png" 
                  alt="Trend Micro Logo" 
                  width={32}
                  height={32}
                  className="h-8 w-auto"
                />
                <div className="border-l border-white/30 pl-4">
                  <h3 className="text-xl font-bold text-white">Intellicket</h3>
                  <p className="text-xs text-red-400 font-medium">AI Support Platform</p>
                </div>
              </div>
              <p className="text-gray-300 mb-4 max-w-md">
                Intelligent support system for Trend Micro products. Secure your digital world with AI-powered cybersecurity solutions.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-red-400 transition-colors">
                  <span className="sr-only">Twitter</span>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-red-400 transition-colors">
                  <span className="sr-only">LinkedIn</span>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd" />
                  </svg>
                </a>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-red-400">Quick Links</h3>
              <ul className="space-y-3 text-gray-300">
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Support Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Contact Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Security Blog</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-red-400">Products</h3>
              <ul className="space-y-3 text-gray-300">
                {products.map((product) => (
                  <li key={product.id}>
                    <Link 
                      href={`/products/${product.id}`}
                      className="hover:text-white transition-colors duration-300 text-left flex items-center"
                    >
                      <span className="text-lg mr-2">{product.icon}</span>
                      {product.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="border-t border-white/20 mt-12 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                &copy; 2025 Intellicket - AI-Powered Cybersecurity Platform. All rights reserved. | Securing your digital transformation.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</a>
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</a>
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Security</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}