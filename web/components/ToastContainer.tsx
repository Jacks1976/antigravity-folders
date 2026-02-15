'use client';

import React from 'react';
import { useToast, Toast, ToastType } from '@/lib/toast-context';

function ToastIcon({ type }: { type: ToastType }) {
  switch (type) {
    case 'success':
      return <span className="text-lg">✓</span>;
    case 'error':
      return <span className="text-lg">✕</span>;
    case 'warning':
      return <span className="text-lg">⚠</span>;
    case 'info':
    default:
      return <span className="text-lg">ℹ</span>;
  }
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: () => void }) {
  const bgColor: Record<ToastType, string> = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const iconBgColor: Record<ToastType, string> = {
    success: 'bg-green-100 text-green-600',
    error: 'bg-red-100 text-red-600',
    warning: 'bg-yellow-100 text-yellow-600',
    info: 'bg-blue-100 text-blue-600',
  };

  return (
    <div
      className={`border rounded-lg p-4 shadow-md flex gap-3 items-start max-w-sm animate-bounce-in ${bgColor[toast.type]}`}
      role="alert"
    >
      <div className={`p-2 rounded flex-shrink-0 ${iconBgColor[toast.type]}`}>
        <ToastIcon type={toast.type} />
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium">{toast.message}</p>
      </div>
      <button
        onClick={onRemove}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Fechar notificação"
      >
        ✕
      </button>
    </div>
  );
}

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 flex flex-col gap-3 z-50 pointer-events-none">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastItem toast={toast} onRemove={() => removeToast(toast.id)} />
        </div>
      ))}
    </div>
  );
}
