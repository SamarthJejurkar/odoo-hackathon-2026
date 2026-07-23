// Base URL (matches your current FastAPI routes)
const API_BASE = 'http://localhost:8000';

// Core request helper
async function request(endpoint, method = 'GET', body = undefined) {
  const user = JSON.parse(localStorage.getItem('user'));

  const response = await fetch(`${API_BASE}/${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(user?.token && {
        Authorization: `Bearer ${user.token}`,
      }),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const json = await response.json().catch(() => null);

  if (!response.ok) {
    const err = new Error(json?.message || json?.detail || `Failed request: ${method} ${endpoint}`);
    err.detail = json?.detail;
    err.errorCode = json?.error_code;
    throw err;
  }

  // Some routers wrap responses as {success, message, data}; others
  // return the resource directly. Unwrap only when that envelope shape
  // is present, so both styles work transparently.
  if (json && typeof json === 'object' && 'success' in json && 'data' in json) {
    return json.data;
  }
  return json;
}

// API methods
export const apiService = {
  get: (endpoint) => request(endpoint, 'GET'),
  post: (endpoint, body) => request(endpoint, 'POST', body),
  patch: (endpoint, body) => request(endpoint, 'PATCH', body),
  delete: (endpoint) => request(endpoint, 'DELETE'),
};

// Convenience methods
export const fetchAssets = () => apiService.get('assets');
export const fetchEmployees = () => apiService.get('users');
export const fetchDepartments = () => apiService.get('departments');
export const fetchCategories = () => apiService.get('categories');
export const fetchAllocations = () => apiService.get('allocations');
export const fetchTransfers = () => apiService.get('transfers');
export const fetchBookings = () => apiService.get('bookings');
export const fetchMaintenanceRequests = () =>
  apiService.get('maintenance-requests');
export const fetchAuditCycles = () => apiService.get('audit-cycles');

// Reports
export const reportService = {
  getSummary: () => apiService.get('reports/summary'),

  exportCsv: async () => {
    const user = JSON.parse(localStorage.getItem('user'));

    const response = await fetch(`${API_BASE}/reports/export`, {
      headers: {
        ...(user?.token && {
          Authorization: `Bearer ${user.token}`,
        }),
      },
    });

    if (!response.ok) {
      throw new Error('Export failed');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'report.csv';
    a.click();

    window.URL.revokeObjectURL(url);
  },
};