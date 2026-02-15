/**
 * Error Boundary Component for catching React errors
 */
'use client';

import React, { ReactNode, ErrorInfo } from 'react';
import Link from 'next/link';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      errorInfo,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen bg-red-50">
          <div className="max-w-md w-full space-y-6 text-center p-6 bg-white rounded-lg shadow-md border border-red-200">
            <div className="text-6xl text-red-500">⚠️</div>
            
            <div>
              <h1 className="text-3xl font-bold text-red-800 mb-2">Algo deu errado</h1>
              <p className="text-gray-600">Desculpe, encontramos um erro inesperado.</p>
            </div>

            <div className="bg-red-50 border border-red-200 rounded p-4 text-left">
              <p className="text-sm font-mono text-red-700 break-words">
                {this.state.error?.message || 'Erro desconhecido'}
              </p>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <details className="text-left">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700">
                  Detalhes do erro (desenvolvimento)
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-40">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors font-medium"
              >
                Recarregar página
              </button>
              <Link
                href="/"
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors font-medium text-center"
              >
                Ir para home
              </Link>
            </div>

            <p className="text-xs text-gray-500">
              Se o problema persistir, entre em contato com o administrador.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
