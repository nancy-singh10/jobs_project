import axios from 'axios';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Response interceptor to handle errors gracefully
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorData = error.response?.data?.error || {
      message: error.message || 'Network error occurred',
      code: 'NETWORK_ERROR',
      details: {},
    };
    return Promise.reject(errorData);
  }
);

// FlowOps API client methods
export const api = {
  // Metrics
  getMetrics: async (projectId) => {
    const params = projectId ? { project_id: projectId } : {};
    const res = await apiClient.get('/jobs/metrics/', { params });
    return res.data.data;
  },

  // Jobs
  getJobs: async (params = {}) => {
    const res = await apiClient.get('/jobs/', { params });
    return res.data.data;
  },

  getJobById: async (jobId) => {
    const res = await apiClient.get(`/jobs/${jobId}/`);
    return res.data.data;
  },

  getJobExecutions: async (jobId) => {
    const res = await apiClient.get(`/jobs/${jobId}/executions/`);
    return res.data.data;
  },

  submitJob: async (jobData) => {
    const res = await apiClient.post('/jobs/', jobData);
    return res.data;
  },

  // Phase 2: Telemetry & Stats
  getDashboardStats: async (projectId) => {
    const params = projectId ? { project_id: projectId } : {};
    const res = await apiClient.get('/dashboard/stats/', { params });
    return res.data.data;
  },

  getWorkers: async () => {
    const res = await apiClient.get('/workers/');
    return res.data.data;
  },

  getHealth: async () => {
    const res = await apiClient.get('/health/');
    return res.data.data;
  },

  // Projects
  getProjects: async () => {
    const res = await apiClient.get('/projects/');
    return res.data.data;
  },

  getProjectById: async (projectId) => {
    const res = await apiClient.get(`/projects/${projectId}/`);
    return res.data.data;
  },

  createProject: async (projectData) => {
    const res = await apiClient.post('/projects/', projectData);
    return res.data.data;
  },

  updateProject: async (projectId, projectData) => {
    const res = await apiClient.patch(`/projects/${projectId}/`, projectData);
    return res.data.data;
  },
};
