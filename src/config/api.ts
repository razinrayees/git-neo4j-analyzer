// API configuration for different environments
const getApiUrl = () => {
  // In production, use the environment variable set by Render
  if (import.meta.env.PROD && import.meta.env.VITE_API_URL) {
    return `https://${import.meta.env.VITE_API_URL}`;
  }
  
  // In development, use localhost
  return 'http://localhost:5000';
};

export const API_BASE_URL = getApiUrl();