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

/**
 * Authentication service for handling user login, logout, and session status.
 */
export const authService = {
  /**
   * Logs in a user and stores the authentication tokens.
   * @param {string} username - The user's username.
   * @param {string} password - The user's password.
   * @returns {Promise<any>} The response data from the API.
   */
  login: async (username: string, password: string) => {
    const response = await axios.post(`${API_BASE_URL}/auth/token/`, {
      username,
      password,
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    return response.data;
  },
  
  /**
   * Logs out the user by removing authentication tokens.
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  
  /**
   * Checks if the user is authenticated.
   * @returns {boolean} True if an access token exists, false otherwise.
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

/**
 * Service for CRUD operations on projects.
 */
export const projectService = {
  /**
   * Retrieves all projects.
   * @returns {Promise<any>} A promise that resolves to the list of projects.
   */
  getAll: () => api.get('/projects/'),
  /**
   * Retrieves a single project by its ID.
   * @param {number} id - The ID of the project.
   * @returns {Promise<any>} A promise that resolves to the project data.
   */
  get: (id: number) => api.get(`/projects/${id}/`),
  /**
   * Creates a new project.
   * @param {any} data - The data for the new project.
   * @returns {Promise<any>} A promise that resolves to the created project data.
   */
  create: (data: any) => api.post('/projects/', data),
  /**
   * Updates an existing project.
   * @param {number} id - The ID of the project to update.
   * @param {any} data - The updated data for the project.
   * @returns {Promise<any>} A promise that resolves to the updated project data.
   */
  update: (id: number, data: any) => api.put(`/projects/${id}/`, data),
  /**
   * Deletes a project.
   * @param {number} id - The ID of the project to delete.
   * @returns {Promise<any>} A promise that resolves when the project is deleted.
   */
  delete: (id: number) => api.delete(`/projects/${id}/`),
};

/**
 * Service for CRUD operations on indicators.
 */
export const indicatorService = {
  /**
   * Retrieves all indicators, optionally filtered by project ID.
   * @param {number} [projectId] - The ID of the project to filter by.
   * @returns {Promise<any>} A promise that resolves to the list of indicators.
   */
  getAll: (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : {};
    return api.get('/indicators/', { params });
  },
  /**
   * Retrieves a single indicator by its ID.
   * @param {number} id - The ID of the indicator.
   * @returns {Promise<any>} A promise that resolves to the indicator data.
   */
  get: (id: number) => api.get(`/indicators/${id}/`),
  /**
   * Creates a new indicator.
   * @param {any} data - The data for the new indicator.
   * @returns {Promise<any>} A promise that resolves to the created indicator data.
   */
  create: (data: any) => api.post('/indicators/', data),
  /**
   * Updates an existing indicator.
   * @param {number} id - The ID of the indicator to update.
   * @param {any} data - The updated data for the indicator.
   * @returns {Promise<any>} A promise that resolves to the updated indicator data.
   */
  update: (id: number, data: any) => api.put(`/indicators/${id}/`, data),
  /**
   * Deletes an indicator.
   * @param {number} id - The ID of the indicator to delete.
   * @returns {Promise<any>} A promise that resolves when the indicator is deleted.
   */
  delete: (id: number) => api.delete(`/indicators/${id}/`),
};

/**
 * Service for CRUD operations on evidence.
 */
export const evidenceService = {
  /**
   * Retrieves all evidence, optionally filtered by indicator ID.
   * @param {number} [indicatorId] - The ID of the indicator to filter by.
   * @returns {Promise<any>} A promise that resolves to the list of evidence.
   */
  getAll: (indicatorId?: number) => {
    const params = indicatorId ? { indicator_id: indicatorId } : {};
    return api.get('/evidence/', { params });
  },
  /**
   * Retrieves a single piece of evidence by its ID.
   * @param {number} id - The ID of the evidence.
   * @returns {Promise<any>} A promise that resolves to the evidence data.
   */
  get: (id: number) => api.get(`/evidence/${id}/`),
  /**
   * Creates a new piece of evidence.
   * @param {FormData} data - The data for the new evidence, as FormData.
   * @returns {Promise<any>} A promise that resolves to the created evidence data.
   */
  create: (data: FormData) => api.post('/evidence/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  /**
   * Updates an existing piece of evidence.
   * @param {number} id - The ID of the evidence to update.
   * @param {FormData} data - The updated data for the evidence, as FormData.
   * @returns {Promise<any>} A promise that resolves to the updated evidence data.
   */
  update: (id: number, data: FormData) => api.put(`/evidence/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  /**
   * Deletes a piece of evidence.
   * @param {number} id - The ID of the evidence to delete.
   * @returns {Promise<any>} A promise that resolves when the evidence is deleted.
   */
  delete: (id: number) => api.delete(`/evidence/${id}/`),
};

/**
 * Service for interacting with the AI assistant endpoints.
 */
export const aiService = {
  /**
   * Sends a checklist to the AI for analysis.
   * @param {string} checklist - The checklist content to analyze.
   * @returns {Promise<any>} A promise that resolves to the AI's analysis.
   */
  analyzeChecklist: (checklist: string) => 
    api.post('/analyze-checklist/', { checklist }),
  
  /**
   * Sends a list of indicators to the AI for categorization.
   * @param {string[]} indicators - An array of indicators.
   * @returns {Promise<any>} A promise that resolves to the AI's categorization.
   */
  analyzeCategories: (indicators: string[]) => 
    api.post('/analyze-categorization/', { indicators }),
  
  /**
   * Asks the AI assistant a question.
   * @param {string} question - The question to ask.
   * @returns {Promise<any>} A promise that resolves to the AI's answer.
   */
  askAssistant: (question: string) => 
    api.post('/ask-assistant/', { question }),
  
  /**
   * Sends data to the AI to generate a summary report.
   * @param {string} data - The data to summarize.
   * @returns {Promise<any>} A promise that resolves to the AI-generated summary.
   */
  generateSummary: (data: string) => 
    api.post('/report-summary/', { data }),
  
  /**
   * Sends a document to the AI for conversion to another format.
   * @param {string} content - The content of the document.
   * @param {string} targetFormat - The desired output format.
   * @returns {Promise<any>} A promise that resolves to the converted document.
   */
  convertDocument: (content: string, targetFormat: string) => 
    api.post('/convert-document/', { content, target_format: targetFormat }),
  
  /**
   * Requests a compliance guide for a specific standard from the AI.
   * @param {string} standard - The name of the standard or regulation.
   * @returns {Promise<any>} A promise that resolves to the compliance guide.
   */
  getComplianceGuide: (standard: string) => 
    api.post('/compliance-guide/', { standard }),
  
  /**
   * Sends a list of tasks to the AI for analysis and optimization.
   * @param {string[]} tasks - An array of tasks.
   * @returns {Promise<any>} A promise that resolves to the AI's analysis.
   */
  analyzeTasks: (tasks: string[]) => 
    api.post('/analyze-tasks/', { tasks }),
};
