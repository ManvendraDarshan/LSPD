import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link, useParams } from "react-router-dom";
import { BadgeCheck, Mail, MapPin, Phone, Share2, Star } from "lucide-react";
import ProviderMap from "../components/ProviderMap";
import { useAuth } from "../context/AuthContext";
import { api, errorMessage } from "../services/api";

export default function ProviderDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const [provider, setProvider] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [review, setReview] = useState({ rating: 5, comment: "" });
  useEffect(() => {
    api.get(`/providers/${id}`).then((res) => setProvider(res.data));
    api.get(`/providers/${id}/reviews`).then((res) => setReviews(res.data));
  }, [id]);
  async function submitReview(e) {
    e.preventDefault();
    try {
      const { data } = await api.post(`/providers/${id}/reviews`, review);
      setReviews([data, ...reviews]);
      toast.success("Review submitted");
    } catch (error) { toast.error(errorMessage(error)); }
  }
  if (!provider) return <div className="page-shell"><div className="skeleton h-80" /></div>;
  return (
    <div className="page-shell">
      <section className="card overflow-hidden">
        <div className="h-44 bg-[linear-gradient(135deg,#0f766e,#e87b28)]" />
        <div className="p-5">
          <div className="-mt-16 flex flex-col gap-4 sm:flex-row sm:items-end">
            <img className="h-28 w-28 rounded-lg border-4 border-white bg-white object-cover" src={provider.profile_image || `https://api.dicebear.com/8.x/initials/svg?seed=${provider.business_name}`} alt={provider.business_name} />
            <div className="flex-1"><div className="flex flex-wrap items-center gap-2"><h1 className="text-3xl font-black">{provider.business_name}</h1>{provider.is_verified && <span className="badge"><BadgeCheck size={14} />Verified</span>}</div><p className="text-brand">{provider.categories?.map((c) => c.name).join(", ")}</p></div>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-4">
            <div className="stat"><Star className="text-saffron" /><strong>{provider.average_rating}</strong><p className="text-sm text-slate-600">{provider.review_count} reviews</p></div>
            <div className="stat"><MapPin className="text-brand" /><strong>{provider.city}</strong><p className="text-sm text-slate-600">{provider.district}</p></div>
            <div className="stat"><Phone className="text-brand" /><strong>{provider.user.phone}</strong><p className="text-sm text-slate-600">Contact number</p></div>
            <div className="stat"><Mail className="text-brand" /><strong className="break-all">{provider.user.email}</strong><p className="text-sm text-slate-600">Email</p></div>
          </div>
          <div className="mt-5 flex flex-wrap gap-2"><a className="btn-primary" href={`tel:${provider.user.phone}`}>Call</a><a className="btn-secondary" href={`https://www.openstreetmap.org/?mlat=${provider.latitude}&mlon=${provider.longitude}`} target="_blank">View on Map</a><button className="btn-secondary" onClick={() => navigator.share?.({ title: provider.business_name, url: location.href })}><Share2 size={16} />Share Profile</button></div>
        </div>
      </section>
      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_420px]">
        <section className="card p-5"><h2 className="text-xl font-black">About</h2><p className="mt-3 text-slate-700">{provider.description}</p><dl className="mt-5 grid gap-3 sm:grid-cols-2"><div><dt className="font-semibold">Experience</dt><dd>{provider.experience} years</dd></div><div><dt className="font-semibold">Working hours</dt><dd>{provider.working_hours}</dd></div><div><dt className="font-semibold">Address</dt><dd>{provider.address}</dd></div><div><dt className="font-semibold">Verification</dt><dd>{provider.verification_status}</dd></div></dl></section>
        <ProviderMap providers={[provider]} height="360px" />
      </div>
      <section className="mt-5 card p-5"><h2 className="text-xl font-black">Reviews</h2>{user?.role === "customer" ? <form onSubmit={submitReview} className="mt-4 grid gap-3"><select className="rounded-lg border p-2" value={review.rating} onChange={(e) => setReview({ ...review, rating: Number(e.target.value) })}>{[5,4,3,2,1].map((r) => <option key={r} value={r}>{r} stars</option>)}</select><textarea required minLength="5" className="rounded-lg border p-3" rows="3" value={review.comment} onChange={(e) => setReview({ ...review, comment: e.target.value })} placeholder="Share your experience" /><button className="btn-primary w-fit">Submit review</button></form> : <p className="mt-2 text-sm text-slate-600"><Link className="text-brand" to="/login">Login as a customer</Link> to write a review.</p>}{reviews.map((r) => <div key={r.id} className="mt-4 border-t pt-4"><strong>{r.customer.name}</strong><div className="text-sm text-saffron">{r.rating} stars</div><p className="text-slate-700">{r.comment}</p></div>)}</section>
    </div>
  );
}
