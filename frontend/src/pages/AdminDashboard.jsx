import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BadgeCheck, ClipboardCheck, Star, Tags, Users } from "lucide-react";
import { api } from "../services/api";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  useEffect(() => { api.get("/admin/dashboard").then((res) => setStats(res.data)); }, []);
  if (!stats) return <div className="page-shell"><div className="skeleton h-72" /></div>;
  const cards = [["Users", stats.total_users, Users], ["Providers", stats.total_providers, ClipboardCheck], ["Verified", stats.verified_providers, BadgeCheck], ["Pending", stats.pending_providers, ClipboardCheck], ["Reviews", stats.total_reviews, Star], ["Categories", stats.total_service_categories, Tags]];
  return (
    <div className="page-shell">
      <h1 className="text-3xl font-black">Super Admin Dashboard</h1>
      <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-6">{cards.map(([label, value, Icon]) => <div className="stat" key={label}><Icon className="text-brand" /><div className="mt-3 text-2xl font-black">{value}</div><p className="text-sm text-slate-600">{label}</p></div>)}</div>
      <div className="mt-6 grid gap-3 md:grid-cols-4">{[["Service Providers", "/admin/providers"], ["Pending Verification", "/admin/verification"], ["Categories", "/admin/categories"], ["Review Moderation", "/admin/reviews"]].map(([label, href]) => <Link className="card p-4 font-semibold hover:border-brand" to={href} key={href}>{label}</Link>)}</div>
      <section className="mt-6 card p-5"><h2 className="text-xl font-black">Recent Registrations</h2><div className="mt-3 overflow-x-auto"><table className="w-full text-left text-sm"><tbody>{stats.recent_registrations.map((u) => <tr className="border-t" key={u.id}><td className="py-3 font-semibold">{u.name}</td><td>{u.email}</td><td>{u.role}</td><td>{u.city}</td></tr>)}</tbody></table></div></section>
    </div>
  );
}
