import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { BadgeCheck, Clock, Search, Star } from "lucide-react";
import SearchBox from "../components/SearchBox";
import ProviderCard from "../components/ProviderCard";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [providers, setProviders] = useState([]);
  useEffect(() => { api.get("/providers", { params: { page_size: 4 } }).then((res) => setProviders(res.data.items)); }, []);
  return (
    <div className="page-shell">
      <div className="mb-5 grid gap-4 md:grid-cols-[1fr_auto] md:items-center"><div><h1 className="text-3xl font-black">Welcome, {user?.name}</h1><p className="text-slate-600">Search trusted services around {user?.city}.</p></div><Link to="/customer/profile" className="btn-secondary">Profile</Link></div>
      <SearchBox onSearch={(params) => navigate(`/search?${new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()}`)} compact />
      <div className="mt-6 grid gap-4 md:grid-cols-4">{[["Verified nearby", BadgeCheck], ["Top rated", Star], ["Fast search", Search], ["Recent activity", Clock]].map(([label, Icon]) => <div className="stat" key={label}><Icon className="text-brand" /><div className="mt-3 font-bold">{label}</div><p className="text-sm text-slate-600">Quick access</p></div>)}</div>
      <h2 className="mb-4 mt-8 text-2xl font-black">Nearby Providers</h2>
      <div className="grid gap-4 md:grid-cols-2">{providers.map((p) => <ProviderCard key={p.id} provider={p} />)}</div>
    </div>
  );
}
