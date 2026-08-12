import axios from 'axios';
import { OpenAPI } from '../client';
import { toast } from 'sonner';

// Initialize OpenAPI defaults
OpenAPI.BASE = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';

// We configure HEADERS dynamically via a resolver to always get the latest state
OpenAPI.HEADERS = async () => {
  const headers: Record<string, string> = {};
  
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const tenantId = localStorage.getItem('tenant_id') || 'default_tenant';
    headers['X-Tenant-ID'] = tenantId;
  }
  
  return headers;
};

// Add global interceptors to the default axios instance used by the generated client
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      
      if (status === 401) {
        // Token expired or invalid
        toast.error("Session expired. Please log in again.");
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
           localStorage.removeItem('token');
           window.location.href = '/login';
        }
      } else if (status === 403) {
        // Forbidden / Policy Denied
        toast.error("Access Denied: You do not have permission for this action.");
      }
    } else {
      // Network error or server down
      toast.error("Network error. Please try again later.");
    }
    
    return Promise.reject(error);
  }
);

export * from '../client';
