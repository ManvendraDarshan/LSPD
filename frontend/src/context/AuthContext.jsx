import { createContext, useContext, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { api, errorMessage } from "../services/api";

const AuthContext = createContext(null);
const storage = {
  get(key) {
    try {
      return typeof window !== "undefined" && typeof window.localStorage?.getItem === "function" ? window.localStorage.getItem(key) : null;
    } catch {
      return null;
    }
  },
  set(key, value) {
    try { window.localStorage?.setItem?.(key, value); } catch {}
  },
  remove(key) {
    try { window.localStorage?.removeItem?.(key); } catch {}
  }
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(storage.get("lspd_token")));

  useEffect(() => {
    const token = storage.get("lspd_token");
    if (!token) return;
    api.get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => storage.remove("lspd_token"))
      .finally(() => setLoading(false));
  }, []);

  async function login(payload) {
    try {
      const { data } = await api.post("/auth/login", payload);
      storage.set("lspd_token", data.access_token);
      setUser(data.user);
      toast.success("Welcome back");
      return data.user;
    } catch (error) {
      toast.error(errorMessage(error));
      throw error;
    }
  }

  async function register(payload) {
    try {
      const { data } = await api.post("/auth/register", payload);
      storage.set("lspd_token", data.access_token);
      setUser(data.user);
      toast.success("Account created");
      return data.user;
    } catch (error) {
      toast.error(errorMessage(error));
      throw error;
    }
  }

  function logout() {
    storage.remove("lspd_token");
    setUser(null);
    toast.success("Logged out");
  }

  const value = useMemo(() => ({ user, loading, login, register, logout }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
