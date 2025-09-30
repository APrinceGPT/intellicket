'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useBackend } from '@/contexts/BackendContext';
import Image from 'next/image';
import StandardFooter from '@/components/common/StandardFooter';

const products = [
  { 
    id: 'deep-security', 
    name: 'Deep Security',
    description: 'Server & Cloud Protection',
    fullDescription: 'Comprehensive security for physical, virtual, and cloud servers with advanced threat protection.',
    icon: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>,
    gradient: 'from-red-600 to-red-800',
    hoverGradient: 'hover:from-red-700 hover:to-red-900',
    features: ['Multi-layered server security', 'Virtual patching and IPS', 'Anti-malware and web reputation', 'Application control and integrity monitoring']
  },
  { 
    id: 'apex-one', 
    name: 'Apex One',
    description: 'Endpoint Security',
    fullDescription: 'Advanced threat detection and response for endpoints with AI-powered protection.',
    icon: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
    gradient: 'from-blue-600 to-blue-800',
    hoverGradient: 'hover:from-blue-700 hover:to-blue-900',
    features: ['Next-gen antivirus', 'Behavioral analysis', 'Advanced threat detection', 'Endpoint detection and response']
  },
  { 
    id: 'vision-one', 
    name: 'Vision One',
    description: 'XDR Platform',
    fullDescription: 'Extended Detection and Response (XDR) for comprehensive security visibility and response.',
    icon: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>,
    gradient: 'from-purple-600 to-purple-800',
    hoverGradient: 'hover:from-purple-700 hover:to-purple-900',
    features: ['Cross-layer visibility', 'Advanced threat hunting', 'Automated response', 'Risk assessment and prioritization']
  },
  { 
    id: 'service-gateway', 
    name: 'Service Gateway',
    description: 'Secure Connectivity',
    fullDescription: 'Secure service delivery platform with enterprise-grade performance and reliability.',
    icon: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>,
    gradient: 'from-green-600 to-green-800',
    hoverGradient: 'hover:from-green-700 hover:to-green-900',
    features: ['Secure service delivery', 'Advanced access control', 'Performance monitoring', 'Centralized configuration management']
  },
];

