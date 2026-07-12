import React from 'react';
import PageContainer from '../components/PageContainer';
import { Calendar, Clock, Plus } from 'lucide-react';

export default function Booking() {
  return (
    <PageContainer title="Resource Booking" description="Manage shared asset schedules.">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-surface-800 p-6 border rounded-lg shadow-sm">
            <h2 className="font-medium mb-4">Active Bookings</h2>
            <div className="p-4 border rounded-md flex justify-between items-center bg-surface-50 dark:bg-surface-900">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-brand-teal" />
                <span>Conference Room A - Meeting</span>
              </div>
              <span className="text-sm font-mono">14:00 - 15:30</span>
            </div>
          </div>
        </div>
        <button className="h-full min-h-[150px] border-2 border-dashed border-surface-300 rounded-lg flex flex-col items-center justify-center gap-2 hover:border-brand-teal hover:text-brand-teal transition">
          <Plus className="w-8 h-8" />
          <span className="font-medium">New Booking</span>
        </button>
      </div>
    </PageContainer>
  );
}