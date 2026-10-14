import axios from 'axios';

// Base URLs from Vite environment variables with sensible defaults
export const SKILL_SERVICE_URL = import.meta.env.VITE_SKILL_API_URL || 'http://localhost:5001/api';
export const OPPORTUNITY_SERVICE_URL = import.meta.env.VITE_OPPORTUNITY_API_URL || 'http://localhost:5002/api';

// Create Axios instances with 45s timeout to handle Render free-tier cold starts
export const skillApi = axios.create({
  baseURL: SKILL_SERVICE_URL,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const opportunityApi = axios.create({
  baseURL: OPPORTUNITY_SERVICE_URL,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Toast & Cold Start notification listeners
let toastCallback = null;
let coldStartCallback = null;

export const registerToastHandler = (handler) => {
  toastCallback = handler;
};

export const registerColdStartHandler = (handler) => {
  coldStartCallback = handler;
};

let activeRequests = 0;
let coldStartTimer = null;
let isColdStarting = false;

const startRequestTracking = (serviceName) => {
  activeRequests += 1;
  if (!coldStartTimer && !isColdStarting) {
    // If request takes longer than 2.5s, signal waking-up state (typical of cold starts)
    coldStartTimer = setTimeout(() => {
      if (activeRequests > 0) {
        isColdStarting = true;
        if (coldStartCallback) {
          coldStartCallback({
            isWakingUp: true,
            service: serviceName,
            message: 'Waking up cloud microservices (Render free-tier cold start typically takes 30–45s)...',
          });
        }
      }
    }, 2500);
  }
};

const endRequestTracking = () => {
  activeRequests = Math.max(0, activeRequests - 1);
  if (activeRequests === 0) {
    if (coldStartTimer) {
      clearTimeout(coldStartTimer);
      coldStartTimer = null;
    }
    if (isColdStarting) {
      isColdStarting = false;
      if (coldStartCallback) {
        coldStartCallback({
          isWakingUp: false,
          justAwakened: true,
          message: 'Services are awake and operational!',
        });
      }
    }
  }
};

// Request interceptors
skillApi.interceptors.request.use((config) => {
  startRequestTracking('Skill Service');
  return config;
});

opportunityApi.interceptors.request.use((config) => {
  startRequestTracking('Opportunity Service');
  return config;
});

const notifyError = (message, title = 'API Error') => {
  if (toastCallback) {
    toastCallback({ type: 'error', title, message });
  } else {
    console.error(`[${title}]`, message);
  }
};

// Response interceptors for unified error handling
skillApi.interceptors.response.use(
  (response) => {
    endRequestTracking();
    return response.data;
  },
  (error) => {
    endRequestTracking();
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || 'Skill Service error';
    // Don't auto-toast for 404 on roadmap check or initial queries where caller handles it
    if (error.response?.status !== 404) {
      notifyError(errorMsg, 'Skill Service');
    }
    return Promise.reject(error);
  }
);

opportunityApi.interceptors.response.use(
  (response) => {
    endRequestTracking();
    return response.data;
  },
  (error) => {
    endRequestTracking();
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || 'Opportunity Service unavailable';
    console.warn('[Opportunity API Warning]', errorMsg);
    // Don't spam toasts when service is in degraded state
    return Promise.reject(error);
  }
);

// -------------------------------------------------------------
// Skill Service API Functions
// -------------------------------------------------------------

// Students
export const getStudents = (params) => skillApi.get('/students', { params });
export const getStudent = (id) => skillApi.get(`/students/${id}`);
export const createStudent = (data) => skillApi.post('/students', data);
export const updateStudent = (id, data) => skillApi.put(`/students/${id}`, data);
export const deleteStudent = (id) => skillApi.delete(`/students/${id}`);

// Student Skills
export const getStudentSkills = (studentId) => skillApi.get(`/students/${studentId}/skills`);
export const addStudentSkill = (studentId, skill) => skillApi.post(`/students/${studentId}/skills`, skill);
export const updateStudentSkill = (studentId, skillName, level) => skillApi.put(`/students/${studentId}/skills/${encodeURIComponent(skillName)}`, { level });
export const deleteStudentSkill = (studentId, skillName) => skillApi.delete(`/students/${studentId}/skills/${encodeURIComponent(skillName)}`);

// Careers
export const getCareers = () => skillApi.get('/careers');
export const getCareer = (id) => skillApi.get(`/careers/${id}`);
export const createCareer = (data) => skillApi.post('/careers', data);
export const updateCareer = (id, data) => skillApi.put(`/careers/${id}`, data);
export const deleteCareer = (id) => skillApi.delete(`/careers/${id}`);

// Career Goals & Gap Analysis
export const setCareerGoal = (studentId, careerId) => skillApi.post(`/students/${studentId}/career-goal`, { career_id: careerId });
export const getSkillGap = (studentId) => skillApi.get(`/students/${studentId}/skill-gap`);

// Learning Roadmap
export const getRoadmap = (studentId) => skillApi.get(`/students/${studentId}/roadmap`);
export const generateRoadmap = (studentId) => skillApi.post(`/students/${studentId}/roadmap`);
export const updateRoadmapStage = (studentId, order, status) => skillApi.put(`/students/${studentId}/roadmap/stages/${order}`, { status });

// Composite Dashboard & Recommendations (Inter-service calls handled backend-side with graceful fallback)
export const getDashboardData = (studentId) => skillApi.get(`/students/${studentId}/dashboard`);
export const getRecommendations = (studentId, params) => skillApi.get(`/students/${studentId}/recommendations`, { params });

// System Status
export const getSystemStatus = () => skillApi.get('/system/status');

// -------------------------------------------------------------
// Opportunity Service API Functions (Direct)
// -------------------------------------------------------------

export const getOpportunities = (params) => opportunityApi.get('/opportunities', { params });
export const getOpportunity = (id) => opportunityApi.get(`/opportunities/${id}`);
export const createOpportunity = (data) => opportunityApi.post('/opportunities', data);
export const updateOpportunity = (id, data) => opportunityApi.put(`/opportunities/${id}`, data);
export const deleteOpportunity = (id) => opportunityApi.delete(`/opportunities/${id}`);
export const getOpportunityStats = () => opportunityApi.get('/opportunities/stats');
export const matchOpportunities = (payload) => opportunityApi.post('/opportunities/match', payload);
