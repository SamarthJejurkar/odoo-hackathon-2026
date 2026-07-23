import React, { useEffect, useState } from 'react';
import { fetchAssets, fetchCategories, fetchDepartments, apiService } from '../services/api';
import { Search, Filter, MoreVertical, Loader2, X, History, Pencil, RefreshCw } from 'lucide-react';

const CONDITIONS = ['new', 'good', 'fair', 'poor', 'damaged'];
const STATUSES = ['available', 'allocated', 'reserved', 'under_maintenance', 'lost', 'retired', 'disposed'];

// ---------- Register Asset Modal ----------
function RegisterAssetModal({ onClose, onCreated }) {
  const [categories, setCategories] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [form, setForm] = useState({
    name: '', category_id: '', department_id: '', serial_number: '',
    acquisition_date: '', acquisition_cost: '', condition: 'new',
    location: '', is_bookable: false,
  });

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]));
    fetchDepartments().then(setDepartments).catch(() => setDepartments([]));
  }, []);

  const handleChange = (field) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.name.trim() || !form.category_id) {
      setError('Name and category are required.');
      return;
    }
    const payload = {
      name: form.name.trim(),
      category_id: Number(form.category_id),
      condition: form.condition,
      is_bookable: form.is_bookable,
    };
    if (form.department_id) payload.department_id = Number(form.department_id);
    if (form.serial_number.trim()) payload.serial_number = form.serial_number.trim();
    if (form.acquisition_date) payload.acquisition_date = form.acquisition_date;
    if (form.acquisition_cost) payload.acquisition_cost = Number(form.acquisition_cost);
    if (form.location.trim()) payload.location = form.location.trim();

    setSubmitting(true);
    try {
      const created = await apiService.post('assets', payload);
      onCreated(created);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to register asset.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ModalShell title="Register New Asset" onClose={onClose}>
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {error && <ErrorBox message={error} />}
        <Field label="Name *">
          <input value={form.name} onChange={handleChange('name')} className={inputCls} placeholder="e.g. Dell Latitude 5420" />
        </Field>
        <Field label="Category *">
          <select value={form.category_id} onChange={handleChange('category_id')} className={inputCls}>
            <option value="">Select category</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </Field>
        <Field label="Department">
          <select value={form.department_id} onChange={handleChange('department_id')} className={inputCls}>
            <option value="">None</option>
            {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Serial Number">
            <input value={form.serial_number} onChange={handleChange('serial_number')} className={inputCls} />
          </Field>
          <Field label="Condition">
            <select value={form.condition} onChange={handleChange('condition')} className={inputCls}>
              {CONDITIONS.map((c) => <option key={c} value={c}>{cap(c)}</option>)}
            </select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Acquisition Date">
            <input type="date" value={form.acquisition_date} onChange={handleChange('acquisition_date')} className={inputCls} />
          </Field>
          <Field label="Acquisition Cost">
            <input type="number" min="0" step="0.01" value={form.acquisition_cost} onChange={handleChange('acquisition_cost')} className={inputCls} />
          </Field>
        </div>
        <Field label="Location">
          <input value={form.location} onChange={handleChange('location')} className={inputCls} placeholder="e.g. HQ - 3rd Floor" />
        </Field>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.is_bookable} onChange={handleChange('is_bookable')} />
          Shared / bookable resource
        </label>
        <FormActions onClose={onClose} submitting={submitting} submitLabel="Register Asset" submittingLabel="Registering..." />
      </form>
    </ModalShell>
  );
}

