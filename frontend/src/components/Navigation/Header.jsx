import React from 'react';
import { Bell, Search, Menu, User } from 'lucide-react';

export default function Header({ toggleSidebar }) {
  return (
    <header className="h-16 bg-white border-b border-surface-200 flex items-center justify-between px-4 sm:px-6 flex-shrink-0">
      <div className="flex items-center gap-4 flex-1">
        <button 
          onClick={toggleSidebar}
          className="p-2 -ml-2 rounded-md text-surface-600 hover:text-surface-900 hover:bg-surface-100 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="hidden sm:flex max-w-md w-full relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-surface-600" />
          <input 
            type="text"
            placeholder="Search AssetFlow..."
            className="w-full pl-9 pr-4 py-2 bg-surface-50 border border-surface-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-3 sm:gap-5">
        <button className="relative p-2 text-surface-600 hover:text-surface-900 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border border-white"></span>
        </button>
        
        <div className="h-8 w-px bg-surface-200 hidden sm:block"></div>
        
        <button className="flex items-center gap-2 hover:bg-surface-50 p-1.5 rounded-md transition-colors">
          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-medium">
            <User className="w-4 h-4" />
          </div>
        </button>
      </div>
    </header>
  );
}