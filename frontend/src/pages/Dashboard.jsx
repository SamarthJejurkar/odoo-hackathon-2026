import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import PageContainer from '../components/PageContainer';

export default function Dashboard() {
  const [allocations, setAllocations] = useState([]);

  useEffect(() => {
    apiService.get('allocations?status=active').then((data) => {
      setAllocations(data ?? []);
    });
  }, []);

  return (
    <PageContainer title="System Overview" description="Live asset distribution and tracking.">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <p className="text-sm text-surface-500">Total Allocated</p>
          <h2 className="text-3xl font-bold">{allocations.length}</h2>
        </div>
      </div>

      <div className="bg-white border rounded-lg shadow-sm">
        <div className="p-6 border-b">
          <h3 className="font-semibold">Recent Allocations</h3>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-surface-50">
            <tr className="text-left text-surface-500">
              <th className="px-6 py-3">Asset ID</th>
              <th className="px-6 py-3">Allocated To (Employee ID)</th>
              <th className="px-6 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {allocations.map((a) => (
              <tr key={a.id}>
                <td className="px-6 py-4 font-medium">{a.asset_id}</td>
                <td className="px-6 py-4">{a.employee_id ?? a.department_id ?? 'Unassigned'}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-teal-100 text-teal-700 rounded text-xs uppercase">
                    {a.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageContainer>
  );
}