import React, { useEffect, useState } from 'react';
import { fetchAssets, fetchEmployees } from '../services/api';
import { Shield, Package, User, CheckCircle } from 'lucide-react';

export default function Allocation() {
  const [assets, setAssets] = useState([]);
  const [users, setUsers] = useState([]);
  // MOCK: Toggle this between 'ADMIN' and 'EMPLOYEE' to see the security logic in action
  const [userRole] = useState('ADMIN'); 

  useEffect(() => {
    Promise.all([fetchAssets(), fetchEmployees()]).then(([a, u]) => {
      setAssets(a);
      setUsers(u);
    });
  }, []);

  // --- EMPLOYEE VIEW ---
  if (userRole === 'EMPLOYEE') {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">My Allocated Assets</h1>
        <div className="bg-white p-6 border rounded-lg shadow-sm">
          <p className="text-surface-500">You are currently assigned:</p>
          <ul className="mt-4 space-y-2">
            {assets.filter(a => a.status === 'ALLOCATED').map(a => (
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
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-2">
        <Shield className="text-brand-orange" />
        <h1 className="text-2xl font-semibold">Asset Allocation (Admin Mode)</h1>
      </div>

      <div className="bg-white p-6 border rounded-lg shadow-sm space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Select Asset</label>
          <select className="w-full p-2 border rounded bg-surface-50">
            {assets.filter(a => a.status === 'AVAILABLE').map(a => (
              <option key={a.id} value={a.id}>{a.name} ({a.asset_tag})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Assign To Employee</label>
          <select className="w-full p-2 border rounded bg-surface-50">
            {users.map(u => (
              <option key={u.id} value={u.id}>{u.full_name}</option>
            ))}
          </select>
        </div>

        <button 
          onClick={() => alert("Allocation successful! Data sent to backend.")}
          className="w-full bg-brand-teal text-white py-2 rounded font-medium hover:bg-brand-teal-hover flex justify-center items-center gap-2"
        >
          <CheckCircle className="w-4 h-4" /> Confirm Allocation
        </button>
      </div>
    </div>
  );
}