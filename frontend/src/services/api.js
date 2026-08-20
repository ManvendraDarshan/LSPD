import axios from "axios";

const apiHost = typeof window !== "undefined" ? window.location.hostname : "localhost";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || `http://${apiHost}:8000/api`
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" && typeof window.localStorage?.getItem === "function"
    ? window.localStorage.getItem("lspd_token")
    : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export function errorMessage(error) {
  const message = error?.response?.data?.detail || error?.response?.data?.message;
  if (!error?.response) return "Cannot reach the API. Make sure the FastAPI server is running.";
  if (error.response.status >= 500 && /database|postgres|psycopg|password authentication/i.test(message || "")) {
    return "Database unavailable. Check PostgreSQL is running and DATABASE_URL credentials are correct.";
  }
  return message || "Request failed. Please try again.";
}
