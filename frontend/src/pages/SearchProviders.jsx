import { SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import SearchBox from "../components/SearchBox";
import ProviderCard from "../components/ProviderCard";
import ProviderMap from "../components/ProviderMap";
import { api, errorMessage } from "../services/api";

export default function SearchProviders() {
  const [params, setParams] = useSearchParams();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sort, setSort] = useState(params.get("sort") || "recommended");
  const query = useMemo(() => Object.fromEntries(params.entries()), [params]);
  useEffect(() => {
    setLoading(true);
    setError("");
    api.get("/search/providers", { params: { ...query, sort } })
      .then((res) => setProviders(res.data.items))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [params, sort]);
  return (
    <div className="page-shell">
      <div className="mb-5"><h1 className="text-3xl font-black">Search Providers</h1><p className="mt-1 text-slate-600">Find reliable local professionals by category, city, rating and distance.</p></div>
      <SearchBox initial={query} onSearch={(data) => setParams(Object.fromEntries(Object.entries(data).filter(([, v]) => v)))} compact />
      <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-600"><SlidersHorizontal size={18} />{providers.length} results</div>
        <select className="rounded-lg border border-slate-200 px-3 py-2 text-sm" value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="recommended">Recommended</option><option value="verified">Verified first</option><option value="highest_rated">Highest rated</option><option value="nearest">Nearest</option><option value="most_reviewed">Most reviewed</option>
        </select>
      </div>
      {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
      <div className="mt-5 grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="grid gap-4">
          {loading ? Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton h-52" />) : providers.length ? providers.map((p) => <ProviderCard key={p.id} provider={p} />) : <div className="card p-8 text-center"><h2 className="font-bold">No providers found</h2><p className="mt-2 text-sm text-slate-600">Try a wider radius or nearby city.</p></div>}
        </div>
        <div className="lg:sticky lg:top-24 lg:self-start"><ProviderMap providers={providers} /></div>
      </div>
    </div>
  );
}
