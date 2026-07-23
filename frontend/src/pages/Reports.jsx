import React, { useEffect, useState } from 'react';
import { reportService } from '../services/api';
import PageContainer from '../components/PageContainer';
import { Download } from 'lucide-react';

export default function Reports() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    reportService.getSummary()
      .then((res) => setData(res))
      .catch((err) => setError(err.message || 'Failed to load report.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageContainer title="Data Analytics" description="Summary of asset utilization and maintenance." loading />;
  if (error) {
    return (
      <PageContainer title="Data Analytics" description="Summary of asset utilization and maintenance.">
        <div className="text-sm text-red-600 bg-red-50 px-4 py-3 rounded">{error}</div>
      </PageContainer>
    );
  }

  return (
    <PageContainer title="Data Analytics" description="Summary of asset utilization and maintenance.">
      <div className="flex justify-end mb-4">
        <button
          onClick={() => reportService.exportCsv()}
          className="flex items-center gap-2 bg-brand-teal text-white px-4 py-2 rounded hover:bg-teal-600"
        >
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Utilization by Department</h3>
          {data.utilization_by_department.length === 0 ? (
            <p className="text-sm text-surface-500">No data yet.</p>
          ) : data.utilization_by_department.map((d, i) => (
            <div key={i} className="flex justify-between py-2 border-b">
              <span>{d.department_name}</span>
              <span className="font-mono font-medium">{d.utilization_pct}%</span>
            </div>
          ))}
        </div>

        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Most Used Assets (30d)</h3>
          {data.most_used_assets.length === 0 ? (
            <p className="text-sm text-surface-500">No usage data yet.</p>
          ) : data.most_used_assets.map((a) => (
            <div key={a.asset_id} className="flex justify-between py-2 border-b">
              <span>{a.name} ({a.asset_tag})</span>
              <span className="font-mono font-medium">{a.usage_count}</span>
            </div>
          ))}
        </div>

        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Idle Assets</h3>
          {data.idle_assets.length === 0 ? (
            <p className="text-sm text-surface-500">No idle assets.</p>
          ) : data.idle_assets.map((a) => (
            <div key={a.asset_id} className="flex justify-between py-2 border-b">
              <span>{a.name} ({a.asset_tag})</span>
              <span className="font-mono font-medium">{a.days_idle}d</span>
            </div>
          ))}
        </div>

        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Maintenance Due</h3>
          {data.maintenance_due.length === 0 ? (
            <p className="text-sm text-surface-500">Nothing open.</p>
          ) : data.maintenance_due.map((a) => (
            <div key={a.asset_id} className="flex justify-between py-2 border-b text-sm">
              <span>{a.name} ({a.asset_tag}) — {a.priority}</span>
              <span className="font-mono font-medium">{a.days_open}d open</span>
            </div>
          ))}
        </div>

        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Assets Nearing Retirement</h3>
          {data.aging_assets.length === 0 ? (
            <p className="text-sm text-surface-500">No aging data.</p>
          ) : data.aging_assets.map((a) => (
            <div key={a.asset_id} className="flex justify-between py-2 border-b">
              <span>{a.name} ({a.asset_tag})</span>
              <span className="font-mono font-medium">{a.age_years}y</span>
            </div>
          ))}
        </div>

        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Maintenance Frequency</h3>
          {data.maintenance_frequency.length === 0 ? (
            <p className="text-sm text-surface-500">No history yet.</p>
          ) : data.maintenance_frequency.map((m, i) => (
            <div key={i} className="flex justify-between py-2 border-b">
              <span>{m.month}</span>
              <span className="font-mono font-medium">{m.count}</span>
            </div>
          ))}
        </div>
      </div>
    </PageContainer>
  );
}