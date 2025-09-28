'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useBackend } from '@/contexts/BackendContext';
import Image from 'next/image';

const products = [
  { 
    id: 'deep-security', 
    name: 'Deep Security',
    description: 'Server & Cloud Protection',
    fullDescription: 'Comprehensive security for physical, virtual, and cloud servers with advanced threat protection.',
    icon: '🛡️',
    gradient: 'from-red-600 to-red-800',
    hoverGradient: 'hover:from-red-700 hover:to-red-900',
    features: ['Multi-layered server security', 'Virtual patching and IPS', 'Anti-malware and web reputation', 'Application control and integrity monitoring']
  },
  { 
    id: 'apex-one', 
    name: 'Apex One',
    description: 'Endpoint Security',
    fullDescription: 'Advanced threat detection and response for endpoints with AI-powered protection.',
    icon: '🔒',
    gradient: 'from-blue-600 to-blue-800',
    hoverGradient: 'hover:from-blue-700 hover:to-blue-900',
    features: ['Next-gen antivirus', 'Behavioral analysis', 'Advanced threat detection', 'Endpoint detection and response']
  },
  { 
    id: 'vision-one', 
    name: 'Vision One',
    description: 'XDR Platform',
    fullDescription: 'Extended Detection and Response (XDR) for comprehensive security visibility and response.',
    icon: '👁️',
    gradient: 'from-purple-600 to-purple-800',
    hoverGradient: 'hover:from-purple-700 hover:to-purple-900',
    features: ['Cross-layer visibility', 'Advanced threat hunting', 'Automated response', 'Risk assessment and prioritization']
  },
  { 
    id: 'service-gateway', 
    name: 'Service Gateway',
    description: 'Secure Connectivity',
    fullDescription: 'Secure service delivery platform with enterprise-grade performance and reliability.',
    icon: '🌐',
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex flex-col relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-20 left-20 w-72 h-72 bg-red-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Image 
                src="/trendlogo.png" 
                alt="Trend Micro Logo" 
                width={48}
                height={48}
                className="h-12 w-auto"
              />
              <div className="border-l border-white/30 pl-4">
                <h1 className="text-2xl font-bold text-white">Intellicket</h1>
                <p className="text-xs text-red-400 font-medium">AI Support Platform</p>
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
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 relative z-10">
        <div className="max-w-6xl mx-auto text-center mb-20">
          <div className="mb-8">
            <span className="inline-flex items-center px-6 py-3 rounded-full text-sm font-medium bg-gradient-to-r from-blue-500/20 to-cyan-500/20 text-blue-300 border border-blue-500/30 mb-6 backdrop-blur-sm">
              <span className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse"></span>
              🚀 AI-Powered Security Support Platform
            </span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-8 leading-tight">
            Intelligent Support for
            <br />
            <span className="bg-gradient-to-r from-red-400 via-orange-400 to-red-500 bg-clip-text text-transparent">
              Trend Micro
            </span> Products
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-12">
            Experience next-generation cybersecurity support with our advanced AI-powered platform.
            <br />
            <span className="text-red-400 font-medium">Fast resolution, intelligent analysis, and expert guidance.</span>
          </p>
          
          {/* Enhanced Statistics Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center">
                  <span className="text-white text-2xl">✓</span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">24/7</div>
                <div className="text-gray-400 text-sm">AI-Powered Support</div>
                <div className="text-gray-500 text-xs mt-1">Instant intelligent assistance</div>
              </div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">
                  <span className="text-white text-2xl">⚡</span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">99.9%</div>
                <div className="text-gray-400 text-sm">Resolution Rate</div>
                <div className="text-gray-500 text-xs mt-1">Advanced threat analysis</div>
              </div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-center mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center">
                  <span className="text-white text-2xl">🎯</span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">&lt;5min</div>
                <div className="text-gray-400 text-sm">Average Response</div>
                <div className="text-gray-500 text-xs mt-1">Expert-level solutions</div>
              </div>
            </div>
          </div>
        </div>

        {/* Product Selection Section */}
        <div className="max-w-7xl mx-auto w-full">
          <h2 className="text-4xl md:text-5xl font-bold text-white text-center mb-4">
            Select Your Product
          </h2>
          <p className="text-lg text-gray-300 text-center mb-12">
            Choose the Trend Micro product you need support for
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {products.map((product) => (
              <button
                key={product.id}
                onClick={() => handleProductSelection(product.id)}
                onMouseEnter={() => setHoveredProduct(product.id)}
                onMouseLeave={() => setHoveredProduct('')}
                className={`
                  group relative bg-white/10 backdrop-blur-sm rounded-3xl shadow-2xl p-8 text-left 
                  transition-all duration-500 transform hover:scale-105 border border-white/20
                  ${hoveredProduct === product.id ? 'border-white/40 bg-white/15' : ''}
                  ${selectedProduct === product.id ? 'border-red-500/60 bg-red-500/10' : ''}
                `}
              >
                {/* Glow effect */}
                <div className={`absolute inset-0 rounded-3xl bg-gradient-to-r ${product.gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-500`}></div>
                
                {/* Card Content */}
                <div className="relative">
                  {/* Header */}
                  <div className="flex items-center space-x-4 mb-6">
                    <div className={`w-16 h-16 bg-gradient-to-br ${product.gradient} rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110`}>
                      <span className="text-3xl">
                        {product.icon}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-1 group-hover:text-red-300 transition-colors duration-300">
                        {product.name}
                      </h3>
                      <p className="text-sm text-gray-400 font-medium">
                        {product.description}
                      </p>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-gray-300 mb-6 leading-relaxed">
                    {product.fullDescription}
                  </p>

                  {/* Features */}
                  <div className="space-y-3 mb-6">
                    <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Key Features</h4>
                    <div className="grid grid-cols-1 gap-2">
                      {product.features.map((feature, index) => (
                        <div key={index} className="flex items-start space-x-3">
                          <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
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
          <div className="mt-16 text-center">
            <div className="mb-8">
              <h3 className="text-3xl font-bold text-white mb-4">
                Need Help Creating a Support Case?
              </h3>
              <p className="text-lg text-gray-300 max-w-3xl mx-auto">
                Use our intelligent portal to submit support requests. Our AI will analyze your case 
                and recommend the best analyzer for your specific needs.
              </p>
            </div>
            
            <button
              onClick={() => router.push('/portal')}
              className="relative px-12 py-6 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-500 text-white rounded-2xl hover:from-purple-700 hover:via-blue-700 hover:to-cyan-600 transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-3xl group overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-cyan-500/20 animate-pulse"></div>
              <div className="relative flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span className="text-2xl font-bold">Open Intellicket Portal</span>
                </div>
                <div className="flex flex-col items-start text-left">
                  <span className="text-sm font-medium opacity-90">AI-Powered Case Analysis</span>
                  <span className="text-xs opacity-75">Submit cases • Get recommendations • Quick resolution</span>
                </div>
                <div className="absolute -top-2 -right-2 w-4 h-4 bg-cyan-300 rounded-full animate-ping"></div>
              </div>
            </button>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <div className="text-purple-400 text-2xl mb-2">🤖</div>
                <h4 className="text-white font-semibold mb-1">AI Analysis</h4>
                <p className="text-gray-400 text-sm">Intelligent analyzer recommendations based on your case description</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <div className="text-blue-400 text-2xl mb-2">⚡</div>
                <h4 className="text-white font-semibold mb-1">Fast Resolution</h4>
                <p className="text-gray-400 text-sm">Direct routing to the most suitable diagnostic tool</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <div className="text-cyan-400 text-2xl mb-2">🎯</div>
                <h4 className="text-white font-semibold mb-1">Precise Support</h4>
                <p className="text-gray-400 text-sm">Context-aware assistance tailored to your specific issue</p>
              </div>
            </div>
          </div>
        </div>

        {/* Security Features Banner */}
        <div className="max-w-6xl mx-auto w-full mt-20">
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-700 rounded-full flex items-center justify-center mb-4">
                  <span className="text-white text-xl">🔐</span>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Advanced Threat Protection</h3>
                <p className="text-gray-400 text-sm">AI-powered security across all your environments</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full flex items-center justify-center mb-4">
                  <span className="text-white text-xl">⚡</span>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Real-time Response</h3>
                <p className="text-gray-400 text-sm">Instant threat detection and automated remediation</p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center mb-4">
                  <span className="text-white text-xl">🎯</span>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Intelligent Analytics</h3>
                <p className="text-gray-400 text-sm">Deep insights and predictive security intelligence</p>
              </div>
            </div>
          </div>
        </div>
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
                    <button 
                      onClick={() => handleProductSelection(product.id)}
                      className="hover:text-white transition-colors duration-300 text-left flex items-center"
                    >
                      <span className="text-lg mr-2">{product.icon}</span>
                      {product.name}
                    </button>
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
  );
}
