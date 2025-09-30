'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import CSDAIv2Integration from '../../../components/deep-security/CSDAIv2Integration';
import ErrorBoundary from '../../../components/common/ErrorBoundary';
import StandardFooter from '../../../components/common/StandardFooter';
import Image from 'next/image';
import { 
  Shield, 
  Zap, 
  Ticket, 
  BookOpen,
  ArrowLeft,
  Brain
} from 'lucide-react';

// Create a separate component for the search params logic
function DeepSecurityContent() {
  const [isIntegrationReady, setIsIntegrationReady] = useState(true); // Set to true to show the integration by default
  const searchParams = useSearchParams();
  const router = useRouter();
  
  // Get analyzer from URL params
  const analyzerParam = searchParams?.get('analyzer');
  const autoUploadedParam = searchParams?.get('autoUploaded');
  
  // Get case context from session storage if it exists
  const [caseContext, setCaseContext] = useState(null);
  
  useEffect(() => {
    // Check for case context in session storage
    const storedContext = sessionStorage.getItem('caseContext');
    if (storedContext) {
      try {
        const parsed = JSON.parse(storedContext);
        // Add autoUploaded flag from URL parameter if present
        if (autoUploadedParam === 'true') {
          parsed.autoUploaded = true;
        }
        setCaseContext(parsed);
        // Clear after use to prevent persistence across sessions
        sessionStorage.removeItem('caseContext');
      } catch (error) {
        console.error('Error parsing case context:', error);
      }
    }
  }, [autoUploadedParam]);



  // This component now contains the integrated CSDAIv2 system
  const IntegrationPlaceholder = () => {
    if (isIntegrationReady) {
      return (
        <ErrorBoundary>
          <CSDAIv2Integration 
            initialAnalyzer={analyzerParam || undefined} 
            caseContext={caseContext || undefined} 
          />
        </ErrorBoundary>
      );
    }
    
    return (
      <div className="bg-gradient-to-br from-red-900/20 to-red-800/20 border-2 border-red-500/30 rounded-2xl p-8 text-center backdrop-blur-sm">
        <div className="w-20 h-20 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-2xl">
          <Zap className="h-10 w-10 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-white mb-4">
          Integration Ready
        </h3>
        <p className="text-gray-300 mb-6 text-lg">
          This area is prepared for Deep Security project integration.
          When prompted, the integrated component will appear here.
        </p>
        <button
          onClick={() => setIsIntegrationReady(true)}
          className="bg-gradient-to-r from-red-500 to-red-600 text-white px-8 py-3 rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
        >
          Activate Deep Security Analyzer
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/10 to-gray-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-20 overflow-hidden">
        {/* Primary floating orbs */}
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-r from-red-500 to-red-600 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-r from-orange-500 to-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        
        {/* Secondary floating elements */}
        <div className="absolute top-1/2 left-1/4 w-64 h-64 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mix-blend-multiply filter blur-2xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-1/3 right-1/3 w-48 h-48 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mix-blend-multiply filter blur-2xl animate-pulse" style={{animationDelay: '3s'}}></div>
        
        {/* Moving particles */}
        <div className="absolute top-1/4 right-1/4 w-32 h-32 bg-red-400 rounded-full mix-blend-multiply filter blur-xl animate-bounce opacity-30" style={{animationDuration: '4s'}}></div>
        <div className="absolute bottom-1/4 left-1/3 w-24 h-24 bg-orange-400 rounded-full mix-blend-multiply filter blur-xl animate-bounce opacity-30" style={{animationDuration: '3s', animationDelay: '0.5s'}}></div>
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
                <Shield className="h-5 w-5 text-red-400" />
                <span className="text-white font-semibold">Deep Security</span>
              </div>
            </div>
            <Link
              href="/"
              className="bg-red-500/20 text-red-300 px-6 py-2 rounded-xl hover:bg-red-500/30 transition-all duration-300 border border-red-500/30 flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Products
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        {/* Clean Hero Section */}
        <div className="text-center mb-16">
          {/* Simple Hero Title */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white via-gray-100 to-red-200 bg-clip-text text-transparent">
                Deep Security
              </span>
              <span className="bg-gradient-to-r from-red-400 via-red-500 to-red-600 bg-clip-text text-transparent"> AI Support</span>
            </h1>
            
            {/* Simplified AI Badge */}
            <div className="inline-flex items-center gap-2 bg-blue-950/30 px-4 py-2 rounded-full border border-blue-500/30 backdrop-blur-sm">
              <Brain className="h-4 w-4 text-blue-400" />
              <span className="text-blue-300 font-medium text-sm">Powered by Advanced AI</span>
            </div>
          </div>

          {/* Streamlined Description */}
          <div className="max-w-2xl mx-auto mb-8">
            <p className="text-lg text-gray-300 leading-relaxed mb-3">
              Experience next-generation Deep Security troubleshooting with our 
              <span className="text-red-400 font-semibold"> AI-Enhanced Unified Analyzer Suite</span>
            </p>
            <p className="text-sm text-gray-400">
              Intelligent analyzers powered by{' '}
              <span className="text-blue-400 font-semibold">machine learning</span>{' '}and{' '}
              <span className="text-green-400 font-semibold">dynamic knowledge retrieval</span>
            </p>
          </div>

          {/* Feature Pills */}
          <div className="flex flex-wrap justify-center gap-3 mb-8">
            <div className="bg-red-950/30 border border-red-500/30 px-4 py-2 rounded-full">
              <span className="text-red-300 text-sm font-medium">AMSP Analysis</span>
            </div>
            <div className="bg-blue-950/30 border border-blue-500/30 px-4 py-2 rounded-full">
              <span className="text-blue-300 text-sm font-medium">Conflict Resolution</span>
            </div>
            <div className="bg-green-950/30 border border-green-500/30 px-4 py-2 rounded-full">
              <span className="text-green-300 text-sm font-medium">Agent Diagnostics</span>
            </div>
            <div className="bg-purple-950/30 border border-purple-500/30 px-4 py-2 rounded-full">
              <span className="text-purple-300 text-sm font-medium">Resource Optimization</span>
            </div>
          </div>
        </div>

        {/* Integration Area - CSDAIv2 Deep Security Unified Analyzer */}
        <div className="mb-16">
          <IntegrationPlaceholder />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
          {/* Support Ticket Card */}
          <div className="group relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-red-500/50 via-orange-500/50 to-red-500/50 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
            <div className="relative bg-gradient-to-br from-slate-900/90 to-red-950/30 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-red-500/30 hover:border-red-400/60 transition-all duration-300">
              <div className="flex items-start justify-between mb-6">
                <div className="relative">
                  <div className="w-18 h-18 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-red-500/30">
                    <Ticket className="h-9 w-9 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center animate-pulse">
                    <span className="text-white text-xs font-bold">!</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-red-400 text-sm font-medium">SUPPORT</div>
                  <div className="text-gray-500 text-xs">24/7 Available</div>
                </div>
              </div>
              
              <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-red-300 transition-colors">
                Create Support Ticket
              </h3>
              <p className="text-gray-300 mb-8 leading-relaxed">
                Submit a new support request for Deep Security issues with our intelligent ticket routing system.
              </p>
              
              <button 
                onClick={() => router.push('/portal')}
                className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white py-4 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-red-500/30 font-semibold flex items-center justify-center gap-2"
              >
                <Ticket className="h-5 w-5" />
                New Ticket
              </button>
            </div>
          </div>

          {/* Knowledge Base Card */}
          <div className="group relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-green-500/50 via-emerald-500/50 to-green-500/50 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
            <div className="relative bg-gradient-to-br from-slate-900/90 to-green-950/30 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-green-500/30 hover:border-green-400/60 transition-all duration-300">
              <div className="flex items-start justify-between mb-6">
                <div className="relative">
                  <div className="w-18 h-18 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-green-500/30">
                    <BookOpen className="h-9 w-9 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center animate-pulse">
                    <Brain className="h-3 w-3 text-white" />
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 text-sm font-medium">KNOWLEDGE</div>
                  <div className="text-gray-500 text-xs">AI-Enhanced</div>
                </div>
              </div>
              
              <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-green-300 transition-colors">
                Knowledge Base
              </h3>
              <p className="text-gray-300 mb-8 leading-relaxed">
                Search our comprehensive Deep Security documentation with AI-powered intelligent search capabilities.
              </p>
              
              <button className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white py-4 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-green-500/30 font-semibold flex items-center justify-center gap-2">
                <BookOpen className="h-5 w-5" />
                Browse Docs
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <StandardFooter showProductsAsLinks={true} />
    </div>
  );
}

// Loading component for Suspense fallback
function DeepSecurityLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900/20 to-black relative overflow-hidden flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-2xl animate-pulse">
          <Shield className="h-8 w-8 text-white" />
        </div>
        <p className="text-white text-lg">Loading Deep Security Support...</p>
      </div>
    </div>
  );
}

// Main exported component with Suspense boundary
export default function DeepSecurityPage() {
  return (
    <Suspense fallback={<DeepSecurityLoading />}>
      <DeepSecurityContent />
    </Suspense>
  );
}
