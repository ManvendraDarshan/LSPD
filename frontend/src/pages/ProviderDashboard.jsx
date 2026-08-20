import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BadgeCheck, FileCheck, MapPin, Star, UserCog } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function ProviderDashboard() {
  const { user } = useAuth();
  const [provider, setProvider] = useState(null);
  useEffect(() => { api.get("/providers/me/profile").then((res) => setProvider(res.data)).catch(() => {}); }, [user]);
  const completion = provider ? Math.round((["business_name", "description", "address", "latitude", "longitude", "working_hours"].filter((k) => provider[k]).length / 6) * 100) : 20;
  return (
    <div className="page-shell">
      <h1 className="text-3xl font-black">Provider Dashboard</h1>
      {!provider && <div className="mt-5 card p-6"><p className="text-slate-700">Complete your provider profile to appear in customer search.</p><Link className="btn-primary mt-4" to="/provider/register">Create provider profile</Link></div>}
      {provider && <>
        <div className="mt-5 grid gap-4 md:grid-cols-5">{[[`${completion}%`, "Profile completion", UserCog], [provider.verification_status, "Verification", FileCheck], [provider.is_verified ? "Active" : "Pending", "Verified badge", BadgeCheck], [provider.profile_views, "Profile views", MapPin], [provider.average_rating, `${provider.review_count} reviews`, Star]].map(([value, label, Icon]) => <div className="stat" key={label}><Icon className="text-brand" /><div className="mt-3 text-2xl font-black">{value}</div><p className="text-sm text-slate-600">{label}</p></div>)}</div>
        <section className="mt-5 card p-5"><h2 className="text-xl font-black">{provider.business_name}</h2><p className="mt-2 text-slate-600">{provider.description}</p><div className="mt-4 flex flex-wrap gap-2"><Link className="btn-primary" to="/provider/edit-profile">Edit profile</Link><Link className="btn-secondary" to="/provider/documents">Upload documents</Link><Link className="btn-secondary" to="/provider/reviews">View reviews</Link></div></section>
      </>}
    </div>
  );
}
