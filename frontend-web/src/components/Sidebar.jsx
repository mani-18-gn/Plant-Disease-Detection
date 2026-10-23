import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Camera,
  CloudSun,
  TrendingUp,
  Sparkles,
  ClipboardList,
  User,
  LogOut,
  Leaf,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const Sidebar = () => {
  const { logout, user } = useAuth();

  const navItems = [
    { to: "/", label: "Overview", icon: LayoutDashboard },
    { to: "/detect", label: "Disease Detection", icon: Camera },
    { to: "/weather", label: "Weather Risk", icon: CloudSun },
    { to: "/market", label: "APMC Market", icon: TrendingUp },
    { to: "/advisory", label: "AI Advisory", icon: Sparkles },
    { to: "/activities", label: "Activity Log", icon: ClipboardList },
    { to: "/profile", label: "Farmer Profile", icon: User },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: "1.5rem", borderBottom: "1px solid #1e293b", display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <div style={{ background: "linear-gradient(135deg, #10b981 0%, #059669 100%)", padding: "0.5rem", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Leaf size={22} color="#ffffff" />
        </div>
        <div>
          <h2 style={{ fontSize: "1.2rem", color: "#ffffff", letterSpacing: "-0.02em", margin: 0 }}>ArecaAgent</h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", display: "block" }}>Autonomous Farm MAS</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: "1.25rem 0.75rem", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.7rem 1rem",
                borderRadius: "8px",
                color: isActive ? "#ffffff" : "#94a3b8",
                backgroundColor: isActive ? "#10b981" : "transparent",
                fontWeight: isActive ? 600 : 500,
                fontSize: "0.925rem",
                textDecoration: "none",
                transition: "all 0.15s ease",
              })}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Footer & Logout */}
      <div style={{ padding: "1rem 1.25rem", borderTop: "1px solid #1e293b", backgroundColor: "#0b1120" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ minWidth: 0, flex: 1 }}>
            <p style={{ fontSize: "0.875rem", fontWeight: 600, color: "#ffffff", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {user?.full_name || user?.username || "Farmer"}
            </p>
            <p style={{ fontSize: "0.75rem", color: "#64748b" }}>Karnataka Region</p>
          </div>
          <button
            onClick={logout}
            title="Log out"
            style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer", padding: "0.4rem", borderRadius: "6px", display: "flex" }}
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  );
};
