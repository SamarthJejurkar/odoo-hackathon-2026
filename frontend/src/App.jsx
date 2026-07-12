import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';

// A temporary placeholder component to test the layout space
const PlaceholderPage = ({ title }) => (
  <div className="bg-white p-8 rounded-lg shadow-sm border border-surface-200">
    <h1 className="text-2xl font-bold text-surface-900">{title}</h1>
    <p className="text-surface-600 mt-2">This module is under construction.</p>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<PlaceholderPage title="Dashboard" />} />
          <Route path="organization" element={<PlaceholderPage title="Organization Setup" />} />
          <Route path="assets" element={<PlaceholderPage title="Asset Directory" />} />
          <Route path="allocation" element={<PlaceholderPage title="Allocation & Transfer" />} />
          <Route path="booking" element={<PlaceholderPage title="Resource Booking" />} />
          <Route path="maintenance" element={<PlaceholderPage title="Maintenance" />} />
          <Route path="audit" element={<PlaceholderPage title="Audit Cycles" />} />
          <Route path="reports" element={<PlaceholderPage title="Reports & Analytics" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;