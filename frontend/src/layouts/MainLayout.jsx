import { Link, NavLink, Outlet } from "react-router-dom";
import { Menu, Search, ShieldCheck, UserRound, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { roleHome } from "../utils/constants";

export default function MainLayout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const links = [
    ["Search", "/search"],
    ["Provider Signup", "/provider/register"],
    ["About", "/about"],
    ["Contact", "/contact"]
  ];
  return (
    <div className="min-h-screen bg-slate-50 text-ink">
      <header className="sticky top-0 z-40 border-b bg-white/95 backdrop-blur">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Link to="/" className="flex items-center gap-2 font-bold">
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-brand text-white"><ShieldCheck size={22} /></span>
            <span className="text-lg">LSPD</span>
          </Link>
          <div className="hidden items-center gap-6 md:flex">
            {links.map(([label, href]) => <NavLink key={href} to={href} className="text-sm font-medium hover:text-brand">{label}</NavLink>)}
          </div>
          <div className="hidden items-center gap-2 md:flex">
            {user ? (
              <>
                <Link to={roleHome[user.role]} className="btn-secondary"><UserRound size={16} />Dashboard</Link>
                <button onClick={logout} className="btn-primary">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-secondary">Login</Link>
                <Link to="/register" className="btn-primary">Create account</Link>
              </>
            )}
          </div>
          <button className="icon-btn md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu">{open ? <X /> : <Menu />}</button>
        </nav>
        {open && (
          <div className="border-t bg-white px-4 py-3 md:hidden">
            {[...links, ["Find providers", "/search"]].map(([label, href]) => <Link key={label} onClick={() => setOpen(false)} className="block py-2 font-medium" to={href}>{label}</Link>)}
            {user ? <button onClick={logout} className="mt-2 w-full btn-primary">Logout</button> : <Link onClick={() => setOpen(false)} className="mt-2 flex btn-primary" to="/login"><Search size={16} />Login</Link>}
          </div>
        )}
      </header>
      <main><Outlet /></main>
      <footer className="border-t bg-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-8 md:grid-cols-4">
          <div><div className="font-bold">LSPD</div><p className="mt-2 text-sm text-slate-600">Verified local service discovery for Madhya Pradesh, built to expand state by state.</p></div>
          <div><div className="font-semibold">Services</div><p className="mt-2 text-sm text-slate-600">Electricians, plumbers, carpenters, repair technicians and more.</p></div>
          <div><div className="font-semibold">Trust</div><p className="mt-2 text-sm text-slate-600">Ratings, moderated reviews and admin-managed verification.</p></div>
          <div><div className="font-semibold">Coverage</div><p className="mt-2 text-sm text-slate-600">Satna, Rewa, Bhopal, Indore, Jabalpur and Gwalior demo data.</p></div>
        </div>
      </footer>
    </div>
  );
}
