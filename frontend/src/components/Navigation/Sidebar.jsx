import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Building2, MonitorSmartphone, 
  ArrowRightLeft, CalendarDays, Wrench, 
  ShieldCheck, BarChart3
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Organization', path: '/organization', icon: Building2 },
  { name: 'Assets', path: '/assets', icon: MonitorSmartphone },
  { name: 'Allocation', path: '/allocation', icon: ArrowRightLeft },
  { name: 'Booking', path: '/booking', icon: CalendarDays },
  { name: 'Maintenance', path: '/maintenance', icon: Wrench },
  { name: 'Audit', path: '/audit', icon: ShieldCheck },
  { name: 'Reports', path: '/reports', icon: BarChart3 },
];

export default function Sidebar({ isOpen }) {
  return (
    <aside 
      className={`flex flex-col bg-surface-900 text-surface-200 transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-20'} hidden md:flex flex-shrink-0`}
    >
      <div className="h-16 flex items-center justify-center border-b border-surface-800 px-4">
        <div className="flex items-center gap-3 w-full">
          <div className="w-8 h-8 rounded bg-primary-600 flex-shrink-0 flex items-center justify-center text-white font-bold tracking-wider">
            AF
          </div>
          {isOpen && <span className="font-semibold text-white tracking-wide truncate">AssetFlow</span>}
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors group ${isActive ? 'bg-primary-600/10 text-primary-400 font-medium' : 'hover:bg-surface-800 hover:text-white'}`}
              title={!isOpen ? item.name : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {isOpen && <span className="truncate">{item.name}</span>}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}