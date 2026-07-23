import React, { useState, useEffect } from 'react';
import { fetchEmployees, fetchDepartments, apiService } from '../services/api';
import { UserCog, ArrowRight, ShieldCheck, X } from 'lucide-react';

function cap(s) {
  return s ? s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : '';
}

function PromoteModal({ user, onClose, onPromoted }) {
  const [departments, setDepartments] = useState([]);
  const [target, setTarget] = useState('department_head'); // 'department_head' | 'asset_manager'
  const [departmentId, setDepartmentId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { fetchDepartments().then(setDepartments).catch(() => setDepartments([])); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (target === 'department_head' && !departmentId) {
      setError('Select a department to assign as head of.');
      return;
    }

    setSubmitting(true);
    try {
      if (target === 'department_head') {
        await apiService.post(`departments/${departmentId}/assign-head`, { user_id: user.id });
      } else {
        await apiService.post(`users/${user.id}/promote-asset-manager`, {});
      }
      onPromoted();
      onClose();
    } catch (err) {
      setError(err.message || 'Promotion failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-sm">
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Promote {user.full_name}</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}

          <div className="flex gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input type="radio" checked={target === 'department_head'} onChange={() => setTarget('department_head')} />
              Department Head
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" checked={target === 'asset_manager'} onChange={() => setTarget('asset_manager')} />
              Asset Manager
            </label>
          </div>

          {target === 'department_head' && (
            <div>
              <label className="block text-sm font-medium mb-1">Department</label>
              <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
                <option value="">Select department</option>
                {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Promoting...' : 'Confirm Promotion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Organization() {
  const [users, setUsers] = useState([]);
  const [promoteTarget, setPromoteTarget] = useState(null);

  const load = () => fetchEmployees().then(setUsers);
  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">User Role Management</h1>
      <div className="bg-white dark:bg-surface-800 p-6 border border-surface-200 dark:border-surface-700 rounded-lg shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-surface-500 border-b">
              <th className="pb-4">Name</th>
              <th className="pb-4">Current Role</th>
              <th className="pb-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {users.map((u) => (
              <tr key={u.id}>
                <td className="py-4 font-medium">{u.full_name}</td>
                <td className="py-4 text-brand-teal font-medium flex items-center gap-2">
                  {u.role === 'admin' && <ShieldCheck className="w-4 h-4 text-brand-orange" />}
                  {cap(u.role)}
                </td>
                <td className="py-4 text-right">
                  {u.role !== 'admin' ? (
                    <button
                      onClick={() => setPromoteTarget(u)}
                      className="text-sm bg-surface-100 hover:bg-surface-200 px-3 py-1 rounded flex items-center gap-2 ml-auto transition-colors"
                    >
                      Promote <ArrowRight className="w-4 h-4" />
                    </button>
                  ) : (
                    <span className="text-xs text-surface-400 italic">System Admin</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {promoteTarget && (
        <PromoteModal user={promoteTarget} onClose={() => setPromoteTarget(null)} onPromoted={load} />
      )}
    </div>
  );
}