// API service for communicating with the backend
import axios from 'axios';
import { getIdToken } from './firebase';

// Base API URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await getIdToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);

// API functions
export const videoAPI = {
  // Upload video file
  uploadVideo: async (formData) => {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Upload video from URL
  uploadVideoFromURL: async (videoUrl, captionStyle) => {
    const formData = new FormData();
    formData.append('video_url', videoUrl);
    formData.append('font_type', captionStyle.fontType);
    formData.append('font_size', captionStyle.fontSize.toString());
    formData.append('font_color', captionStyle.fontColor);
    formData.append('stroke_color', captionStyle.strokeColor);
    formData.append('stroke_width', captionStyle.strokeWidth.toString());
    formData.append('padding', captionStyle.padding.toString());
    formData.append('position', captionStyle.position);

    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Create captions for existing video
  createCaptions: async (videoId, captionStyle) => {
    const response = await api.post('/api/caption', {
      video_id: videoId,
      caption_style: captionStyle,
    });
    return response.data;
  },

  // Get all videos
  getVideos: async (page = 1, pageSize = 10, status = null) => {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    
    const response = await api.get('/api/videos', { params });
    return response.data;
  },

  // Get video details
  getVideo: async (videoId) => {
    const response = await api.get(`/api/video/${videoId}`);
    return response.data;
  },

  // Get video status
  getVideoStatus: async (videoId) => {
    const response = await api.get(`/api/video/${videoId}/status`);
    return response.data;
  },

  // Download video
  downloadVideo: async (videoId, type = 'processed') => {
    const response = await api.get(`/api/video/${videoId}/download`, {
      params: { type },
      responseType: 'blob',
    });
    return response.data;
  },

  // Delete video
  deleteVideo: async (videoId) => {
    const response = await api.delete(`/api/video/${videoId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;