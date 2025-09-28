'use client';

import Link from 'next/link';

export default function PortalHeader() {
  return (
    <header className="bg-black text-white">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-3">
          {/* Left side - Logo */}
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <div className="bg-red-600 rounded-full w-8 h-8 flex items-center justify-center">
                <span className="text-white font-bold text-lg">T</span>
              </div>
              <div>
                <span className="font-bold text-lg">TREND</span>
                <span className="text-red-600 font-bold text-lg">◆</span>
              </div>
            </Link>
            <span className="text-lg font-medium">Business Success</span>
          </div>

          {/* Center - Navigation */}
          <nav className="hidden lg:flex items-center space-x-8">
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-gray-300">
                <span>Products and Services</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-gray-300">
                <span>Resources</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            <a href="#" className="hover:text-gray-300">FAQ</a>
            <a href="#" className="hover:text-gray-300">Contact</a>
            
            {/* Back to Intellicket Button */}
            <Link 
              href="/"
              className="relative px-4 py-2 bg-gradient-to-r from-red-600 via-red-500 to-orange-500 text-white rounded-lg hover:from-red-700 hover:via-red-600 hover:to-orange-600 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl group overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-red-600/20 via-red-500/20 to-orange-500/20 animate-pulse"></div>
              <div className="relative flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                <span className="font-semibold text-sm">Back to Intellicket</span>
              </div>
            </Link>
          </nav>

          {/* Right side - Search and User */}
          <div className="flex items-center space-x-4">
            <button className="hover:text-gray-300">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <div className="flex items-center space-x-2">
              <div className="bg-red-600 rounded-full w-8 h-8 flex items-center justify-center">
                <span className="text-white font-bold text-sm">J</span>
              </div>
              <div className="relative group">
                <button className="flex items-center space-x-1 hover:text-gray-300">
                  <div className="text-left">
                    <div className="text-sm">new_user@trendmicro.com</div>
                    <div className="text-xs text-gray-400">AMEA House Account</div>
                  </div>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
