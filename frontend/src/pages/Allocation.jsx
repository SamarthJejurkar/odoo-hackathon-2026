import React, { useEffect, useState } from 'react';
import { fetchAssets, fetchEmployees, apiService } from '../services/api';
import { Shield, Package, CheckCircle } from 'lucide-react';

export default function Allocation() {
  const [assets, setAssets] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [assetId, setAssetId] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [expectedReturnDate, setExpectedReturnDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // MOCK: Toggle this between 'ADMIN' and 'EMPLOYEE' to see the security logic in action
 const user = JSON.parse(localStorage.getItem('user') || 'null');
const userRole = user?.role === 'employee' ? 'EMPLOYEE' : 'ADMIN';

  const loadData = () => {
    Promise.all([fetchAssets(), fetchEmployees()]).then(([a, u]) => {
      setAssets(a);
      setUsers(u);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async () => {
    setError(null);
    setSuccess(false);

    if (!assetId || !employeeId) {
      setError('Select both an asset and an employee.');
      return;
    }

    const payload = {
      asset_id: Number(assetId),
      employee_id: Number(employeeId),
    };
    if (expectedReturnDate) payload.expected_return_date = expectedReturnDate;

    setSubmitting(true);
    try {
      await apiService.post('allocations', payload);
      setSuccess(true);
      setAssetId('');
      setEmployeeId('');
      setExpectedReturnDate('');
      loadData(); // refresh so the allocated asset drops out of the AVAILABLE list
    } catch (err) {
      // Backend returns 409 with a conflict detail when the asset is already
      // actively allocated — err.message carries the envelope's message string.
      setError(err.message || 'Allocation failed.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-sm text-surface-500">Loading...</div>;
  }

  // --- EMPLOYEE VIEW ---
  if (userRole === 'EMPLOYEE') {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">My Allocated Assets</h1>
        <div className="bg-white p-6 border rounded-lg shadow-sm">
          <p className="text-surface-500">You are currently assigned:</p>
          <ul className="mt-4 space-y-2">
            {assets.filter((a) => a.status === 'allocated').map((a) => (
              <li key={a.id} className="p-3 border rounded flex items-center gap-3">
                <Package className="text-brand-teal" /> {a.name} ({a.asset_tag})
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  // --- ADMIN VIEW ---
  const availableAssets = assets.filter((a) => a.status === 'available');

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-2">
        <Shield className="text-brand-orange" />
        <h1 className="text-2xl font-semibold">Asset Allocation (Admin Mode)</h1>
      </div>

      <div className="bg-white p-6 border rounded-lg shadow-sm space-y-6">
        {error && (
          <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{error}</div>
        )}
        {success && (
          <div className="text-sm text-green-700 bg-green-50 px-3 py-2 rounded">
            Asset allocated successfully.
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-2">Select Asset</label>
          <select
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            className="w-full p-2 border rounded bg-surface-50"
          >
            <option value="">
              {availableAssets.length === 0 ? 'No available assets' : 'Choose an asset'}
            </option>
            {availableAssets.map((a) => (
              <option key={a.id} value={a.id}>{a.name} ({a.asset_tag})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Assign To Employee</label>
          <select
            value={employeeId}
            onChange={(e) => setEmployeeId(e.target.value)}
            className="w-full p-2 border rounded bg-surface-50"
          >
            <option value="">Choose an employee</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.full_name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Expected Return Date (optional)</label>
          <input
            type="date"
            value={expectedReturnDate}
            onChange={(e) => setExpectedReturnDate(e.target.value)}
            className="w-full p-2 border rounded bg-surface-50"
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full bg-brand-teal text-white py-2 rounded font-medium hover:bg-brand-teal-hover flex justify-center items-center gap-2 disabled:opacity-60"
        >
          <CheckCircle className="w-4 h-4" /> {submitting ? 'Allocating...' : 'Confirm Allocation'}
        </button>
      </div>
    </div>
  );
}