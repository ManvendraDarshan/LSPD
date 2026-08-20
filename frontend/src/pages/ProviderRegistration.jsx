import { useState } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api, errorMessage } from "../services/api";

export default function ProviderRegistration() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [account, setAccount] = useState({ name: "", email: "", phone: "", password: "", city: "", district: "", role: "provider" });
  const [profile, setProfile] = useState({ business_name: "", description: "", experience: 1, address: "", city: "", district: "", state: "Madhya Pradesh", pincode: "", latitude: 23.2599, longitude: 77.4126, working_hours: "Mon-Sat, 9:00 AM - 7:00 PM", category_name: "" });
  async function submit(e) {
    e.preventDefault();
    try {
      if (!profile.category_name.trim()) {
        toast.error("Please enter a service category");
        return;
      }
      if (!user) await register(account);
      await api.post("/providers", { ...profile, category_name: profile.category_name.trim() });
      toast.success("Provider profile submitted for verification");
      navigate("/provider/dashboard");
    } catch (error) {
      toast.error(errorMessage(error));
    }
  }
  return (
    <div className="page-shell">
      <div className="mb-5"><h1 className="text-3xl font-black">Join as a Service Provider</h1><p className="mt-1 text-slate-600">Create your account, add services, and submit your profile for verification.</p></div>
      <form onSubmit={submit} className="grid gap-5 lg:grid-cols-2">
        {!user && <section className="card p-5"><h2 className="font-bold">Account</h2><div className="mt-4 grid gap-3 sm:grid-cols-2">{["name", "email", "phone", "password", "city", "district"].map((key) => <label className="field" key={key}><span>{key}</span><input required type={key === "password" ? "password" : key === "email" ? "email" : "text"} value={account[key]} onChange={(e) => setAccount({ ...account, [key]: e.target.value })} /></label>)}</div></section>}
        <section className="card p-5 lg:col-span-2"><h2 className="font-bold">Business Profile</h2><div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <label className="field"><span>Business name</span><input required value={profile.business_name} onChange={(e) => setProfile({ ...profile, business_name: e.target.value })} /></label>
          <label className="field"><span>Category</span><input required placeholder="e.g. Plumber" value={profile.category_name} onChange={(e) => setProfile({ ...profile, category_name: e.target.value })} /></label>
          <label className="field"><span>Experience</span><input required type="number" min="0" value={profile.experience} onChange={(e) => setProfile({ ...profile, experience: Number(e.target.value) })} /></label>
          <label className="field sm:col-span-2"><span>Address</span><input required value={profile.address} onChange={(e) => setProfile({ ...profile, address: e.target.value })} /></label>
          {["city", "district", "pincode", "latitude", "longitude", "working_hours"].map((key) => <label className="field" key={key}><span>{key}</span><input required type={["latitude", "longitude"].includes(key) ? "number" : "text"} step="0.0001" value={profile[key]} onChange={(e) => setProfile({ ...profile, [key]: ["latitude", "longitude"].includes(key) ? Number(e.target.value) : e.target.value })} /></label>)}
          <label className="field sm:col-span-2 lg:col-span-3"><span>Description</span><textarea required rows="4" value={profile.description} onChange={(e) => setProfile({ ...profile, description: e.target.value })} /></label>
        </div><button className="btn-primary mt-5" disabled={!profile.category_name.trim()}>Submit provider profile</button></section>
      </form>
    </div>
  );
}
