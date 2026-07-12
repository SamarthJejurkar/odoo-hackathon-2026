import React, { useState, useEffect } from 'react';
import { fetchEmployees } from '../services/api';
import { UserCog, ArrowRight, ShieldCheck } from 'lucide-react';

export default function Organization() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchEmployees().then(setUsers);
  }, []);

  const promoteUser = (userId) => {
    alert(`System: Promoting User ${userId} via OrganizationSetup Service.`);
  };

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
            {users.map(u => (
              <tr key={u.id}>
                <td className="py-4 font-medium">{u.full_name}</td>
                <td className="py-4 text-brand-teal font-medium flex items-center gap-2">
                  {u.role === 'ADMIN' && <ShieldCheck className="w-4 h-4 text-brand-orange" />}
                  {u.role}
                </td>
                <td className="py-4 text-right">
                  {/* LOGIC: If role is already ADMIN, do not show button */}
                  {u.role !== 'ADMIN' ? (
                    <button 
                      onClick={() => promoteUser(u.id)}
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
    </div>
  );
}