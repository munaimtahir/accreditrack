import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          localStorage.setItem('access_token', response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

// Auth services
export const authService = {
  login: async (username: string, password: string) => {
    const response = await axios.post(`${API_BASE_URL}/auth/token/`, {
      username,
      password,
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

// Project services
export const projectService = {
  getAll: () => api.get('/projects/'),
  get: (id: number) => api.get(`/projects/${id}/`),
  create: (data: any) => api.post('/projects/', data),
  update: (id: number, data: any) => api.put(`/projects/${id}/`, data),
  delete: (id: number) => api.delete(`/projects/${id}/`),
};

// Indicator services
export const indicatorService = {
  getAll: (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : {};
    return api.get('/indicators/', { params });
  },
  get: (id: number) => api.get(`/indicators/${id}/`),
  create: (data: any) => api.post('/indicators/', data),
  update: (id: number, data: any) => api.put(`/indicators/${id}/`, data),
  delete: (id: number) => api.delete(`/indicators/${id}/`),
};

// Evidence services
export const evidenceService = {
  getAll: (indicatorId?: number) => {
    const params = indicatorId ? { indicator_id: indicatorId } : {};
    return api.get('/evidence/', { params });
  },
  get: (id: number) => api.get(`/evidence/${id}/`),
  create: (data: FormData) => api.post('/evidence/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id: number, data: FormData) => api.put(`/evidence/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id: number) => api.delete(`/evidence/${id}/`),
};

// AI services
export const aiService = {
  analyzeChecklist: (checklist: string) => 
    api.post('/analyze-checklist/', { checklist }),
  
  analyzeCategories: (indicators: string[]) => 
    api.post('/analyze-categorization/', { indicators }),
  
  askAssistant: (question: string) => 
    api.post('/ask-assistant/', { question }),
  
  generateSummary: (data: string) => 
    api.post('/report-summary/', { data }),
  
  convertDocument: (content: string, targetFormat: string) => 
    api.post('/convert-document/', { content, target_format: targetFormat }),
  
  getComplianceGuide: (standard: string) => 
    api.post('/compliance-guide/', { standard }),
  
  analyzeTasks: (tasks: string[]) => 
    api.post('/analyze-tasks/', { tasks }),
};
