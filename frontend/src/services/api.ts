import { OpenAPI } from '../client';

// Re-export the entire client so this becomes the single import path
export * from '../client';

// Configure base URL
OpenAPI.BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Enable cookies for refresh token
OpenAPI.WITH_CREDENTIALS = true;

// Inject dynamic headers
OpenAPI.HEADERS = async () => {
  const tenantId = typeof window !== 'undefined' ? localStorage.getItem('tenant_id') || 'default_tenant' : 'default_tenant';
  return {
    'X-Tenant-ID': tenantId,
  };
};

// Inject Bearer token
OpenAPI.TOKEN = async () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return token || '';
};

// Global Fetch Interceptor
if (typeof window !== 'undefined') {
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    let response = await originalFetch(...args);
    
    // 401 Silent Token Refresh
    if (response.status === 401 && !args[0]?.toString().includes('/auth/login')) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const refreshRes = await originalFetch(OpenAPI.BASE + '/api/v1/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
          });
          
          if (refreshRes.ok) {
            const data = await refreshRes.json();
            localStorage.setItem('token', data.access_token);
            
            // Replay original request
            if (args[1]) {
              const newHeaders = new Headers(args[1].headers);
              newHeaders.set('Authorization', `Bearer ${data.access_token}`);
              args[1].headers = newHeaders;
            }
            response = await originalFetch(...args);
          } else {
            // Refresh failed
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        } catch (e) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    
    // Global Error Toast handling
    if (!response.ok && response.status !== 401) {
      try {
        const cloned = response.clone();
        const errorData = await cloned.json();
        
        // Import toast dynamically to avoid circular dependencies
        import('sonner').then(({ toast }) => {
          const message = errorData.message || 'An unexpected error occurred';
          if (response.status >= 500) {
            toast.error(message, { description: errorData.code || `Error ${response.status}` });
          } else if (response.status === 403) {
            toast.error('Permission Denied', { description: message });
          } else {
            toast.warning(message, { description: errorData.code });
          }
        });
      } catch (e) {
        import('sonner').then(({ toast }) => {
          toast.error(`Request failed with status ${response.status}`);
        });
      }
    }
    
    return response;
  };
}
