// src/pages/Reports.jsx
import React, { useEffect, useState } from 'react';
import { reportService } from '../services/api';
import PageContainer from '../components/PageContainer';
import { Download } from 'lucide-react';

export default function Reports() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportService.getSummary()
      .then(res => { setData(res); setLoading(false); })
      .catch(err => console.error("Report fetch error:", err));
  }, []);

  if (loading) return <PageContainer loading={loading} />;

  return (
    <PageContainer title="Data Analytics" description="Summary of asset utilization and maintenance.">
      <div className="flex justify-end mb-4">
        <button 
          onClick={reportService.exportCsv}
          className="flex items-center gap-2 bg-brand-teal text-white px-4 py-2 rounded hover:bg-teal-600"
        >
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Render your data here using the keys from your backend ReportSummary schema */}
        <div className="p-6 bg-white border rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Utilization by Department</h3>
          {data.utilization_by_department.map((d, i) => (
            <div key={i} className="flex justify-between py-2 border-b">
              <span>{d.department_name}</span>
              <span className="font-mono font-medium">{d.utilization_pct}%</span>
            </div>
          ))}
        </div>
        
        {/* Add more cards for most_used_assets, etc. */}
      </div>
    </PageContainer>
  );
}