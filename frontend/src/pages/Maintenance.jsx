import React from 'react';
import PageContainer from '../components/PageContainer';
import { Wrench, CheckCircle, Clock, AlertCircle } from 'lucide-react';

export default function Maintenance() {
  // Mock data representing your maintenance model
  const maintenanceTasks = [
    { id: 1, asset: "MacBook Pro (LAP-001)", issue: "Battery Swelling", status: "IN_PROGRESS", priority: "High" },
    { id: 2, asset: "Dell Monitor (MON-005)", issue: "Flickering Screen", status: "PENDING", priority: "Medium" },
    { id: 3, asset: "Logitech Mouse (MOU-002)", issue: "Sensor Error", status: "COMPLETED", priority: "Low" }
  ];

  const getStatusIcon = (status) => {
    switch(status) {
      case 'IN_PROGRESS': return <Clock className="w-4 h-4 text-brand-orange" />;
      case 'PENDING': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'COMPLETED': return <CheckCircle className="w-4 h-4 text-brand-teal" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <PageContainer 
      title="Maintenance Requests" 
      description="Monitor and resolve active maintenance tickets."
    >
      <div className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface-50 dark:bg-surface-900 border-b border-surface-200 dark:border-surface-700">
            <tr className="text-left text-surface-600 dark:text-surface-400">
              <th className="px-6 py-4 font-medium">Asset</th>
              <th className="px-6 py-4 font-medium">Issue</th>
              <th className="px-6 py-4 font-medium">Priority</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
            {maintenanceTasks.map((task) => (
              <tr key={task.id} className="hover:bg-surface-50 dark:hover:bg-surface-700/30 transition-colors">
                <td className="px-6 py-4 font-medium">{task.asset}</td>
                <td className="px-6 py-4 text-surface-600">{task.issue}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    task.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-surface-100 text-surface-600'
                  }`}>
                    {task.priority}
                  </span>
                </td>
                <td className="px-6 py-4 flex items-center gap-2">
                  {getStatusIcon(task.status)}
                  <span className="text-surface-700 dark:text-surface-300">{task.status.replace('_', ' ')}</span>
                </td>
                <td className="px-6 py-4 text-center">
                  <button className="text-brand-teal hover:underline text-xs font-medium">
                    Update Status
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageContainer>
  );
}