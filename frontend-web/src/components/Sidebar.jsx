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
      <div
        style={{
          padding: "1.4rem 1.25rem",
          borderBottom: "2px solid #000000",
          display: "flex",
          alignItems: "center",
          gap: "0.85rem",
          backgroundColor: "#171e19",
        }}
      >
        <div
          style={{
            backgroundColor: "#ffe17c",
            border: "2px solid #000000",
            padding: "0.5rem",
            borderRadius: "6px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "3px 3px 0px 0px #000000",
          }}
        >
          <Leaf size={22} color="#000000" strokeWidth={2.5} />
        </div>
        <div>
          <h2
            style={{
              fontSize: "1.3rem",
              color: "#ffffff",
              letterSpacing: "-0.04em",
              margin: 0,
              fontWeight: 800,
              fontFamily: "var(--font-heading)",
            }}
          >
            ArecaAgent
          </h2>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.35rem",
              backgroundColor: "#b7c6c2",
              color: "#000000",
              border: "1px solid #000000",
              borderRadius: "4px",
              padding: "0.1rem 0.45rem",
              fontSize: "0.7rem",
              letterSpacing: "0.02em",
              fontWeight: 800,
              textTransform: "uppercase",
              fontFamily: "var(--font-heading)",
              marginTop: "3px",
            }}
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: "#171e19",
                display: "inline-block",
              }}
            />
            Autonomous MAS
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav
        style={{
          flex: 1,
          padding: "1.25rem 0.85rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}
      >
        <span
          style={{
            fontSize: "0.72rem",
            color: "#b7c6c2",
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            padding: "0.2rem 0.5rem",
            fontFamily: "var(--font-heading)",
          }}
        >
          Core Intelligence
        </span>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "active" : "")}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "0.85rem",
                padding: "0.65rem 0.95rem",
                borderRadius: "6px",
                color: isActive ? "#000000" : "#ffffff",
                backgroundColor: isActive ? "#ffe17c" : "transparent",
                fontWeight: isActive ? 800 : 600,
                fontSize: "0.925rem",
                textDecoration: "none",
                border: isActive ? "2px solid #000000" : "2px solid transparent",
                boxShadow: isActive ? "3px 3px 0px 0px #000000" : "none",
                fontFamily: "var(--font-heading)",
                letterSpacing: "-0.02em",
                transition: "all 0.12s cubic-bezier(0.4, 0, 0.2, 1)",
              })}
            >
              {({ isActive }) => (
                <>
                  <Icon
                    size={19}
                    strokeWidth={2.2}
                    style={{
                      color: isActive ? "#000000" : "#b7c6c2",
                      flexShrink: 0,
                    }}
                  />
                  <span>{item.label}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User Footer & Logout */}
      <div
        style={{
          padding: "1.1rem 1.25rem",
          borderTop: "2px solid #000000",
          backgroundColor: "#171e19",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.5rem" }}>
          <div style={{ minWidth: 0, flex: 1 }}>
            <p
              style={{
                fontSize: "0.9rem",
                fontWeight: 800,
                color: "#ffffff",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                margin: 0,
                fontFamily: "var(--font-heading)",
                letterSpacing: "-0.02em",
              }}
            >
              {user?.full_name || user?.username || "Farmer"}
            </p>
            <p
              style={{
                fontSize: "0.75rem",
                color: "#ffe17c",
                margin: "2px 0 0 0",
                fontWeight: 600,
                fontFamily: "var(--font-body)",
              }}
            >
              Karnataka Region
            </p>
          </div>
          <button
            onClick={logout}
            title="Log out"
            style={{
              backgroundColor: "#ffffff",
              border: "2px solid #000000",
              color: "#000000",
              cursor: "pointer",
              padding: "0.45rem",
              borderRadius: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "2px 2px 0px 0px #000000",
              transition: "transform 0.12s, box-shadow 0.12s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#ff5252";
              e.currentTarget.style.color = "#ffffff";
              e.currentTarget.style.transform = "translate(2px, 2px)";
              e.currentTarget.style.boxShadow = "0px 0px 0px 0px #000000";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#ffffff";
              e.currentTarget.style.color = "#000000";
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "2px 2px 0px 0px #000000";
            }}
          >
            <LogOut size={16} strokeWidth={2.5} />
          </button>
        </div>
      </div>
    </aside>
  );
};
