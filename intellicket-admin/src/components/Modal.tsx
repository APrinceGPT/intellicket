import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-slate-100">{title}</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {children}
        </div>
      </div>
    </div>
  );
};

interface AnalyzerConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  analyzers: Array<{
    id: string;
    name: string;
    status: string;
    health: string;
  }>;
  onToggleAnalyzer: (analyzerId: string) => void;
}

export const AnalyzerConfigModal: React.FC<AnalyzerConfigModalProps> = ({ 
  isOpen, 
  onClose, 
  analyzers,
  onToggleAnalyzer 
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Analyzer Configuration">
      <div className="space-y-4">
        <p className="text-slate-400 mb-6">
          Configure individual analyzers. Disabled analyzers will not be available for log analysis.
        </p>
        
        {analyzers.map((analyzer) => (
          <div key={analyzer.id} className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  analyzer.health === 'healthy' ? 'bg-green-400' :
                  analyzer.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                }`} />
                <div>
                  <h4 className="font-medium text-slate-200">{analyzer.name}</h4>
                  <p className="text-xs text-slate-400">Status: {analyzer.status}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  analyzer.status === 'enabled' ? 'bg-green-900/40 text-green-300' : 'bg-red-900/40 text-red-300'
                }`}>
                  {analyzer.status}
                </span>
                
                <button
                  onClick={() => onToggleAnalyzer(analyzer.id)}
                  className={`px-3 py-1 text-xs rounded-lg font-medium transition-colors ${
                    analyzer.status === 'enabled'
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {analyzer.status === 'enabled' ? 'Disable' : 'Enable'}
                </button>
              </div>
            </div>
          </div>
        ))}
        
        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-slate-700">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

interface SessionModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessions: Array<{
    id: string;
    status: string;
    analyzer: string;
    startTime: string;
  }>;
  onTerminateSession: (sessionId: string) => void;
}

export const SessionModal: React.FC<SessionModalProps> = ({ 
  isOpen, 
  onClose, 
  sessions,
  onTerminateSession 
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Active Sessions">
      <div className="space-y-4">
        <p className="text-slate-400 mb-6">
          Manage active analysis sessions. You can terminate sessions if needed.
        </p>
        
        {sessions.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <span className="text-4xl">📭</span>
            <p className="mt-2">No active sessions</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div key={session.id} className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-slate-200">Session {session.id.slice(0, 8)}</h4>
                  <p className="text-xs text-slate-400">Analyzer: {session.analyzer}</p>
                  <p className="text-xs text-slate-400">Started: {session.startTime}</p>
                </div>
                
                <div className="flex items-center space-x-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    session.status === 'processing' ? 'bg-yellow-900/40 text-yellow-300' :
                    session.status === 'completed' ? 'bg-green-900/40 text-green-300' :
                    'bg-blue-900/40 text-blue-300'
                  }`}>
                    {session.status}
                  </span>
                  
                  {session.status === 'processing' && (
                    <button
                      onClick={() => onTerminateSession(session.id)}
                      className="px-3 py-1 text-xs rounded-lg font-medium bg-red-600 hover:bg-red-700 text-white transition-colors"
                    >
                      Terminate
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        
        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-slate-700">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};