// ---------- Edit Asset Modal ----------
function EditAssetModal({ asset, onClose, onUpdated }) {
  const [categories, setCategories] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [form, setForm] = useState({
    name: asset.name || '',
    category_id: asset.category_id || '',
    department_id: asset.department_id || '',
    serial_number: asset.serial_number || '',
    acquisition_date: asset.acquisition_date || '',
    acquisition_cost: asset.acquisition_cost || '',
    condition: asset.condition || 'new',
    location: asset.location || '',
    is_bookable: !!asset.is_bookable,
  });

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]));
    fetchDepartments().then(setDepartments).catch(() => setDepartments([]));
  }, []);

  const handleChange = (field) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.name.trim() || !form.category_id) {
      setError('Name and category are required.');
      return;
    }
    const payload = {
      name: form.name.trim(),
      category_id: Number(form.category_id),
      department_id: form.department_id ? Number(form.department_id) : null,
      serial_number: form.serial_number.trim() || null,
      acquisition_date: form.acquisition_date || null,
      acquisition_cost: form.acquisition_cost ? Number(form.acquisition_cost) : null,
      condition: form.condition,
      location: form.location.trim() || null,
      is_bookable: form.is_bookable,
    };

    setSubmitting(true);
    try {
      const updated = await apiService.patch(`assets/${asset.id}`, payload);
      onUpdated(updated);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to update asset.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ModalShell title={`Edit Asset — ${asset.asset_tag}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {error && <ErrorBox message={error} />}
        <Field label="Name *">
          <input value={form.name} onChange={handleChange('name')} className={inputCls} />
        </Field>
        <Field label="Category *">
          <select value={form.category_id} onChange={handleChange('category_id')} className={inputCls}>
            <option value="">Select category</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </Field>
        <Field label="Department">
          <select value={form.department_id} onChange={handleChange('department_id')} className={inputCls}>
            <option value="">None</option>
            {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Serial Number">
            <input value={form.serial_number} onChange={handleChange('serial_number')} className={inputCls} />
          </Field>
          <Field label="Condition">
            <select value={form.condition} onChange={handleChange('condition')} className={inputCls}>
              {CONDITIONS.map((c) => <option key={c} value={c}>{cap(c)}</option>)}
            </select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Acquisition Date">
            <input type="date" value={form.acquisition_date} onChange={handleChange('acquisition_date')} className={inputCls} />
          </Field>
          <Field label="Acquisition Cost">
            <input type="number" min="0" step="0.01" value={form.acquisition_cost} onChange={handleChange('acquisition_cost')} className={inputCls} />
          </Field>
        </div>
        <Field label="Location">
          <input value={form.location} onChange={handleChange('location')} className={inputCls} />
        </Field>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.is_bookable} onChange={handleChange('is_bookable')} />
          Shared / bookable resource
        </label>
        <FormActions onClose={onClose} submitting={submitting} submitLabel="Save Changes" submittingLabel="Saving..." />
      </form>
    </ModalShell>
  );
}

// ---------- Change Status Modal ----------
function ChangeStatusModal({ asset, onClose, onChanged }) {
  const [toStatus, setToStatus] = useState(asset.status?.toLowerCase() || 'available');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const payload = { to_status: toStatus };
      if (reason.trim()) payload.reason = reason.trim();
      const updated = await apiService.post(`assets/${asset.id}/change-status`, payload);
      onChanged(updated);
      onClose();
    } catch (err) {
      setError(err.message || 'Status transition rejected.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ModalShell title={`Change Status — ${asset.asset_tag}`} onClose={onClose}>
      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {error && <ErrorBox message={error} />}
        <p className="text-sm text-surface-500">
          Current status: <span className="font-medium text-surface-900 dark:text-white">{cap(asset.status)}</span>
        </p>
        <Field label="New Status">
          <select value={toStatus} onChange={(e) => setToStatus(e.target.value)} className={inputCls}>
            {STATUSES.map((s) => <option key={s} value={s}>{cap(s)}</option>)}
          </select>
        </Field>
        <Field label="Reason (optional)">
          <input value={reason} onChange={(e) => setReason(e.target.value)} className={inputCls} placeholder="e.g. Sent for annual servicing" />
        </Field>
        <FormActions onClose={onClose} submitting={submitting} submitLabel="Update Status" submittingLabel="Updating..." />
      </form>
    </ModalShell>
  );
}

// ---------- View History Modal ----------
function HistoryModal({ asset, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiService
      .get(`assets/${asset.id}/history`)
      .then(setHistory)
      .catch((err) => setError(err.message || 'Failed to load history.'))
      .finally(() => setLoading(false));
  }, [asset.id]);

  return (
    <ModalShell title={`Status History — ${asset.asset_tag}`} onClose={onClose}>
      <div className="p-6">
        {loading && <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-brand-teal" /></div>}
        {error && <ErrorBox message={error} />}
        {!loading && !error && history.length === 0 && (
          <p className="text-sm text-surface-500 text-center py-6">No status changes recorded yet.</p>
        )}
        {!loading && history.length > 0 && (
          <ul className="space-y-3">
            {history.map((h) => (
              <li key={h.id} className="border-l-2 border-brand-teal pl-3 py-1">
                <p className="text-sm font-medium text-surface-900 dark:text-white">
                  {h.from_status ? `${cap(h.from_status)} → ${cap(h.to_status)}` : `Registered as ${cap(h.to_status)}`}
                </p>
                {h.reason && <p className="text-xs text-surface-500">{h.reason}</p>}
                <p className="text-xs text-surface-400">{new Date(h.changed_at).toLocaleString()}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </ModalShell>
  );
}

// ---------- Shared small components ----------
const inputCls = "w-full p-2 border rounded bg-surface-50 dark:bg-surface-900 dark:border-surface-700";

function cap(s) {
  return s ? s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : '';
}

function Field({ label, children }) {
  return (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      {children}
    </div>
  );
}

function ErrorBox({ message }) {
  return <div className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 px-3 py-2 rounded">{message}</div>;
}

function FormActions({ onClose, submitting, submitLabel, submittingLabel }) {
  return (
    <div className="flex justify-end gap-3 pt-2">
      <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border border-surface-200 dark:border-surface-700 text-surface-600 dark:text-surface-300">
        Cancel
      </button>
      <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal hover:bg-brand-teal-hover text-white font-medium disabled:opacity-60">
        {submitting ? submittingLabel : submitLabel}
      </button>
    </div>
  );
}

function ModalShell({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center px-6 py-4 border-b border-surface-200 dark:border-surface-700">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">{title}</h2>
          <button onClick={onClose} className="text-surface-400 hover:text-surface-900 dark:hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

// ---------- Row action dropdown ----------
function RowActionsMenu({ asset, onEdit, onChangeStatus, onHistory }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-surface-400 hover:text-surface-900 dark:hover:text-white transition-colors"
      >
        <MoreVertical className="w-4 h-4" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-1 w-44 bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-md shadow-lg z-20 text-left">
            <button
              onClick={() => { setOpen(false); onEdit(asset); }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-surface-700 dark:text-surface-200 hover:bg-surface-50 dark:hover:bg-surface-700"
            >
              <Pencil className="w-3.5 h-3.5" /> Edit
            </button>
            <button
              onClick={() => { setOpen(false); onChangeStatus(asset); }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-surface-700 dark:text-surface-200 hover:bg-surface-50 dark:hover:bg-surface-700"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Change Status
            </button>
            <button
              onClick={() => { setOpen(false); onHistory(asset); }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-surface-700 dark:text-surface-200 hover:bg-surface-50 dark:hover:bg-surface-700"
            >
              <History className="w-3.5 h-3.5" /> View History
            </button>
          </div>
        </>
      )}
    </div>
  );
}

// ---------- Main page ----------
export default function Assets() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [statusTarget, setStatusTarget] = useState(null);
  const [historyTarget, setHistoryTarget] = useState(null);

  useEffect(() => {
    fetchAssets().then((data) => {
      setAssets(data);
      setLoading(false);
    });
  }, []);

  const getStatusStyle = (status) => {
    const styles = {
      AVAILABLE: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      ALLOCATED: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      UNDER_MAINTENANCE: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    };
    return styles[status] || 'bg-surface-100 text-surface-600 dark:bg-surface-700 dark:text-surface-300';
  };

  const replaceAsset = (updated) => {
    setAssets((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-white">Asset Directory</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">Manage and track your organization's physical assets.</p>
        </div>
        <button
          onClick={() => setShowRegister(true)}
          className="bg-brand-teal hover:bg-brand-teal-hover text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm"
        >
          Register New Asset
        </button>
      </div>

      <div className="bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg shadow-sm overflow-hidden">
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
                <tr key={asset.id} className="hover:bg-surface-50 dark:hover:bg-surface-700/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-brand-rust">{asset.asset_tag}</td>
                  <td className="px-6 py-4 font-medium text-surface-900 dark:text-white">{asset.name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusStyle(asset.status)}`}>
                      {asset.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-surface-500 dark:text-surface-400">{asset.location}</td>
                  <td className="px-6 py-4 text-center">
                    <RowActionsMenu
                      asset={asset}
                      onEdit={setEditTarget}
                      onChangeStatus={setStatusTarget}
                      onHistory={setHistoryTarget}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showRegister && (
        <RegisterAssetModal
          onClose={() => setShowRegister(false)}
          onCreated={(created) => setAssets((prev) => [created, ...prev])}
        />
      )}
      {editTarget && (
        <EditAssetModal asset={editTarget} onClose={() => setEditTarget(null)} onUpdated={replaceAsset} />
      )}
      {statusTarget && (
        <ChangeStatusModal asset={statusTarget} onClose={() => setStatusTarget(null)} onChanged={replaceAsset} />
      )}
      {historyTarget && (
        <HistoryModal asset={historyTarget} onClose={() => setHistoryTarget(null)} />
      )}
    </div>
  );
}