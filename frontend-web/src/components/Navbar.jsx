import React, { useState, useEffect } from "react";
import { Bell, MapPin, Layers, ShieldCheck } from "lucide-react";
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
    const interval = setInterval(fetchNotifs, 15000);
    return () => clearInterval(interval);
  }, [profile?.id]);

  const unreadCount = notifications.filter((n) => n.status === "sent").length;

  return (
    <header className="topbar">
      {/* Farm & Crop Block Selectors */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.85rem", flexWrap: "wrap" }}>
        {farms.length > 0 && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              backgroundColor: "#ffffff",
              padding: "0.35rem 0.75rem",
              borderRadius: "4px",
              border: "2px solid #000000",
              boxShadow: "3px 3px 0px 0px #000000",
            }}
          >
            <MapPin size={17} color="#000000" strokeWidth={2.5} />
            <select
              style={{
                border: "none",
                background: "transparent",
                outline: "none",
                fontFamily: "var(--font-heading)",
                fontSize: "0.875rem",
                fontWeight: 800,
                color: "#000000",
                cursor: "pointer",
                padding: 0,
                boxShadow: "none",
                transform: "none",
              }}
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
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              backgroundColor: "#b7c6c2",
              padding: "0.35rem 0.85rem",
              borderRadius: "4px",
              border: "2px solid #000000",
              boxShadow: "3px 3px 0px 0px #000000",
            }}
          >
            <Layers size={17} color="#000000" strokeWidth={2.5} />
            <select
              style={{
                border: "none",
                background: "transparent",
                outline: "none",
                fontFamily: "var(--font-heading)",
                fontSize: "0.875rem",
                fontWeight: 800,
                color: "#000000",
                cursor: "pointer",
                padding: 0,
                boxShadow: "none",
                transform: "none",
              }}
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

      {/* Right Side: Agent Status & Notification Bell */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", position: "relative" }}>
        {/* System Online Status Badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            fontSize: "0.8rem",
            fontWeight: 800,
            fontFamily: "var(--font-heading)",
            color: "#000000",
            backgroundColor: "#ffe17c",
            border: "2px solid #000000",
            padding: "0.4rem 0.85rem",
            borderRadius: "4px",
            boxShadow: "3px 3px 0px 0px #000000",
            textTransform: "uppercase",
            letterSpacing: "0.02em",
          }}
        >
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              backgroundColor: "#000000",
              display: "inline-block",
            }}
          />
          <ShieldCheck size={16} color="#000000" strokeWidth={2.5} />
          <span>8 Agents Active</span>
        </div>

        {/* Notification Bell */}
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            style={{
              backgroundColor: "#ffffff",
              border: "2px solid #000000",
              borderRadius: "4px",
              width: "42px",
              height: "42px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              position: "relative",
              boxShadow: "4px 4px 0px 0px #000000",
              transition: "transform 0.12s, box-shadow 0.12s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translate(4px, 4px)";
              e.currentTarget.style.boxShadow = "0px 0px 0px 0px #000000";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "4px 4px 0px 0px #000000";
            }}
          >
            <Bell size={20} color="#000000" strokeWidth={2.2} />
            {unreadCount > 0 && (
              <span
                style={{
                  position: "absolute",
                  top: "-6px",
                  right: "-6px",
                  backgroundColor: "#ff5252",
                  color: "#ffffff",
                  fontSize: "0.7rem",
                  fontWeight: 900,
                  width: "20px",
                  height: "20px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "2px solid #000000",
                  fontFamily: "var(--font-heading)",
                }}
              >
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown: 8px 8px hard shadow */}
          {showNotifs && (
            <div
              style={{
                position: "absolute",
                right: 0,
                top: "52px",
                width: "360px",
                backgroundColor: "#ffffff",
                borderRadius: "6px",
                boxShadow: "8px 8px 0px 0px #000000",
                border: "2px solid #000000",
                zIndex: 50,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  padding: "0.85rem 1.15rem",
                  borderBottom: "2px solid #000000",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  backgroundColor: "#ffe17c",
                }}
              >
                <h4 style={{ fontSize: "0.95rem", fontWeight: 800, margin: 0, color: "#000000", fontFamily: "var(--font-heading)" }}>
                  Alerts & Notifications
                </h4>
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "#000000",
                    fontWeight: 800,
                    fontFamily: "var(--font-mono)",
                    backgroundColor: "#ffffff",
                    border: "1px solid #000000",
                    padding: "0.15rem 0.5rem",
                    borderRadius: "4px",
                  }}
                >
                  {notifications.length} total
                </span>
              </div>
              <div style={{ maxHeight: "320px", overflowY: "auto", padding: "0.75rem" }}>
                {notifications.length === 0 ? (
                  <p style={{ padding: "1.5rem", textAlign: "center", fontSize: "0.9rem", color: "#000000", fontWeight: 500 }}>
                    No alerts at this time
                  </p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      style={{
                        padding: "0.75rem 0.85rem",
                        borderRadius: "4px",
                        marginBottom: "0.55rem",
                        backgroundColor: n.channel === "sms" ? "#b7c6c2" : "#ffffff",
                        border: "2px solid #000000",
                        boxShadow: "3px 3px 0px 0px #000000",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "0.75rem",
                          color: "#000000",
                          marginBottom: "0.25rem",
                          fontFamily: "var(--font-heading)",
                        }}
                      >
                        <span style={{ fontWeight: 800, textTransform: "uppercase" }}>
                          {n.channel} alert
                        </span>
                        <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700 }}>
                          {n.sent_at
                            ? new Date(n.sent_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                            : "Queued"}
                        </span>
                      </div>
                      <p style={{ fontSize: "0.85rem", color: "#000000", margin: 0, lineHeight: 1.4, fontWeight: 500 }}>
                        {n.content}
                      </p>
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
