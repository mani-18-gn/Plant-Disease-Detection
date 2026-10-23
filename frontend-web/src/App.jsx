import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { FarmProvider } from "./context/FarmContext";
import { ProtectedLayout } from "./components/ProtectedRoute";

import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { DiseaseDetection } from "./pages/DiseaseDetection";
import { Weather } from "./pages/Weather";
import { Market } from "./pages/Market";
import { Advisory } from "./pages/Advisory";
import { ActivityLog } from "./pages/ActivityLog";
import { FarmerProfile } from "./pages/FarmerProfile";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <FarmProvider>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Application Routes */}
            <Route element={<ProtectedLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/detect" element={<DiseaseDetection />} />
              <Route path="/weather" element={<Weather />} />
              <Route path="/market" element={<Market />} />
              <Route path="/advisory" element={<Advisory />} />
              <Route path="/activities" element={<ActivityLog />} />
              <Route path="/profile" element={<FarmerProfile />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </FarmProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
