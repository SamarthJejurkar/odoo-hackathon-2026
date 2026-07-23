
import React, { useEffect, useState } from 'react';
import PageContainer from '../components/PageContainer';
import { fetchDepartments, apiService } from '../services/api';
import { Plus, X, UserPlus, PlayCircle, CheckSquare, Lock } from 'lucide-react';

const ITEM_OUTCOMES = ['verified', 'missing', 'damaged'];

function cap(s) {
  return s ? s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : '';
}

function cycleStatusStyle(status) {
  const styles = {
    planned: 'bg-surface-100 text-surface-600',
    in_progress: 'bg-blue-100 text-blue-700',
    closed: 'bg-green-100 text-green-700',
  };
  return styles[status] || 'bg-surface-100 text-surface-600';
}

// ---------- Create Cycle Modal ----------
function CreateCycleModal({ onClose, onCreated }) {
  const [departments, setDepartments] = useState([]);
  const [name, setName] = useState('');
  const [scopeDepartmentId, setScopeDepartmentId] = useState('');
  const [scopeLocation, setScopeLocation] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { fetchDepartments().then(setDepartments).catch(() => setDepartments([])); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!name.trim() || !startDate || !endDate) {
      setError('Name, start date, and end date are required.');
      return;
    }
    const payload = { name: name.trim(), start_date: startDate, end_date: endDate };
    if (scopeDepartmentId) payload.scope_department_id = Number(scopeDepartmentId);
    if (scopeLocation.trim()) payload.scope_location = scopeLocation.trim();

    setSubmitting(true);
    try {
      const created = await apiService.post('audit-cycles', payload);
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
          <h2 className="text-lg font-semibold">New Audit Cycle</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Name *</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="w-full p-2 border rounded bg-surface-50" placeholder="e.g. Q3 2026 HQ Audit" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Scope: Department</label>
            <select value={scopeDepartmentId} onChange={(e) => setScopeDepartmentId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              <option value="">Any / not scoped</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Scope: Location</label>
            <input value={scopeLocation} onChange={(e) => setScopeLocation(e.target.value)} className="w-full p-2 border rounded bg-surface-50" placeholder="e.g. HQ - 3rd Floor" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Date *</label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full p-2 border rounded bg-surface-50" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date *</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full p-2 border rounded bg-surface-50" />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Creating...' : 'Create Cycle'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---------- Assign Auditor Modal ----------
function AssignAuditorModal({ cycle, onClose, onAssigned }) {
  const [users, setUsers] = useState([]);
  const [auditorId, setAuditorId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { apiService.get('users').then(setUsers).catch(() => setUsers([])); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!auditorId) { setError('Select an auditor.'); return; }
    setSubmitting(true);
    try {
      await apiService.post(`audit-cycles/${cycle.id}/auditors`, { auditor_id: Number(auditorId) });
      onAssigned();
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
          <h2 className="text-lg font-semibold">Assign Auditor — {cycle.name}</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}
          <div>
            <label className="block text-sm font-medium mb-1">Auditor</label>
            <select value={auditorId} onChange={(e) => setAuditorId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              <option value="">Select a user</option>
              {users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Assigning...' : 'Assign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---------- Cycle Items / Verification Modal ----------
function CycleItemsModal({ cycle, onClose, onCycleUpdated }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [closing, setClosing] = useState(false);
  const [closeResult, setCloseResult] = useState(null);

  const load = () =>
    apiService.get(`audit-cycles/${cycle.id}/items`)
      .then(setItems)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const markItem = async (itemId, verification_status) => {
    try {
      const updated = await apiService.post(`audit-cycles/items/${itemId}/verify`, { verification_status });
      setItems((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleClose = async () => {
    setClosing(true);
    setError(null);
    try {
      const result = await apiService.post(`audit-cycles/${cycle.id}/close`, {});
      setCloseResult(result);
      onCycleUpdated(result.cycle);
    } catch (err) {
      setError(err.message);
    } finally {
      setClosing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-2xl max-h-[85vh] overflow-y-auto">
        <div className="flex justify-between items-center px-6 py-4 border-b sticky top-0 bg-white dark:bg-surface-800">
          <h2 className="text-lg font-semibold">Verify Items — {cycle.name}</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <div className="p-6 space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>}

          {closeResult && (
            <div className="text-sm bg-green-50 text-green-700 px-3 py-2 rounded">
              Cycle closed. {closeResult.items_transitioned_to_lost.length} asset(s) marked Lost.
              {closeResult.items_transition_failed.length > 0 && (
                <span> {closeResult.items_transition_failed.length} item(s) failed to transition.</span>
              )}
            </div>
          )}

          {loading ? (
            <p className="text-sm text-surface-500">Loading items...</p>
          ) : items.length === 0 ? (
            <p className="text-sm text-surface-500">
              No items in this cycle yet — items are generated when the cycle is started.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-surface-500 border-b">
                <tr>
                  <th className="py-2">Asset ID</th>
                  <th className="py-2">Status</th>
                  <th className="py-2 text-right">Mark As</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {items.map((item) => (
                  <tr key={item.id}>
                    <td className="py-3">#{item.asset_id}</td>
                    <td className="py-3">{cap(item.verification_status)}</td>
                    <td className="py-3 text-right">
                      {item.verification_status === 'pending' ? (
                        <div className="flex justify-end gap-2">
                          {ITEM_OUTCOMES.map((o) => (
                            <button
                              key={o}
                              onClick={() => markItem(item.id, o)}
                              className="text-xs px-2 py-1 rounded border hover:bg-surface-50"
                            >
                              {cap(o)}
                            </button>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs text-surface-400">Recorded</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {cycle.status === 'in_progress' && !closeResult && (
            <div className="flex justify-end pt-4 border-t">
              <button
                onClick={handleClose}
                disabled={closing}
                className="flex items-center gap-2 px-4 py-2 rounded text-sm bg-brand-orange text-white font-medium disabled:opacity-60"
              >
                <Lock className="w-4 h-4" /> {closing ? 'Closing...' : 'Close Cycle'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------- Main page ----------
export default function Audit() {
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [assignTarget, setAssignTarget] = useState(null);
  const [itemsTarget, setItemsTarget] = useState(null);

  const load = () => apiService.get('audit-cycles').then((data) => { setCycles(data); setLoading(false); });
  useEffect(() => { load(); }, []);

  const replaceCycle = (updated) => setCycles((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));

  const startCycle = async (cycle) => {
    try {
      const updated = await apiService.post(`audit-cycles/${cycle.id}/start`, {});
      replaceCycle(updated);
    } catch (err) {
      alert(err.message); // simple inline feedback for a one-click action
    }
  };

  return (
    <PageContainer title="Security Audit" description="Run structured asset verification cycles.">
      <div className="flex justify-end mb-4">
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-brand-teal hover:bg-brand-teal-hover text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> New Audit Cycle
        </button>
      </div>

      <div className="bg-white dark:bg-surface-800 border rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-surface-500">Loading...</div>
        ) : cycles.length === 0 ? (
          <div className="p-12 text-center text-surface-500">No audit cycles yet.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-surface-50 dark:bg-surface-900 border-b text-left text-surface-500">
              <tr>
                <th className="px-6 py-3">Name</th>
                <th className="px-6 py-3">Dates</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {cycles.map((c) => (
                <tr key={c.id} className="hover:bg-surface-50 dark:hover:bg-surface-700/30">
                  <td className="px-6 py-4 font-medium">{c.name}</td>
                  <td className="px-6 py-4 text-surface-500">{c.start_date} → {c.end_date}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${cycleStatusStyle(c.status)}`}>
                      {cap(c.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-3">
                      {c.status === 'planned' && (
                        <>
                          <button onClick={() => setAssignTarget(c)} className="flex items-center gap-1 text-brand-teal hover:underline text-xs font-medium">
                            <UserPlus className="w-3.5 h-3.5" /> Assign Auditor
                          </button>
                          <button onClick={() => startCycle(c)} className="flex items-center gap-1 text-brand-teal hover:underline text-xs font-medium">
                            <PlayCircle className="w-3.5 h-3.5" /> Start Cycle
                          </button>
                        </>
                      )}
                      {c.status === 'in_progress' && (
                        <button onClick={() => setItemsTarget(c)} className="flex items-center gap-1 text-brand-teal hover:underline text-xs font-medium">
                          <CheckSquare className="w-3.5 h-3.5" /> Verify Items
                        </button>
                      )}
                      {c.status === 'closed' && (
                        <button onClick={() => setItemsTarget(c)} className="text-xs text-surface-400 hover:underline">
                          View Results
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showCreate && (
        <CreateCycleModal onClose={() => setShowCreate(false)} onCreated={(created) => setCycles((prev) => [created, ...prev])} />
      )}
      {assignTarget && (
        <AssignAuditorModal cycle={assignTarget} onClose={() => setAssignTarget(null)} onAssigned={() => {}} />
      )}
      {itemsTarget && (
        <CycleItemsModal cycle={itemsTarget} onClose={() => setItemsTarget(null)} onCycleUpdated={replaceCycle} />
      )}
    </PageContainer>
  );
}