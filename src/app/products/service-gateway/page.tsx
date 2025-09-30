'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import StandardFooter from '@/components/common/StandardFooter';

export default function ServiceGatewayPage() {
  const [isIntegrationReady, setIsIntegrationReady] = useState(false);
  const router = useRouter();



  // This component is ready for integration
  // When you need to integrate other projects, this is where they will be embedded
  const IntegrationPlaceholder = () => {
    return (
      <div className="bg-gradient-to-br from-green-900/20 to-green-800/20 border-2 border-green-500/30 rounded-2xl p-8 text-center backdrop-blur-sm">
        <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-2xl">
          <span className="text-white font-bold text-3xl">⚡</span>
        </div>
        <h3 className="text-2xl font-bold text-white mb-4">
          Integration Ready
        </h3>
        <p className="text-gray-300 mb-6 text-lg">
          This area is prepared for Service Gateway project integration.
          When prompted, the integrated component will appear here.
        </p>
        <button
          onClick={() => setIsIntegrationReady(true)}
          className="bg-gradient-to-r from-green-500 to-green-600 text-white px-8 py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-900/20 to-black relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-green-500/30">
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
                  <div className="text-xl font-bold text-green-400">Intellicket</div>
                  <div className="text-xs text-gray-400">AI Support Platform</div>
                </div>
              </Link>
              <span className="text-gray-500">→</span>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🌐</span>
                <span className="text-white font-semibold">Service Gateway</span>
              </div>
            </div>
            <Link
              href="/"
              className="bg-green-500/20 text-green-300 px-6 py-2 rounded-xl hover:bg-green-500/30 transition-all duration-300 border border-green-500/30"
            >
              ← Back to Products
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <div className="w-32 h-32 bg-gradient-to-br from-green-500 to-green-700 rounded-3xl mx-auto mb-8 flex items-center justify-center shadow-2xl">
            <span className="text-white font-bold text-5xl">🌐</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Service Gateway <span className="text-green-400">Support</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Get support for Trend Micro Service Gateway - your secure service delivery platform.
            Manage and monitor your service infrastructure with <span className="text-green-400">confidence and security</span>.
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
              Submit a new support request for Service Gateway issues.
            </p>
            <button 
              onClick={() => router.push('/portal')}
              className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white py-3 rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 transform hover:scale-105"
            >
              New Ticket
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-green-500/40 transition-all duration-300 group">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mb-6 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <span className="text-white text-2xl">�</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-4 group-hover:text-green-300 transition-colors">
              Knowledge Base
            </h3>
            <p className="text-gray-300 mb-6">
              Search our comprehensive Service Gateway documentation.
            </p>
            <button 
              onClick={() => window.open('https://docs.trendmicro.com/en-us/documentation/trend-micro-service-gateway/', '_blank')}
              className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105"
            >
              Browse Docs
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <StandardFooter showProductsAsLinks={true} />
    </div>
  );
}
