'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function ApexOnePage() {
  const [isIntegrationReady, setIsIntegrationReady] = useState(false);

  const products = [
    { id: 'deep-security', name: 'Deep Security', icon: '🛡️' },
    { id: 'apex-one', name: 'Apex One', icon: '🔒' },
    { id: 'vision-one', name: 'Vision One', icon: '👁️' },
    { id: 'service-gateway', name: 'Service Gateway', icon: '🌐' },
  ];

  // This component is ready for integration
  // When you need to integrate other projects, this is where they will be embedded
  const IntegrationPlaceholder = () => {
    return (
      <div className="bg-gradient-to-br from-blue-900/20 to-blue-800/20 border-2 border-blue-500/30 rounded-2xl p-8 text-center backdrop-blur-sm">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-2xl">
          <span className="text-white font-bold text-3xl">⚡</span>
        </div>
        <h3 className="text-2xl font-bold text-white mb-4">
          Integration Ready
        </h3>
        <p className="text-gray-300 mb-6 text-lg">
          This area is prepared for Apex One project integration.
          When prompted, the integrated component will appear here.
        </p>
        <button
          onClick={() => setIsIntegrationReady(true)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
        >
          Simulate Integration
        </button>
        {isIntegrationReady && (
          <div className="mt-6 p-4 bg-green-500/20 border border-green-400/30 rounded-xl backdrop-blur-sm">
            <p className="text-green-300 font-semibold">✅ Integration area activated - Ready for your project!</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900/20 to-black relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-blue-500/30">
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
                  <div className="text-xl font-bold text-blue-400">Intellicket</div>
                  <div className="text-xs text-gray-400">AI Support Platform</div>
                </div>
              </Link>
              <span className="text-gray-500">→</span>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🔒</span>
                <span className="text-white font-semibold">Apex One</span>
              </div>
            </div>
            <Link
              href="/"
              className="bg-blue-500/20 text-blue-300 px-6 py-2 rounded-xl hover:bg-blue-500/30 transition-all duration-300 border border-blue-500/30"
            >
              ← Back to Products
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-blue-700 rounded-3xl mx-auto mb-8 flex items-center justify-center shadow-2xl">
            <span className="text-white font-bold text-5xl">🔒</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Apex One <span className="text-blue-400">Support</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Comprehensive support for your Trend Micro Apex One endpoint security solution.
            Get help with deployment, configuration, and <span className="text-blue-400">advanced threat protection</span>.
          </p>
        </div>

        {/* Integration Area */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">
            Project Integration Area
          </h2>
          <IntegrationPlaceholder />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-red-500/40 transition-all duration-300 group">
            <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <span className="text-white text-2xl">🎫</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-4 group-hover:text-red-300 transition-colors">
              Create Support Ticket
            </h3>
            <p className="text-gray-300 mb-6">
              Submit a new support request for Apex One issues.
            </p>
            <button 
              onClick={() => window.open('https://success.trendmicro.com/', '_blank')}
              className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-3 rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 transform hover:scale-105"
            >
              New Ticket
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-green-500/40 transition-all duration-300 group">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <span className="text-white text-2xl">📚</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-4 group-hover:text-green-300 transition-colors">
              Knowledge Base
            </h3>
            <p className="text-gray-300 mb-6">
              Search our comprehensive Apex One documentation.
            </p>
            <button 
              onClick={() => window.open('https://docs.trendmicro.com/en-us/documentation/apex-one/', '_blank')}
              className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105"
            >
              Browse Docs
            </button>
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
  );
}
