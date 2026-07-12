// 1. Define the base API logic first
const API_BASE = 'http://localhost:8000';

// 2. Define the main service object
export const apiService = {
  get: async (endpoint) => {
    const user = JSON.parse(localStorage.getItem('user'));
    const response = await fetch(`${API_BASE}/${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user?.token}`
      }
    });
    if (!response.ok) throw new Error(`Failed to fetch ${endpoint}`);
    return await response.json();
  }
};

// 3. Define your specific reports service AFTER apiService is defined
export const reportService = {
  getSummary: () => apiService.get('reports/summary'),
  
  exportCsv: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    window.open(`${API_BASE}/reports/export?token=${user?.token}`, '_blank');
  }
};