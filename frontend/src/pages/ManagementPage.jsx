import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { api, errorMessage } from "../services/api";

export default function ManagementPage({ type }) {
  const [rows, setRows] = useState([]);
  const [categories, setCategories] = useState([]);
  const title = { providers: "Provider Management", verification: "Provider Verification", customers: "Customer Management", categories: "Category Management", reviews: "Review Moderation" }[type];
  useEffect(() => {
    if (type === "customers") api.get("/admin/customers").then((r) => setRows(r.data));
    else if (type === "reviews") api.get("/admin/reviews").then((r) => setRows(r.data));
    else if (type === "categories") api.get("/categories", { params: { include_inactive: true } }).then((r) => setCategories(r.data));
    else api.get("/admin/providers", { params: type === "verification" ? { status: "pending" } : {} }).then((r) => setRows(r.data));
  }, [type]);
  async function providerAction(id, action) {
    try {
      const { data } = await api.put(`/admin/providers/${id}/${action}`);
      setRows(rows.map((row) => row.id === id ? data : row));
      toast.success("Provider updated");
    } catch (error) { toast.error(errorMessage(error)); }
  }
  async function reviewStatus(id, status) {
    const { data } = await api.put(`/admin/reviews/${id}`, { status });
    setRows(rows.map((row) => row.id === id ? data : row));
  }
  return (
    <div className="page-shell">
      <h1 className="text-3xl font-black">{title}</h1>
      {type === "categories" ? <div className="mt-5 grid gap-3 md:grid-cols-3">{categories.map((c) => <div className="card p-4" key={c.id}><h2 className="font-bold">{c.name}</h2><p className="text-sm text-slate-600">{c.provider_count} providers</p><span className="badge mt-3">{c.is_active ? "Active" : "Inactive"}</span></div>)}</div> : <div className="mt-5 overflow-x-auto card"><table className="w-full text-left text-sm"><tbody>{rows.map((row) => <tr className="border-t" key={row.id}>{type === "reviews" ? <><td className="p-3 font-semibold">{row.customer.name}</td><td>{row.rating} stars</td><td>{row.comment}</td><td><select value={row.status} onChange={(e) => reviewStatus(row.id, e.target.value)} className="rounded border p-2"><option value="published">Published</option><option value="hidden">Hidden</option><option value="reported">Reported</option></select></td></> : type === "customers" ? <><td className="p-3 font-semibold">{row.name}</td><td>{row.email}</td><td>{row.city}</td><td>{row.is_active ? "Active" : "Inactive"}</td></> : <><td className="p-3 font-semibold">{row.business_name}</td><td>{row.city}</td><td>{row.verification_status}</td><td>{row.is_verified ? "Verified" : "Not verified"}</td><td className="flex gap-2 p-3"><button className="btn-secondary" onClick={() => providerAction(row.id, "approve")}>Approve</button><button className="btn-secondary" onClick={() => providerAction(row.id, "reject")}>Reject</button><button className="btn-secondary" onClick={() => providerAction(row.id, "revoke-verification")}>Revoke</button></td></>}</tr>)}</tbody></table></div>}
    </div>
  );
}
