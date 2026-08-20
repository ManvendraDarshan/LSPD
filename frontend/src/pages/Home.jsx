import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, BadgeCheck, MapPin, ShieldCheck, Star, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";
import SearchBox from "../components/SearchBox";
import ProviderCard from "../components/ProviderCard";
import { api } from "../services/api";

const popular = ["Electrician", "Plumber", "Carpenter", "AC Repair", "Painter", "Appliance Repair", "Pest Control", "Tutor"];

export default function Home() {
  const navigate = useNavigate();
  const [providers, setProviders] = useState([]);
  useEffect(() => {
    api.get("/providers", { params: { page_size: 3, sort: "verified" } }).then((res) => setProviders(res.data.items)).catch(() => {});
  }, []);
  return (
    <>
      <section className="bg-[linear-gradient(135deg,#f8fafc_0%,#e8f4f8_58%,#fff7ed_100%)]">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 md:grid-cols-[1.15fr_0.85fr] md:items-center">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-sm font-semibold text-brand shadow-sm"><MapPin size={16} />Madhya Pradesh service discovery</div>
            <h1 className="max-w-3xl text-4xl font-black leading-tight md:text-6xl">Find Trusted Local Service Providers Near You</h1>
            <p className="mt-5 max-w-2xl text-lg text-slate-650">Discover verified electricians, plumbers, carpenters, technicians and other professionals in your city.</p>
            <div className="mt-6">
              <SearchBox onSearch={(params) => navigate(`/search?${new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()}`)} />
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link className="btn-primary" to="/search">Find a Service Provider <ArrowRight size={18} /></Link>
              <Link className="btn-secondary" to="/provider/register">Join as a Provider</Link>
            </div>
          </div>
          <div className="grid gap-4">
            <div className="card p-5">
              <div className="flex items-center gap-3"><ShieldCheck className="text-brand" /><div><p className="font-bold">Admin-verified providers</p><p className="text-sm text-slate-600">Verification documents stay private.</p></div></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="stat"><UsersRound className="text-saffron" /><div className="mt-3 text-3xl font-black">6+</div><p className="text-sm text-slate-600">Demo cities</p></div>
              <div className="stat"><Star className="text-saffron" /><div className="mt-3 text-3xl font-black">4.6</div><p className="text-sm text-slate-600">Seeded average</p></div>
            </div>
          </div>
        </div>
      </section>
      <section className="page-shell">
        <div className="mb-5 flex items-end justify-between"><h2 className="text-2xl font-black">Popular Categories</h2><Link to="/search" className="text-sm font-semibold text-brand">View all</Link></div>
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">{popular.map((item) => <Link to={`/search?q=${encodeURIComponent(item)}`} className="card p-4 font-semibold hover:border-brand" key={item}>{item}</Link>)}</div>
      </section>
      <section className="bg-white">
        <div className="page-shell grid gap-6 md:grid-cols-3">
          {["Search by need and city", "Compare ratings and distance", "Contact verified professionals"].map((item, idx) => <div className="card p-5" key={item}><div className="mb-3 grid h-9 w-9 place-items-center rounded-lg bg-skywash font-bold text-brand">{idx + 1}</div><h3 className="font-bold">{item}</h3><p className="mt-2 text-sm text-slate-600">Fast, location-aware discovery with transparent trust signals.</p></div>)}
        </div>
      </section>
      <section className="page-shell">
        <h2 className="mb-5 text-2xl font-black">Featured Providers</h2>
        <div className="grid gap-4 md:grid-cols-3">{providers.map((p) => <ProviderCard key={p.id} provider={p} />)}</div>
      </section>
      <section className="bg-ink text-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-10 md:grid-cols-[1fr_auto] md:items-center">
          <div><h2 className="text-2xl font-black">Build trust before the first call.</h2><p className="mt-2 text-slate-300">Verification workflows, review moderation and role-based dashboards are built in.</p></div>
          <Link className="btn-primary bg-saffron hover:bg-orange-700" to="/register">Get started</Link>
        </div>
      </section>
    </>
  );
}
