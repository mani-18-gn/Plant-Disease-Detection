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
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
        <p style={{ fontSize: "1.1rem", fontWeight: 600, color: "#10b981" }}>Loading ArecaAgent System...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
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
      {showSetupModal && <FarmSetupModal />}
    </div>
  );
};
