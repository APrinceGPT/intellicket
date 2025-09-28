'use client';

interface NavigationTabsProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function NavigationTabs({ activeTab, setActiveTab }: NavigationTabsProps) {
  const tabs = [
    'Dashboard',
    'New Case',
    'Case List',
    'Diagnostic Tool',
  ];

  const rightTabs = [
    'License & Service',
    'Account',
  ];

  return (
    <div className="bg-gray-600 text-white border-b border-gray-500">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          {/* Left tabs */}
          <div className="flex items-stretch">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 text-sm font-medium transition-all relative border-r border-gray-500 last:border-r-0 ${
                  activeTab === tab
                    ? 'bg-white text-black font-semibold'
                    : 'text-white hover:bg-gray-500 hover:text-white'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Right tabs */}
          <div className="flex items-stretch">
            {rightTabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 text-sm font-medium transition-all flex items-center space-x-1 border-l border-gray-500 first:border-l-0 ${
                  activeTab === tab
                    ? 'bg-white text-black font-semibold'
                    : 'text-white hover:bg-gray-500 hover:text-white'
                }`}
              >
                <span>{tab}</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
