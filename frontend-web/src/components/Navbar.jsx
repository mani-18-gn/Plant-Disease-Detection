import React, { useState, useEffect } from "react";
import { Bell, MapPin, Layers, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useFarm } from "../context/FarmContext";
import { notifyingApi } from "../api/notifying";

export const Navbar = () => {
  const { profile } = useAuth();
  const { farms, cropBlocks, selectedFarm, selectedCropBlock, selectFarmById, selectCropBlockById } = useFarm();
  const [notifications, setNotifications] = useState([]);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    const fetchNotifs = async () => {
      if (profile?.id) {
        try {
          const list = await notifyingApi.listNotifications(profile.id);
          setNotifications(list);
        } catch (err) {
          console.warn("Could not fetch notifications:", err.message);
        }
      }
    };
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 15000); // 15s poll
    return () => clearInterval(interval);
  }, [profile?.id]);

  const unreadCount = notifications.filter((n) => n.status === "sent").length;

  return (
    <header className="topbar">
      {/* Farm & Crop Block Selectors */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
        {farms.length > 0 && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <MapPin size={16} color="#64748b" />
            <select
              className="form-select"
              style={{ padding: "0.35rem 0.6rem", fontSize: "0.85rem", width: "auto" }}
              value={selectedFarm?.id || ""}
              onChange={(e) => selectFarmById(e.target.value)}
            >
              {farms.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.farm_name} {profile?.district ? `(${profile.district})` : ""}
                </option>
              ))}
            </select>
          </div>
        )}

        {cropBlocks.length > 0 && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Layers size={16} color="#10b981" />
            <select
              className="form-select"
              style={{ padding: "0.35rem 0.6rem", fontSize: "0.85rem", width: "auto", fontWeight: 600, borderColor: "#10b981" }}
              value={selectedCropBlock?.id || ""}
              onChange={(e) => selectCropBlockById(e.target.value)}
            >
              {cropBlocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.block_name} ({b.variety || "Arecanut"})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Right Side: Notification Bell & Status */}
      <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", position: "relative" }}>
        {/* System Online Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.8rem", color: "#047857", background: "#d1fae5", padding: "0.25rem 0.6rem", borderRadius: "999px" }}>
          <ShieldCheck size={14} />
          <span>8 Agents Active</span>
        </div>

        {/* Notification Bell */}
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            style={{
              background: "#f1f5f9",
              border: "1px solid #e2e8f0",
              borderRadius: "50%",
              width: "38px",
              height: "38px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              position: "relative",
            }}
          >
            <Bell size={18} color="#334155" />
            {unreadCount > 0 && (
              <span
                style={{
                  position: "absolute",
                  top: "-2px",
                  right: "-2px",
                  background: "#ef4444",
                  color: "#ffffff",
                  fontSize: "0.65rem",
                  fontWeight: 700,
                  width: "18px",
                  height: "18px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifs && (
            <div
              style={{
                position: "absolute",
                right: 0,
                top: "45px",
                width: "340px",
                backgroundColor: "#ffffff",
                borderRadius: "12px",
                boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
                border: "1px solid #e2e8f0",
                zIndex: 50,
                overflow: "hidden",
              }}
            >
              <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #f1f5f9", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h4 style={{ fontSize: "0.9rem", margin: 0 }}>Alerts & Notifications</h4>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>{notifications.length} total</span>
              </div>
              <div style={{ maxHeight: "300px", overflowY: "auto", padding: "0.5rem" }}>
                {notifications.length === 0 ? (
                  <p style={{ padding: "1rem", textAlign: "center", fontSize: "0.85rem", color: "#94a3b8" }}>
                    No alerts at this time
                  </p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      style={{
                        padding: "0.65rem 0.75rem",
                        borderRadius: "8px",
                        marginBottom: "0.35rem",
                        backgroundColor: n.channel === "sms" ? "#f8fafc" : "#f0fdf4",
                        borderLeft: n.channel === "sms" ? "3px solid #64748b" : "3px solid #10b981",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#64748b", marginBottom: "0.2rem" }}>
                        <span style={{ fontWeight: 600, textTransform: "uppercase" }}>{n.channel} alert</span>
                        <span>{n.sent_at ? new Date(n.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Queued"}</span>
                      </div>
                      <p style={{ fontSize: "0.825rem", color: "#1e293b", margin: 0 }}>{n.content}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
