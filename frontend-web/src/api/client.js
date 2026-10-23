import axios from "axios";

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== "undefined" && window.location) {
    const { hostname, protocol } = window.location;
    if (hostname && hostname !== "localhost" && hostname !== "127.0.0.1") {
      return `${protocol}//${hostname}:8000`;
    }
  }
  return "http://127.0.0.1:8000";
};

const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Request Interceptor: Attach JWT Bearer Token safely
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("plantguard_token") || localStorage.getItem("areca_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // Safe masked logging for debugging (never log raw tokens)
      if (import.meta.env.DEV) {
        const masked = `${token.substring(0, 6)}...${token.substring(token.length - 4)}`;
        // config.headers['X-Auth-Debug'] = masked;
      }
    }
    if (config.data instanceof FormData) {
      delete config.headers["Content-Type"];
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Extract data & handle 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem("plantguard_token");
        localStorage.removeItem("areca_token");
        localStorage.removeItem("plantguard_user");
        localStorage.removeItem("areca_user");
        if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
          window.location.href = "/login";
        }
      }
      const message =
        error.response.data?.detail ||
        error.response.data?.message ||
        `Request failed with status ${error.response.status}`;
      return Promise.reject(new Error(message));
    } else if (error.code === "ECONNABORTED") {
      return Promise.reject(new Error("Request timed out (server took too long to respond)."));
    } else if (error.request) {
      return Promise.reject(
        new Error(`Unable to reach PlantGuard backend server at ${API_BASE_URL} (${error.message || "Connection refused"}).`)
      );
    }
    return Promise.reject(error);
  }
);

export default apiClient;
