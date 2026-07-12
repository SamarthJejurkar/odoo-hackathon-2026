import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Navigation/Sidebar';
import Header from '../components/Navigation/Header';

export default function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex flex-col h-screen w-full bg-surface-50 dark:bg-surface-900 overflow-hidden font-sans text-surface-900 dark:text-surface-300 transition-colors duration-200">
      <div className="h-1 w-full brand-gradient flex-shrink-0 z-50"></div>
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={isSidebarOpen} />
        <div className="flex flex-col flex-1 min-w-0 relative">
          <Header toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
          <main className="flex-1 overflow-y-auto p-6 md:p-8 relative z-10 bg-surface-50 dark:bg-surface-900 transition-colors duration-200">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}