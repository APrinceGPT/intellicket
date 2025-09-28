'use client';

import { useState } from 'react';
import PortalHeader from './components/PortalHeader';
import NavigationTabs from './components/NavigationTabs';
import EnhancedNewCaseForm from './components/EnhancedNewCaseForm';

export default function PortalPage() {
  const [activeTab, setActiveTab] = useState('New Case');

  return (
    <div className="min-h-screen bg-gray-100">
      <PortalHeader />
      <NavigationTabs activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'New Case' && <EnhancedNewCaseForm />}
        {activeTab === 'Dashboard' && (
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H9a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Dashboard Coming Soon</h2>
              <p className="text-lg text-gray-600 mb-8">Track your cases, analyze trends, and monitor support metrics</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="text-3xl font-bold text-blue-600 mb-2">0</div>
                  <div className="text-gray-700">Active Cases</div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="text-3xl font-bold text-green-600 mb-2">0</div>
                  <div className="text-gray-700">Resolved Cases</div>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="text-3xl font-bold text-purple-600 mb-2">0</div>
                  <div className="text-gray-700">AI Analyses</div>
                </div>
              </div>
            </div>
          </div>
        )}
        {activeTab === 'Case List' && (
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Case Management</h2>
              <p className="text-lg text-gray-600 mb-8">View and manage all your support cases in one place</p>
              <div className="bg-white rounded-lg shadow-md p-8">
                <p className="text-gray-500">No cases found. Submit your first case using the &ldquo;New Case&rdquo; tab.</p>
              </div>
            </div>
          </div>
        )}
        {activeTab === 'Diagnostic Tool' && (
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <div className="bg-gradient-to-r from-red-500 to-pink-600 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Advanced Diagnostic Tools</h2>
              <p className="text-lg text-gray-600 mb-8">Use AI-powered analysis tools for immediate insights</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                  <div className="text-4xl mb-4">🛡️</div>
                  <h3 className="text-xl font-semibold mb-2">Deep Security Analysis</h3>
                  <p className="text-gray-600 mb-4">Comprehensive log analysis and troubleshooting</p>
                  <button 
                    onClick={() => window.open('/products/deep-security', '_blank')}
                    className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                  >
                    Open Tool
                  </button>
                </div>
                <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                  <div className="text-4xl mb-4">🔒</div>
                  <h3 className="text-xl font-semibold mb-2">Apex One Analysis</h3>
                  <p className="text-gray-600 mb-4">Endpoint security diagnostics and optimization</p>
                  <button 
                    onClick={() => window.open('/products/apex-one', '_blank')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Open Tool
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {(activeTab === 'License & Service' || activeTab === 'Account') && (
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">{activeTab}</h2>
              <p className="text-lg text-gray-600 mb-8">
                {activeTab === 'License & Service' 
                  ? 'Manage your licenses and service subscriptions' 
                  : 'Account settings and profile management'}
              </p>
              <div className="bg-white rounded-lg shadow-md p-8">
                <p className="text-gray-500">This section will be available in a future update.</p>
              </div>
            </div>
          </div>
        )}
      </main>
      <footer className="bg-black text-white text-center py-4 mt-auto">
        <p className="text-sm">Copyright © 2025 Trend Micro Incorporated. All rights reserved.</p>
      </footer>
    </div>
  );
}
