import React, { useEffect, useState } from 'react';
import PageContainer from '../components/PageContainer';
import { fetchAssets, fetchMaintenanceRequests, apiService } from '../services/api';
import { CheckCircle, Clock, AlertCircle, Wrench, Plus, X } from 'lucide-react';

const PRIORITIES = ['low', 'medium', 'high', 'critical'];
const RESOLUTION_TARGETS = ['available', 'lost', 'retired', 'disposed'];

function cap(s) {
  return s ? s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : '';
}

function getStatusIcon(status) {
  switch (status) {
    case 'in_progress': return <Clock className="w-4 h-4 text-brand-orange" />;
    case 'pending': return <AlertCircle className="w-4 h-4 text-red-500" />;
    case 'resolved': return <CheckCircle className="w-4 h-4 text-brand-teal" />;
    default: return <Wrench className="w-4 h-4 text-surface-400" />;
  }
}

// ---------- Raise Request Modal ----------
function RaiseRequestModal({ onClose, onCreated }) {
  const [assets, setAssets] = useState([]);
  const [assetId, setAssetId] = useState('');
  const [issue, setIssue] = useState('');
  const [priority, setPriority] = useState('medium');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { fetchAssets().then(setAssets); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!assetId || !issue.trim()) {
      setError('Asset and issue description are required.');
      return;
    }
    setSubmitting(true);
    try {
      const created = await apiService.post('maintenance-requests', {
        asset_id: Number(assetId),
        issue_description: issue.trim(),
        priority,
      });
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
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-md">
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Raise Maintenance Request</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Asset *</label>
            <select value={assetId} onChange={(e) => setAssetId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              <option value="">Select asset</option>
              {assets.map((a) => <option key={a.id} value={a.id}>{a.name} ({a.asset_tag})</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Issue *</label>
            <textarea value={issue} onChange={(e) => setIssue(e.target.value)} className="w-full p-2 border rounded bg-surface-50" rows={3} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Priority</label>
            <select value={priority} onChange={(e) => setPriority(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              {PRIORITIES.map((p) => <option key={p} value={p}>{cap(p)}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Submitting...' : 'Submit Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---------- Small action modals (reject reason / technician / resolve) ----------
function PromptModal({ title, fields, onClose, onSubmit }) {
  const [values, setValues] = useState(Object.fromEntries(fields.map((f) => [f.name, f.default || ''])));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit(values);
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
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}
          {fields.map((f) => (
            <div key={f.name}>
              <label className="block text-sm font-medium mb-1">{f.label}</label>
              {f.type === 'select' ? (
                <select
                  value={values[f.name]}
                  onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  className="w-full p-2 border rounded bg-surface-50"
                >
                  {f.options.map((o) => <option key={o} value={o}>{cap(o)}</option>)}
                </select>
              ) : (
                <input
                  value={values[f.name]}
                  onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
                  className="w-full p-2 border rounded bg-surface-50"
                />
              )}
            </div>
          ))}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Saving...' : 'Confirm'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---------- Row actions, by status ----------
function RequestActions({ req, onReplace, openModal }) {
  const patch = (fn) => async (values) => {
    const updated = await fn(values);
    onReplace(updated);
  };

  switch (req.status) {
    case 'pending':
      return (
        <div className="flex gap-3 justify-center">
          <button
            onClick={async () => onReplace(await apiService.post(`maintenance-requests/${req.id}/approve`, {}))}
            className="text-brand-teal hover:underline text-xs font-medium"
          >
            Approve
          </button>
          <button
            onClick={() => openModal(
              <PromptModal
                title="Reject Request"
                fields={[{ name: 'rejection_reason', label: 'Reason' }]}
                onClose={() => openModal(null)}
                onSubmit={patch((v) => apiService.post(`maintenance-requests/${req.id}/reject`, v))}
              />
            )}
            className="text-red-600 hover:underline text-xs font-medium"
          >
            Reject
          </button>
        </div>
      );
    case 'approved':
      return (
        <button
          onClick={() => openModal(
            <PromptModal
              title="Assign Technician"
              fields={[{ name: 'technician_name', label: 'Technician Name' }]}
              onClose={() => openModal(null)}
              onSubmit={patch((v) => apiService.post(`maintenance-requests/${req.id}/assign-technician`, v))}
            />
          )}
          className="text-brand-teal hover:underline text-xs font-medium"
        >
          Assign Technician
        </button>
      );
    case 'technician_assigned':
      return (
        <button
          onClick={async () => onReplace(await apiService.post(`maintenance-requests/${req.id}/start`, {}))}
          className="text-brand-teal hover:underline text-xs font-medium"
        >
          Start Work
        </button>
      );
    case 'in_progress':
      return (
        <button
          onClick={() => openModal(
            <PromptModal
              title="Resolve Request"
              fields={[
                { name: 'resolution_notes', label: 'Resolution Notes' },
                { name: 'resulting_status', label: 'Resulting Asset Status', type: 'select', options: RESOLUTION_TARGETS, default: 'available' },
              ]}
              onClose={() => openModal(null)}
              onSubmit={patch((v) => apiService.post(`maintenance-requests/${req.id}/resolve`, v))}
            />
          )}
          className="text-brand-teal hover:underline text-xs font-medium"
        >
          Resolve
        </button>
      );
    default:
      return <span className="text-xs text-surface-400">—</span>;
  }
}

export default function Maintenance() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRaise, setShowRaise] = useState(false);
  const [activeModal, setActiveModal] = useState(null);

  const load = () => fetchMaintenanceRequests().then((data) => { setRequests(data); setLoading(false); });
  useEffect(() => { load(); }, []);

  const replace = (updated) => setRequests((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));

  return (
    <PageContainer title="Maintenance Requests" description="Monitor and resolve active maintenance tickets.">
      <div className="flex justify-end mb-4">
        <button
          onClick={() => setShowRaise(true)}
          className="flex items-center gap-2 bg-brand-teal hover:bg-brand-teal-hover text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> Raise Request
        </button>
      </div>

      <div className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-surface-500">Loading...</div>
        ) : requests.length === 0 ? (
          <div className="p-12 text-center text-surface-500">No maintenance requests yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-surface-50 dark:bg-surface-900 border-b border-surface-200 dark:border-surface-700">
              <tr className="text-left text-surface-600 dark:text-surface-400">
                <th className="px-6 py-4 font-medium">Asset ID</th>
                <th className="px-6 py-4 font-medium">Issue</th>
                <th className="px-6 py-4 font-medium">Priority</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
              {requests.map((req) => (
                <tr key={req.id} className="hover:bg-surface-50 dark:hover:bg-surface-700/30 transition-colors">
                  <td className="px-6 py-4 font-medium">#{req.asset_id}</td>
                  <td className="px-6 py-4 text-surface-600">{req.issue_description}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${req.priority === 'high' || req.priority === 'critical' ? 'bg-red-100 text-red-700' : 'bg-surface-100 text-surface-600'}`}>
                      {cap(req.priority)}
                    </span>
                  </td>
                  <td className="px-6 py-4 flex items-center gap-2">
                    {getStatusIcon(req.status)}
                    <span className="text-surface-700 dark:text-surface-300">{cap(req.status)}</span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <RequestActions req={req} onReplace={replace} openModal={setActiveModal} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showRaise && (
        <RaiseRequestModal onClose={() => setShowRaise(false)} onCreated={(created) => setRequests((prev) => [created, ...prev])} />
      )}
      {activeModal}
    </PageContainer>
  );
}