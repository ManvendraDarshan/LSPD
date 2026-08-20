import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { roleHome } from "../utils/constants";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "", city: "", district: "", role: "customer" });
  const { register } = useAuth();
  const navigate = useNavigate();
  async function submit(e) {
    e.preventDefault();
    const user = await register(form);
    navigate(roleHome[user.role]);
  }
  return (
    <div className="page-shell max-w-2xl">
      <div className="card p-6">
        <h1 className="text-2xl font-black">Customer Registration</h1>
        <form onSubmit={submit} className="mt-5 grid gap-4 sm:grid-cols-2">
          {["name", "email", "phone", "city", "district"].map((key) => <label key={key} className="field"><span>{key}</span><input required type={key === "email" ? "email" : "text"} value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></label>)}
          <label className="field"><span>Password</span><input required minLength="8" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="btn-primary sm:col-span-2">Create account</button>
        </form>
      </div>
    </div>
  );
}