export default function Home() {
  const [selectedProduct, setSelectedProduct] = useState<string>('');
  const [hoveredProduct, setHoveredProduct] = useState<string>('');
  const router = useRouter();
  const { backendStatus } = useBackend();

  const handleProductSelection = (productId: string) => {
    setSelectedProduct(productId);
    // Navigate to the product-specific page
    router.push(`/products/${productId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/10 to-gray-950 flex flex-col relative overflow-hidden">
      {/* Animated Background Elements - Following Design System */}
      <div className="absolute inset-0 opacity-15">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-orange-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header - Consistent with Design System */}
      <header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-red-500/30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
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
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-white/80 text-sm">
                Intelligent Security Support
              </div>
              {/* Global Backend Status */}
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg text-xs font-medium border transition-all duration-300 ${
                backendStatus === 'connected' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                backendStatus === 'checking' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse' :
                'bg-red-500/20 text-red-400 border-red-500/30'
              }`}>
                {backendStatus === 'connected' && (
                  <>
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span>CSDAIv2 Ready</span>
                  </>
                )}
                {backendStatus === 'checking' && (
                  <>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <span>Connecting...</span>
                  </>
                )}
                {backendStatus === 'error' && (
                  <>
                    <div className="w-2 h-2 bg-red-400 rounded-full animate-ping"></div>
                    <span>Backend Offline</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-4 mb-6">
            <Image
              src="/trendlogo.png"
              alt="Trend Micro"
              width={60}
              height={60}
              className="drop-shadow-2xl"
            />
            <div className="h-12 w-px bg-gradient-to-b from-transparent via-red-500/50 to-transparent" />
            <div className="relative">
              <div className="flex items-center justify-center">
                <svg className="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center animate-pulse">
                <span className="text-white text-xs">AI</span>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-gray-200 to-red-300 bg-clip-text text-transparent mb-6">
              Intellicket Support Platform
            </h1>
            <div className="flex items-center justify-center gap-2 mb-4">
              <div className="inline-flex items-center px-6 py-3 rounded-full text-sm font-medium bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border border-blue-500/30 backdrop-blur-sm">
                <span className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse"></span>
                <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                AI-Powered Security Support
              </div>
            </div>
            <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-12">
              Experience next-generation cybersecurity support with our advanced AI-powered platform.
              Featuring intelligent analyzers, ML-enhanced diagnostics, and dynamic knowledge retrieval for 
              <span className="text-red-400 font-semibold"> faster issue resolution</span>.
            </p>
          </div>
          
          {/* AI Capabilities Showcase */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:border-green-500/40 transition-all duration-300 group">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <span className="text-white text-2xl">✓</span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">24/7</div>
                <div className="text-gray-300 text-sm font-semibold mb-1">AI-Powered Support</div>
                <div className="text-gray-400 text-xs">Instant intelligent assistance with machine learning algorithms</div>
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:border-blue-500/40 transition-all duration-300 group">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">99.9%</div>
                <div className="text-gray-300 text-sm font-semibold mb-1">Resolution Rate</div>
                <div className="text-gray-400 text-xs">Advanced threat analysis with dynamic knowledge retrieval</div>
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 hover:border-purple-500/40 transition-all duration-300 group">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">&lt;5min</div>
                <div className="text-gray-300 text-sm font-semibold mb-1">Average Response</div>
                <div className="text-gray-400 text-xs">Expert-level solutions with confidence scoring</div>
              </div>
            </div>
          </div>
        </div>

        {/* Product Selection Section */}
        <div className="w-full">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold bg-gradient-to-r from-white via-green-200 to-green-400 bg-clip-text text-transparent mb-4">
              Select Your Product
            </h2>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              Choose the Trend Micro product you need support for and access our AI-powered diagnostic tools
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {products.map((product) => (
              <button
                key={product.id}
                onClick={() => handleProductSelection(product.id)}
                onMouseEnter={() => setHoveredProduct(product.id)}
                onMouseLeave={() => setHoveredProduct('')}
                className={`
                  group relative bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 text-left 
                  transition-all duration-300 transform hover:scale-105 border border-white/20
                  hover:border-red-500/40
                  ${hoveredProduct === product.id ? 'border-red-500/40 bg-white/15' : ''}
                  ${selectedProduct === product.id ? 'border-red-500/60 bg-red-500/10' : ''}
                `}
              >
                {/* Background glow effect - Following design system */}
                <div className="absolute inset-0 bg-gradient-to-br from-red-500/0 to-red-500/0 group-hover:from-red-500/5 group-hover:to-red-500/10 rounded-2xl transition-all duration-300"></div>
                
                {/* Card Content */}
                <div className="relative">
                  {/* Header - Following card design pattern */}
                  <div className="flex items-center gap-3 mb-6">
                    <div className={`w-12 h-12 bg-gradient-to-br ${product.gradient} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                      <div className="text-white">
                        {product.icon}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-1">
                        {product.name}
                      </h3>
                      <p className="text-gray-300 text-sm">
                        {product.description}
                      </p>
                    </div>
                  </div>

                  {/* Description */}
                  <div className="bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10 mb-6">
                    <p className="text-gray-300 leading-relaxed">
                      {product.fullDescription}
                    </p>
                  </div>

                  {/* Features */}
                  <div className="space-y-3 mb-6">
                    <h4 className="text-white font-semibold flex items-center gap-2">
                      <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                      Key Features
                    </h4>
                    <div className="space-y-2">
                      {product.features.map((feature, index) => (
                        <div key={index} className="flex items-start gap-3">
                          <div className="w-1 h-1 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-sm text-gray-300">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Call to Action */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-gray-300 group-hover:text-white transition-colors duration-300">
                      <span className="text-sm font-medium">Get Support</span>
                      <svg className="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                    <div className={`px-4 py-2 rounded-xl bg-gradient-to-r ${product.gradient} text-white text-xs font-medium opacity-80 group-hover:opacity-100 transition-opacity duration-300`}>
                      AI Powered
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Intellicket Portal Section */}
          <div className="mt-20 text-center">
            <div className="mb-12">
              <h3 className="text-4xl font-bold bg-gradient-to-r from-white via-red-100 to-red-200 bg-clip-text text-transparent mb-6">
                Need Expert Support Analysis?
              </h3>
              <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
                Experience our intelligent portal that transforms support requests with AI-powered analysis, 
                delivering personalized analyzer recommendations for your cybersecurity challenges.
              </p>
            </div>
            
            <div className="relative group cursor-pointer" onClick={() => router.push('/portal')}>
              <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 via-red-600/20 to-red-700/20 rounded-2xl blur opacity-60 group-hover:opacity-100 transition duration-300"></div>
              <div className="relative bg-slate-950/90 backdrop-blur-sm border border-red-500/30 hover:border-red-500/50 rounded-2xl p-8 transition-all duration-300 transform hover:scale-105">
                <div className="flex flex-col md:flex-row items-center gap-6">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-red-950/30 rounded-xl flex items-center justify-center border border-red-500/30">
                      <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div className="text-left">
                      <h4 className="text-2xl font-bold text-white mb-2">Launch Intellicket Portal</h4>
                      <p className="text-red-400 font-medium">AI-Powered Support Analysis</p>
                    </div>
                  </div>
                  <div className="flex-1 text-center md:text-left">
                    <p className="text-gray-300 text-sm">
                      Submit cases • Get AI recommendations • Accelerate resolution
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-red-400">
                    <span className="text-sm font-medium">Access Portal</span>
                    <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Comprehensive AI Security Intelligence Platform */}
        <div className="max-w-7xl mx-auto w-full mt-24">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 via-red-600/20 to-red-700/20 rounded-3xl blur opacity-50 group-hover:opacity-75 transition duration-300"></div>
            <div className="relative bg-slate-950/90 backdrop-blur-sm border border-red-500/30 rounded-2xl p-12">
              <div className="text-center mb-16">
                <h3 className="text-4xl font-bold bg-gradient-to-r from-white via-red-100 to-red-200 bg-clip-text text-transparent mb-6">
                  AI-Powered Security Intelligence Platform
                </h3>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
                  Next-generation cybersecurity with AI-driven threat detection, 
                  rapid response, and intelligent analysis tailored to your needs.
                </p>
              </div>
              
              {/* Top Row - Primary Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                <div className="flex flex-col items-center text-center group/card">
                  <div className="w-20 h-20 bg-gradient-to-br from-red-600 to-red-800 rounded-2xl flex items-center justify-center mb-6 group-hover/card:scale-110 transition-all duration-300 shadow-lg">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h4 className="text-2xl font-bold text-white mb-4">AI-Driven Analysis</h4>
                  <p className="text-gray-300 leading-relaxed">Smart algorithms deliver intelligent recommendations and threat detection tailored to your security environment.</p>
                </div>
                
                <div className="flex flex-col items-center text-center group/card">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl flex items-center justify-center mb-6 group-hover/card:scale-110 transition-all duration-300 shadow-lg">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h4 className="text-2xl font-bold text-white mb-4">Lightning-Fast Processing</h4>
                  <p className="text-gray-300 leading-relaxed">Instant threat detection and automated remediation with results delivered in seconds.</p>
                </div>
                
                <div className="flex flex-col items-center text-center group/card">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-purple-800 rounded-2xl flex items-center justify-center mb-6 group-hover/card:scale-110 transition-all duration-300 shadow-lg">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h4 className="text-2xl font-bold text-white mb-4">Advanced Threat Protection</h4>
                  <p className="text-gray-300 leading-relaxed">Real-time pattern recognition with comprehensive threat analysis and predictive vulnerability assessment.</p>
                </div>
              </div>

              {/* Bottom Row - Supporting Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-red-500/20 hover:border-red-500/40 transition-all duration-300 group/feature">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-red-950/30 rounded-lg flex items-center justify-center mr-4 group-hover/feature:bg-red-950/40 transition-colors duration-300">
                      <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    </div>
                    <h5 className="text-lg font-semibold text-white">Expert Precision</h5>
                  </div>
                  <p className="text-gray-400 text-sm leading-relaxed">Expert-level pattern recognition for precise security solutions.</p>
                </div>
                
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-red-500/20 hover:border-red-500/40 transition-all duration-300 group/feature">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-red-950/30 rounded-lg flex items-center justify-center mr-4 group-hover/feature:bg-red-950/40 transition-colors duration-300">
                      <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <h5 className="text-lg font-semibold text-white">Intelligence Analytics</h5>
                  </div>
                  <p className="text-gray-400 text-sm leading-relaxed">Deep insights with predictive analytics and comprehensive vulnerability assessment.</p>
                </div>
                
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-red-500/20 hover:border-red-500/40 transition-all duration-300 group/feature">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-red-950/30 rounded-lg flex items-center justify-center mr-4 group-hover/feature:bg-red-950/40 transition-colors duration-300">
                      <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </div>
                    <h5 className="text-lg font-semibold text-white">Automated Response</h5>
                  </div>
                  <p className="text-gray-400 text-sm leading-relaxed">Automated remediation with intelligent case routing for optimal resolution.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <StandardFooter onProductSelect={handleProductSelection} />
    </div>
  );
}
