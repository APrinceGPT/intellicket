'use client';

import { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';

type BackendStatus = 'checking' | 'connected' | 'error';

interface BackendContextType {
  backendStatus: BackendStatus;
  checkBackendStatus: () => Promise<void>;
  isBackendReady: boolean;
}

const BackendContext = createContext<BackendContextType | undefined>(undefined);

export function useBackend() {
  const context = useContext(BackendContext);
  if (context === undefined) {
    throw new Error('useBackend must be used within a BackendProvider');
  }
  return context;
}

interface BackendProviderProps {
  children: ReactNode;
}

export function BackendProvider({ children }: BackendProviderProps) {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');
  const isMountedRef = useRef(true);
  const retryCountRef = useRef(0);

  const API_BASE = '/api/csdai';

  const checkBackendStatus = async () => {
    if (!isMountedRef.current) return;
    
    console.log('🔍 Global backend check...', new Date().toLocaleTimeString());
    setBackendStatus('checking');
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log('⏰ Global backend check timeout');
        controller.abort();
      }, 5000);
      
      const response = await fetch(`${API_BASE}`, {
        signal: controller.signal,
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        if (isMountedRef.current) {
          const status = data.success ? 'connected' : 'error';
          console.log('✅ Global backend status:', status, data);
          setBackendStatus(status);
          if (status === 'connected') {
            retryCountRef.current = 0; // Reset retry count on success
          }
        }
      } else {
        console.log('❌ Global backend response not ok:', response.status);
        if (isMountedRef.current) {
          setBackendStatus('error');
        }
      }
    } catch (error) {
      console.error('❌ Global backend connection failed:', error);
      if (isMountedRef.current) {
        setBackendStatus('error');
        retryCountRef.current++;
      }
    }
  };

  // Start global backend monitoring immediately when app loads
  useEffect(() => {
    let connectionInterval: NodeJS.Timeout;
    
    const startGlobalMonitoring = () => {
      console.log('🚀 Starting global backend monitoring...');
      
      // Initial check immediately
      checkBackendStatus();
      
      // Set up persistent monitoring every 30 seconds (reduced frequency)
      connectionInterval = setInterval(() => {
        if (isMountedRef.current) {
          // Only check if backend is not connected or if it's been a while
          if (backendStatus !== 'connected') {
            checkBackendStatus();
          } else {
            // Reduce checks when connected - only check every 30 seconds
            console.log('⚡ Backend still connected, skipping check');
          }
        }
      }, 30000); // Increased from 10s to 30s
    };

    // Start monitoring after a brief delay to ensure app is ready
    const startTimeout = setTimeout(startGlobalMonitoring, 500);

    // Cleanup function
    return () => {
      isMountedRef.current = false;
      clearTimeout(startTimeout);
      if (connectionInterval) clearInterval(connectionInterval);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const value: BackendContextType = {
    backendStatus,
    checkBackendStatus,
    isBackendReady: backendStatus === 'connected'
  };

  return (
    <BackendContext.Provider value={value}>
      {children}
    </BackendContext.Provider>
  );
}
