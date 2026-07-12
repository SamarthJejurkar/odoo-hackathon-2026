import React from 'react';
import PageContainer from '../components/PageContainer';
import { ShieldAlert, History } from 'lucide-react';

export default function Audit() {
  const logs = [
    { id: 1, action: "Asset Tag 'LAP-001' moved to Maintenance", time: "2 hours ago" },
    { id: 2, action: "User 'Anushka' promoted to Manager", time: "5 hours ago" }
  ];

  return (
    <PageContainer title="Security Audit" description="Review system activity logs.">
      <div className="bg-white dark:bg-surface-800 border rounded-lg shadow-sm divide-y">
        {logs.map(log => (
          <div key={log.id} className="p-4 flex items-center gap-4">
            <div className="p-2 bg-red-50 text-red-600 rounded-full">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <p className="text-sm font-medium">{log.action}</p>
              <p className="text-xs text-surface-500">{log.time}</p>
            </div>
          </div>
        ))}
      </div>
    </PageContainer>
  );
}