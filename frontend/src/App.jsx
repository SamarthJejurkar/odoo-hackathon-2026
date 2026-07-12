import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Allocation from './pages/Allocation';
import Organization from './pages/Organization';
import Maintenance from './pages/Maintenance';
import Booking from './pages/Booking';
import Audit from './pages/Audit';
import Reports from './pages/Reports';
// Protected Route Guard
const ProtectedRoute = ({ children, allowedRoles }) => {
  const user = JSON.parse(localStorage.getItem('user'));

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

const PlaceholderPage = ({ title }) => (
  <div className="bg-surface-50 dark:bg-surface-800/50 p-8 rounded-lg border border-surface-200 dark:border-surface-700">
    <h1 className="text-2xl font-medium text-surface-900 dark:text-white">{title}</h1>
    <p className="text-surface-500 mt-2 font-mono text-sm">System module pending initialization...</p>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          
          <Route path="dashboard" element={
            <ProtectedRoute> <Dashboard /> </ProtectedRoute>
          } />
          
          <Route path="organization" element={
            <ProtectedRoute allowedRoles={['ADMIN']}> <Organization /> </ProtectedRoute>
          } />
          
          <Route path="assets" element={
            <ProtectedRoute> <Assets /> </ProtectedRoute>
          } />
          
          <Route path="allocation" element={
            <ProtectedRoute> <Allocation /> </ProtectedRoute>
          } />
          
          <Route path="maintenance" element={
            <ProtectedRoute> <Maintenance /> </ProtectedRoute>
          } />
          
          {/* Placeholders */}
          <Route path="booking" element={<Booking />} />
<Route path="audit" element={<Audit />} />
<Route path="reports" element={<Reports />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;