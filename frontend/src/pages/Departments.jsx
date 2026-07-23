import React, { useEffect, useState } from 'react';
import { fetchDepartments, fetchEmployees, apiService } from '../services/api';
import { Plus, X, UserCheck, Power } from 'lucide-react';

function cap(s) {
  return s ? s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : '';
}

function CreateDepartmentModal({ departments, onClose, onCreated }) {
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [parentId, setParentId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!name.trim() || !code.trim()) {
      setError('Name and code are required.');
      return;
    }
    const payload = { name: name.trim(), code: code.trim() };
    if (parentId) payload.parent_department_id = Number(parentId);

    setSubmitting(true);
    try {
      const created = await apiService.post('departments', payload);
      onCreated(created);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-sm">
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">New Department</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Name *</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="w-full p-2 border rounded bg-surface-50" placeholder="e.g. Engineering" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Code *</label>
            <input value={code} onChange={(e) => setCode(e.target.value)} className="w-full p-2 border rounded bg-surface-50" placeholder="e.g. ENG" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Parent Department</label>
            <select value={parentId} onChange={(e) => setParentId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              <option value="">None (top-level)</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Creating...' : 'Create Department'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function AssignHeadModal({ department, onClose, onAssigned }) {
  const [users, setUsers] = useState([]);
  const [userId, setUserId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { fetchEmployees().then(setUsers).catch(() => setUsers([])); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!userId) { setError('Select an employee.'); return; }
    setSubmitting(true);
    try {
      const updated = await apiService.post(`departments/${department.id}/assign-head`, { user_id: Number(userId) });
      onAssigned(updated);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-sm">
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Assign Head — {department.name}</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Employee</label>
            <select value={userId} onChange={(e) => setUserId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              <option value="">Select an employee</option>
              {users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Assigning...' : 'Assign Head'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Departments() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [assignTarget, setAssignTarget] = useState(null);
  const [error, setError] = useState(null);

  const load = () => fetchDepartments().then((data) => { setDepartments(data); setLoading(false); });
  useEffect(() => { load(); }, []);

  const replaceDept = (updated) => setDepartments((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));

  const toggleStatus = async (dept) => {
    setError(null);
    const action = dept.status === 'active' ? 'deactivate' : 'activate';
    try {
      const updated = await apiService.patch(`departments/${dept.id}/${action}`, {});
      replaceDept(updated);
    } catch (err) {
      // e.g. 409 if trying to deactivate a department with active employees
      setError(err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Departments</h1>
          <p className="text-sm text-surface-500 mt-1">Set up your organization's department structure.</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-brand-teal hover:bg-brand-teal-hover text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> New Department
        </button>
      </div>

      {error && <div className="text-sm text-red-600 bg-red-50 px-4 py-3 rounded">{error}</div>}

      <div className="bg-white dark:bg-surface-800 border rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-surface-500">Loading...</div>
        ) : departments.length === 0 ? (
          <div className="p-12 text-center text-surface-500">No departments yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-surface-50 dark:bg-surface-900 border-b text-left text-surface-500">
              <tr>
                <th className="px-6 py-3">Name</th>
                <th className="px-6 py-3">Code</th>
                <th className="px-6 py-3">Head (User ID)</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {departments.map((d) => (
                <tr key={d.id}>
                  <td className="px-6 py-4 font-medium">{d.name}</td>
                  <td className="px-6 py-4 font-mono text-surface-500">{d.code}</td>
                  <td className="px-6 py-4">{d.department_head_id ?? '—'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${d.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-surface-100 text-surface-600'}`}>
                      {cap(d.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-3">
                      <button onClick={() => setAssignTarget(d)} className="flex items-center gap-1 text-brand-teal hover:underline text-xs font-medium">
                        <UserCheck className="w-3.5 h-3.5" /> Assign Head
                      </button>
                      <button onClick={() => toggleStatus(d)} className="flex items-center gap-1 text-surface-500 hover:underline text-xs font-medium">
                        <Power className="w-3.5 h-3.5" /> {d.status === 'active' ? 'Deactivate' : 'Activate'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showCreate && (
        <CreateDepartmentModal departments={departments} onClose={() => setShowCreate(false)} onCreated={(created) => setDepartments((prev) => [created, ...prev])} />
      )}
      {assignTarget && (
        <AssignHeadModal department={assignTarget} onClose={() => setAssignTarget(null)} onAssigned={replaceDept} />
      )}
    </div>
  );
}