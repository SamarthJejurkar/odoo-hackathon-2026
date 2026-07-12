import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Login from './pages/Login';

// A temporary placeholder component to test the layout space
const PlaceholderPage = ({ title }) => (
  <div className="bg-surface-900/50 p-8 rounded-lg border border-surface-800">
    <h1 className="text-2xl font-medium text-white">{title}</h1>
    <p className="text-surface-500 mt-2 font-mono text-sm">System module pending initialization...</p>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Unprotected Route for Authentication */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes wrapped in the Technical Layout */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<PlaceholderPage title="System Dashboard" />} />
          <Route path="organization" element={<PlaceholderPage title="Organization Setup" />} />
          <Route path="assets" element={<PlaceholderPage title="Asset Telemetry" />} />
          <Route path="allocation" element={<PlaceholderPage title="Node Allocation" />} />
          <Route path="booking" element={<PlaceholderPage title="Resource Booking" />} />
          <Route path="maintenance" element={<PlaceholderPage title="Maintenance Logs" />} />
          <Route path="audit" element={<PlaceholderPage title="Security Audit" />} />
          <Route path="reports" element={<PlaceholderPage title="Data Analytics" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;