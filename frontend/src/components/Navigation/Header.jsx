import React, { useState, useEffect } from 'react';
import { Bell, Search, Menu, Sun, Moon } from 'lucide-react';

export default function Header({ toggleSidebar }) {
  const [isDark, setIsDark] = useState(false);

  // Check the initial theme on load
  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'));
  }, []);

  const toggleTheme = () => {
    document.documentElement.classList.toggle('dark');
    setIsDark(!isDark);
  };

  return (
    <header className="h-16 bg-white dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between px-4 sm:px-6 flex-shrink-0 z-10 transition-colors duration-200">
      <div className="flex items-center gap-4 flex-1">
        <button onClick={toggleSidebar} className="p-2 -ml-2 rounded-md text-surface-500 hover:text-surface-900 dark:hover:text-white hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors">
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="hidden sm:flex max-w-md w-full relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500" />
          <input 
            type="text"
            placeholder="Search assets..."
            className="w-full pl-10 pr-4 py-2 bg-surface-50 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-md text-surface-900 dark:text-surface-300 placeholder:text-surface-400 dark:placeholder:text-surface-500 text-sm focus:outline-none focus:border-brand-teal focus:ring-1 focus:ring-brand-teal transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        {/* The Magic Theme Toggle Button */}
        <button 
          onClick={toggleTheme}
          className="p-2 rounded-md text-surface-500 hover:text-surface-900 dark:hover:text-white transition-colors"
          title="Toggle Theme"
        >
          {isDark ? <Sun className="w-5 h-5 text-brand-yellow" /> : <Moon className="w-5 h-5" />}
        </button>

        <button className="relative p-2 text-surface-500 hover:text-surface-900 dark:hover:text-white transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-yellow rounded-full border-2 border-white dark:border-surface-800"></span>
        </button>
        
        <div className="h-6 w-px bg-surface-200 dark:bg-surface-700 hidden sm:block mx-1"></div>
        
        <button className="flex items-center gap-2 p-1 transition-colors group">
          <div className="w-8 h-8 rounded-full bg-surface-100 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 flex items-center justify-center text-surface-600 dark:text-surface-300 text-xs font-bold group-hover:border-brand-teal dark:group-hover:text-white transition-colors">
            JS
          </div>
        </button>
      </div>
    </header>
  );
}