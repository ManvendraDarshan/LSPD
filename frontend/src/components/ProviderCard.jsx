import { Link } from "react-router-dom";
import { BadgeCheck, MapPin, Phone, Star } from "lucide-react";

export default function ProviderCard({ provider }) {
  const category = provider.categories?.[0]?.name || "Local Service";
  return (
    <article className="card p-4">
      <div className="flex gap-4">
        <img className="h-20 w-20 rounded-lg object-cover" src={provider.profile_image || `https://api.dicebear.com/8.x/initials/svg?seed=${encodeURIComponent(provider.business_name)}`} alt={provider.business_name} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="truncate text-lg font-bold">{provider.business_name}</h3>
            {provider.is_verified && <span className="badge"><BadgeCheck size={14} />Verified</span>}
          </div>
          <p className="text-sm font-medium text-brand">{category}</p>
          <p className="mt-1 line-clamp-2 text-sm text-slate-600">{provider.description}</p>
        </div>
      </div>
      <div className="mt-4 grid gap-2 text-sm text-slate-600 sm:grid-cols-3">
        <span className="flex items-center gap-1"><Star size={16} className="fill-saffron text-saffron" />{provider.average_rating || 0} ({provider.review_count})</span>
        <span className="flex items-center gap-1"><MapPin size={16} />{provider.city}, {provider.district}</span>
        <span>{provider.distance_km ? `${provider.distance_km} km away` : `${provider.experience} yrs exp.`}</span>
      </div>
      <div className="mt-4 flex gap-2">
        <a href={`tel:${provider.user?.phone}`} className="btn-secondary flex-1"><Phone size={16} />Contact</a>
        <Link to={`/providers/${provider.id}`} className="btn-primary flex-1">View profile</Link>
      </div>
    </article>
  );
}
