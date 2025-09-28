'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      // Return custom fallback UI or default error message
      return this.props.fallback || (
        <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-6 mb-6">
          <div className="flex items-center space-x-3 mb-3">
            <span className="text-red-400 text-2xl">⚠️</span>
            <h3 className="text-xl font-bold text-red-400">Something went wrong</h3>
          </div>
          <p className="text-red-300 mb-4">
            An unexpected error occurred in this component. The error has been logged.
          </p>
          <details className="text-sm text-red-200">
            <summary className="cursor-pointer mb-2">Error Details</summary>
            <pre className="bg-red-900/20 p-2 rounded text-xs overflow-auto">
              {this.state.error?.message}
              {this.state.error?.stack && '\n\n' + this.state.error.stack}
            </pre>
          </details>
          <button
            className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors duration-200"
            onClick={() => this.setState({ hasError: false, error: undefined })}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}