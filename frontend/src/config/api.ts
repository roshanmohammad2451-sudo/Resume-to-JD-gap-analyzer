/**
 * Centralized API configuration for Resume-to-JD Gap Analyzer.
 * 
 * Supports:
 * 1. Explicit environment variable: VITE_API_BASE_URL (configured in Vercel or .env)
 * 2. Production build fallback: Deployed Render backend (https://resume-to-jd-gap-analyzer.onrender.com)
 * 3. Local development fallback: Empty string '' to utilize Vite dev server proxy
 */

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;

export const API_BASE_URL = (
  typeof rawBaseUrl === 'string' && rawBaseUrl.trim() !== ''
    ? rawBaseUrl.trim()
    : import.meta.env.PROD
      ? 'https://resume-to-jd-gap-analyzer.onrender.com'
      : ''
).replace(/\/+$/, '');

/**
 * Constructs the full URL for an API endpoint.
 * Ensures consistent handling of leading slashes.
 */
export const getApiUrl = (endpoint: string): string => {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE_URL}${cleanEndpoint}`;
};
