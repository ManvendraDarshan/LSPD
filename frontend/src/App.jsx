import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import SearchProviders from "./pages/SearchProviders";
import ProviderDetails from "./pages/ProviderDetails";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProviderRegistration from "./pages/ProviderRegistration";
import Dashboard from "./pages/Dashboard";
import ProviderDashboard from "./pages/ProviderDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import ManagementPage from "./pages/ManagementPage";
import SimplePage from "./pages/SimplePage";
import NotFound from "./pages/NotFound";
import Unauthorized from "./pages/Unauthorized";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<SearchProviders />} />
          <Route path="/providers/:id" element={<ProviderDetails />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/provider/register" element={<ProviderRegistration />} />
          <Route path="/about" element={<SimplePage title="About LSPD" />} />
          <Route path="/contact" element={<SimplePage title="Contact" />} />
          <Route path="/unauthorized" element={<Unauthorized />} />
          <Route element={<ProtectedRoute roles={["customer"]} />}>
            <Route path="/customer/dashboard" element={<Dashboard />} />
            <Route path="/customer/profile" element={<SimplePage title="Customer Profile" />} />
            <Route path="/customer/reviews" element={<SimplePage title="My Reviews" />} />
          </Route>
          <Route element={<ProtectedRoute roles={["provider"]} />}>
            <Route path="/provider/dashboard" element={<ProviderDashboard />} />
            <Route path="/provider/edit-profile" element={<ProviderRegistration editMode />} />
            <Route path="/provider/services" element={<SimplePage title="Provider Services" />} />
            <Route path="/provider/documents" element={<SimplePage title="Verification Documents" />} />
            <Route path="/provider/reviews" element={<SimplePage title="Provider Reviews" />} />
          </Route>
          <Route element={<ProtectedRoute roles={["admin"]} />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/providers" element={<ManagementPage type="providers" />} />
            <Route path="/admin/verification" element={<ManagementPage type="verification" />} />
            <Route path="/admin/customers" element={<ManagementPage type="customers" />} />
            <Route path="/admin/categories" element={<ManagementPage type="categories" />} />
            <Route path="/admin/reviews" element={<ManagementPage type="reviews" />} />
          </Route>
          <Route path="/dashboard" element={<Navigate to="/customer/dashboard" replace />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
