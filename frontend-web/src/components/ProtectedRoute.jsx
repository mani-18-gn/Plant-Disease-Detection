import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";
import { FarmSetupModal } from "./FarmSetupModal";
import { useFarm } from "../context/FarmContext";

export const ProtectedLayout = () => {
  const { isAuthenticated, loading } = useAuth();
  const { showSetupModal } = useFarm();

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", backgroundColor: "#ffe17c" }}>
        <p style={{ fontSize: "1.2rem", fontWeight: 800, color: "#000000", fontFamily: "var(--font-heading)" }}>
          Loading ArecaAgent System...
        </p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Navbar />
        <main className="page-body">
          <Outlet />
        </main>
      </div>
      {showSetupModal && isAuthenticated && <FarmSetupModal />}
    </div>
  );
};

export const RequireAuth = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};
