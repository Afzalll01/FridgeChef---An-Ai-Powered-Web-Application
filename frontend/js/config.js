/**
 * FridgeChef Frontend Configuration
 * Easily configure local development vs production Render backend URLs.
 */

(function () {
  // Determine if running in local development
  const isLocalhost = Boolean(
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname.startsWith('192.168.') ||
    window.location.protocol === 'file:'
  );

  // Default Backend URL
  // In development: http://localhost:5000/api
  // In production: Configure with your Render backend URL e.g. 'https://fridgechef-backend.onrender.com/api'
  const DEFAULT_DEV_API = 'http://localhost:5000/api';
  const DEFAULT_PROD_API =
    "https://fridgechef-an-ai-powered-web-application.onrender.com/api";

  // Allow custom override via localStorage if needed
  const overrideApi = localStorage.getItem('FRIDGECHEF_API_URL');

  window.APP_CONFIG = {
    API_BASE_URL: overrideApi || (isLocalhost ? DEFAULT_DEV_API : DEFAULT_PROD_API),
    IS_LOCAL: isLocalhost,
  };
})();
