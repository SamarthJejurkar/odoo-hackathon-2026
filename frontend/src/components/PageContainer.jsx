// src/components/PageContainer.jsx
import React from 'react';
import { Loader2 } from 'lucide-react';

export default function PageContainer({ title, description, children, loading }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-brand-teal" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-surface-200 dark:border-surface-700 pb-6">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">{title}</h1>
        {description && <p className="text-surface-500 mt-1">{description}</p>}
      </div>
      <div>
        {children}
      </div>
    </div>
  );
}