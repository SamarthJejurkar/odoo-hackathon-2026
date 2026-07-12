import React, { useEffect, useState } from 'react';
import { fetchAssets } from '../services/api';
import { Search, Filter, MoreVertical, Loader2 } from 'lucide-react';

export default function Assets() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssets().then((data) => {
      setAssets(data);
      setLoading(false);
    });
  }, []);

  // Helper for status colors
  const getStatusStyle = (status) => {
    const styles = {
      AVAILABLE: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      ALLOCATED: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      UNDER_MAINTENANCE: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    };
    return styles[status] || 'bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-brand-teal" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-white">Asset Directory</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">Manage and track your organization's physical assets.</p>
        </div>
        <button className="bg-brand-teal hover:bg-brand-teal-hover text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm">
          Register New Asset
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg shadow-sm overflow-hidden">
        {/* Search & Filter Bar */}
        <div className="p-4 border-b border-surface-200 dark:border-surface-700 flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-surface-400" />
            <input 
              placeholder="Search by tag, serial number, or name..." 
              className="w-full pl-10 pr-4 py-2 bg-surface-50 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded text-sm focus:border-brand-teal outline-none"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border border-surface-200 dark:border-surface-700 rounded text-sm text-surface-600 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors">
            <Filter className="w-4 h-4" /> Filters
          </button>
        </div>

        {/* Data Table */}
        {assets.length === 0 ? (
          <div className="p-12 text-center text-surface-500">No assets found in the system.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-surface-50 dark:bg-surface-900 text-surface-600 dark:text-surface-400 border-b border-surface-200 dark:border-surface-700">
              <tr>
                <th className="px-6 py-3 text-left font-medium">Tag</th>
                <th className="px-6 py-3 text-left font-medium">Name</th>
                <th className="px-6 py-3 text-left font-medium">Status</th>
                <th className="px-6 py-3 text-left font-medium">Location</th>
                <th className="px-6 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
              {assets.map((asset) => (
                <tr key={asset.id} className="hover:bg-surface-50 dark:hover:bg-surface-700/50 cursor-pointer transition-colors">
                  <td className="px-6 py-4 font-mono text-brand-rust">{asset.asset_tag}</td>
                  <td className="px-6 py-4 font-medium text-surface-900 dark:text-white">{asset.name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusStyle(asset.status)}`}>
                      {asset.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-surface-500 dark:text-surface-400">{asset.location}</td>
                  <td className="px-6 py-4 text-center">
                    <button className="text-surface-400 hover:text-surface-900 dark:hover:text-white transition-colors">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}