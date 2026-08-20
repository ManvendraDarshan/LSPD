import { LocateFixed, Search } from "lucide-react";
import { useState } from "react";
import { radii } from "../utils/constants";

export default function SearchBox({ initial = {}, onSearch, compact = false }) {
  const [form, setForm] = useState({ q: "", city: "", radius_km: 10, ...initial });
  const [locating, setLocating] = useState(false);
  function submit(e) {
    e.preventDefault();
    onSearch(form);
  }
  function locate() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm((prev) => ({ ...prev, lat: pos.coords.latitude, lng: pos.coords.longitude }));
        setLocating(false);
      },
      () => setLocating(false)
    );
  }
  return (
    <form onSubmit={submit} className={`grid gap-3 rounded-lg bg-white p-3 shadow-soft ${compact ? "md:grid-cols-[1fr_1fr_120px_auto_auto]" : "md:grid-cols-[1.2fr_1fr_130px_auto_auto]"}`}>
      <label className="field"><span>What service?</span><input value={form.q} onChange={(e) => setForm({ ...form, q: e.target.value })} placeholder="Electrician, plumber, AC repair" /></label>
      <label className="field"><span>Where?</span><input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="Satna, Rewa, Bhopal" /></label>
      <label className="field"><span>Radius</span><select value={form.radius_km} onChange={(e) => setForm({ ...form, radius_km: Number(e.target.value) })}>{radii.map((r) => <option key={r} value={r}>{r} km</option>)}</select></label>
      <button type="button" onClick={locate} className="btn-secondary self-end" title="Use current location"><LocateFixed size={18} />{locating ? "Locating" : "Near me"}</button>
      <button className="btn-primary self-end"><Search size={18} />Search</button>
    </form>
  );
}
