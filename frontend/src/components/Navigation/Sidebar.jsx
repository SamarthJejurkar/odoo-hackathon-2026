import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Building2, Users2, MonitorSmartphone, ArrowRightLeft, CalendarDays, Wrench, ShieldCheck, BarChart3 } from 'lucide-react';

// allowedRoles: undefined means "any logged-in user can see this."
const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Organization', path: '/organization', icon: Building2, allowedRoles: ['admin'] },
  { name: 'Departments', path: '/departments', icon: Users2, allowedRoles: ['admin'] },
  { name: 'Assets', path: '/assets', icon: MonitorSmartphone },
  { name: 'Allocation', path: '/allocation', icon: ArrowRightLeft },
  { name: 'Booking', path: '/booking', icon: CalendarDays },
  { name: 'Maintenance', path: '/maintenance', icon: Wrench },
  { name: 'Audit', path: '/audit', icon: ShieldCheck },
  { name: 'Reports', path: '/reports', icon: BarChart3 },
];

export default function Sidebar({ isOpen }) {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const visibleItems = navItems.filter(
    (item) => !item.allowedRoles || (user && item.allowedRoles.includes(user.role))
  );

  return (
    <aside className={`flex flex-col bg-white dark:bg-surface-800 border-r border-surface-200 dark:border-surface-700 transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-20'} hidden md:flex flex-shrink-0 z-20`}>
      <div className="h-16 flex items-center justify-center border-b border-surface-200 dark:border-surface-700 px-4">
        <div className="flex items-center gap-3 w-full">
          <div className="w-8 h-8 bg-brand-rust flex-shrink-0 flex items-center justify-center text-white font-bold tracking-tighter text-sm rounded shadow-sm">
            AF
          </div>
          {isOpen && <span className="font-semibold text-surface-900 dark:text-white tracking-tight truncate">AssetFlow</span>}
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
        {isOpen && <p className="px-3 text-xs font-semibold uppercase tracking-wider text-surface-400 dark:text-surface-500 mb-4">Modules</p>}
        {visibleItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-md transition-all group ${isActive ? 'bg-surface-100 dark:bg-surface-700 text-surface-900 dark:text-white font-medium' : 'text-surface-600 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-surface-900 hover:text-surface-900 dark:hover:text-surface-300'}`}
              title={!isOpen ? item.name : undefined}
            >
              {({ isActive }) => (
                <>
                  <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-brand-teal' : 'text-surface-400 dark:text-surface-500 group-hover:text-surface-600 dark:group-hover:text-surface-400'}`} />
                  {isOpen && <span className="text-sm">{item.name}</span>}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}