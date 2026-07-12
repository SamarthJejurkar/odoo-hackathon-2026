import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Navigation/Sidebar';
import Header from '../components/Navigation/Header';

export default function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full bg-surface-50 overflow-hidden font-sans">
      <Sidebar isOpen={isSidebarOpen} />
      
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
        
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl">
            {/* The Outlet renders whatever page component matches the current URL */}
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}