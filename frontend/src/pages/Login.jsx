import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { roleHome } from "../utils/constants";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  async function submit(e) {
    e.preventDefault();
    const user = await login(form);
    navigate(location.state?.from || roleHome[user.role] || "/");
  }
  return (
    <div className="page-shell max-w-xl">
      <div className="card p-6">
        <h1 className="text-2xl font-black">Login</h1>
        <form onSubmit={submit} className="mt-5 grid gap-4">
          <label className="field"><span>Email</span><input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label className="field"><span>Password</span><input required type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="btn-primary">Login</button>
        </form>
        <p className="mt-4 text-sm text-slate-600">Demo: customer@example.com, provider@example.com, admin@example.com. Password: DemoPass@123</p>
        <Link className="mt-4 inline-block text-sm font-semibold text-brand" to="/register">Create customer account</Link>
      </div>
    </div>
  );
}
