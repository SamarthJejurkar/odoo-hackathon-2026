import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Allocation from './pages/Allocation';
import Organization from './pages/Organization';
import Departments from './pages/Departments';
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

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />

          <Route path="dashboard" element={
            <ProtectedRoute> <Dashboard /> </ProtectedRoute>
          } />

          <Route path="organization" element={
            <ProtectedRoute allowedRoles={['admin']}> <Organization /> </ProtectedRoute>
          } />

          <Route path="departments" element={
            <ProtectedRoute allowedRoles={['admin']}> <Departments /> </ProtectedRoute>
          } />

          <Route path="assets" element={
            <ProtectedRoute> <Assets /> </ProtectedRoute>
          } />

          <Route path="allocation" element={
            <ProtectedRoute> <Allocation /> </ProtectedRoute>
          } />

          <Route path="booking" element={
            <ProtectedRoute> <Booking /> </ProtectedRoute>
          } />

          <Route path="maintenance" element={
            <ProtectedRoute> <Maintenance /> </ProtectedRoute>
          } />

          <Route path="audit" element={
            <ProtectedRoute> <Audit /> </ProtectedRoute>
          } />

          <Route path="reports" element={
            <ProtectedRoute> <Reports /> </ProtectedRoute>
          } />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;