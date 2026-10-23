"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "motion/react";

/* ========================================================================
   BentoCard – Neo-Brutalist Autonomous Agent Orchestration Hub
   - 2px solid black borders
   - 8px 8px hard shadow for large container, 3-4px for items
   - Cabinet Grotesk headings + Satoshi body
   - #ffe17c yellow, #b7c6c2 sage, #171e19 charcoal, #000000 black
   - Tactile translate on hover
   ======================================================================== */

interface TabConfig {
  id: string;
  label: string;
  emoji: string;
  badge?: string;
  header: string;
  description: string;
}

const TABS: TabConfig[] = [
  {
    id: "agents",
    label: "Agent Swarm",
    emoji: "🧠",
    header: "Multi-Agent Swarm Orchestration",
    description:
      "Real-time consensus & health telemetry across 8 agricultural specialized agents.",
  },
  {
    id: "plantation",
    label: "Estate Blocks",
    emoji: "🌴",
    header: "Plantation Geo-Blocks",
    description:
      "Active canopy coverage, palm counts, and localized microclimate data.",
    badge: "8 Active",
  },
  {
    id: "actions",
    label: "Quick Actions",
    emoji: "⚡",
    header: "Agronomic Dispatch",
    description:
      "Immediate interventions, spray schedules, and sensor recalibration.",
    badge: "3 Due",
  },
  {
    id: "telemetry",
    label: "Data Logs",
    emoji: "📊",
    header: "Sensor & Market Telemetry",
    description:
      "Archived weather readings, APMC mandi rates, and Bayesian priors.",
  },
];

const fonts = {
  body: "'Satoshi', system-ui, -apple-system, sans-serif",
  heading: "'Cabinet Grotesk', -apple-system, sans-serif",
  mono: "'JetBrains Mono', monospace",
};

const BentoCard = () => {
  const [activeTab, setActiveTab] = useState(TABS[0]);

  const content = useMemo(() => {
    switch (activeTab.id) {
      case "agents":
        return <AgentSwarmDashboard />;
      case "plantation":
        return <PlantationDashboard />;
      case "actions":
        return <QuickActionsDashboard />;
      case "telemetry":
        return <TelemetryLogsDashboard />;
      default:
        return null;
    }
  }, [activeTab.id]);

  return (
    <div
      style={{
        width: "100%",
        borderRadius: "8px",
        border: "2px solid #000000",
        backgroundColor: "#ffffff",
        boxShadow: "8px 8px 0px 0px #000000",
        overflow: "hidden",
        fontFamily: fonts.body,
      }}
    >
      {/* ── Outer Header ─────────────────────────────────────────────── */}
      <div
        style={{
          padding: "20px 24px",
          borderBottom: "2px solid #000000",
          backgroundColor: "#ffe17c",
          backgroundImage: "radial-gradient(rgba(0, 0, 0, 0.10) 2px, transparent 2px)",
          backgroundSize: "32px 32px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "4px",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "10px",
                height: "10px",
                borderRadius: "50%",
                backgroundColor: "#000000",
              }}
            />
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 800,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
                color: "#000000",
                fontFamily: fonts.heading,
              }}
            >
              Autonomous Agent Orchestration Hub
            </span>
          </div>
          <h2
            style={{
              fontSize: "1.35rem",
              fontWeight: 800,
              color: "#000000",
              fontFamily: fonts.heading,
              letterSpacing: "-0.04em",
              lineHeight: 1.2,
              margin: 0,
            }}
          >
            Precision Ag-Intelligence & Real-Time Plantation Consensus
          </h2>
        </div>

        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            backgroundColor: "#171e19",
            color: "#ffffff",
            border: "2px solid #000000",
            padding: "0.35rem 0.75rem",
            borderRadius: "4px",
            boxShadow: "3px 3px 0px 0px #000000",
            fontFamily: fonts.heading,
            fontSize: "0.75rem",
            fontWeight: 800,
            letterSpacing: "0.04em",
            textTransform: "uppercase",
          }}
        >
          <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#ffe17c" }} />
          MAS Engine v0.2
        </div>
      </div>

      {/* ── Inner Chrome & Two-Column Workspace ─────────────────────── */}
      <div style={{ display: "flex", minHeight: "320px", flexWrap: "wrap" }}>
        {/* Tab Sidebar */}
        <div
          style={{
            width: "220px",
            borderRight: "2px solid #000000",
            backgroundColor: "#b7c6c2",
            padding: "16px 12px",
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            flexShrink: 0,
          }}
        >
          <div
            style={{
              fontSize: "0.7rem",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "#000000",
              padding: "0 6px 4px 6px",
              fontFamily: fonts.heading,
            }}
          >
            Orchestration Tabs
          </div>
          {TABS.map((tab) => {
            const isActive = activeTab.id === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "9px 12px",
                  borderRadius: "4px",
                  border: "2px solid #000000",
                  backgroundColor: isActive ? "#ffe17c" : "#ffffff",
                  cursor: "pointer",
                  textAlign: "left",
                  fontSize: "0.85rem",
                  fontWeight: 800,
                  color: "#000000",
                  fontFamily: fonts.heading,
                  letterSpacing: "-0.02em",
                  boxShadow: isActive ? "3px 3px 0px 0px #000000" : "2px 2px 0px 0px #000000",
                  transform: isActive ? "translate(1px, 1px)" : "none",
                  transition: "transform 0.12s, box-shadow 0.12s",
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = "#ffe17c";
                    e.currentTarget.style.transform = "translate(2px, 2px)";
                    e.currentTarget.style.boxShadow = "0px 0px 0px 0px #000000";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = "#ffffff";
                    e.currentTarget.style.transform = "none";
                    e.currentTarget.style.boxShadow = "2px 2px 0px 0px #000000";
                  }
                }}
              >
                <span style={{ fontSize: "1.05rem", flexShrink: 0 }}>{tab.emoji}</span>
                <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {tab.label}
                </span>
                {tab.badge && (
                  <span
                    style={{
                      fontSize: "0.62rem",
                      fontWeight: 800,
                      fontFamily: fonts.mono,
                      padding: "2px 6px",
                      borderRadius: "3px",
                      backgroundColor: "#171e19",
                      color: "#ffe17c",
                      border: "1px solid #000000",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Content Area */}
        <div
          style={{
            flex: 1,
            padding: "20px 24px",
            display: "flex",
            flexDirection: "column",
            gap: "16px",
            backgroundColor: "#ffffff",
            minWidth: "280px",
          }}
        >
          {/* Header */}
          <div style={{ borderBottom: "2px solid #000000", paddingBottom: "10px" }}>
            <h3
              style={{
                fontSize: "0.85rem",
                fontWeight: 800,
                letterSpacing: "0.04em",
                textTransform: "uppercase",
                color: "#000000",
                fontFamily: fonts.heading,
                margin: "0 0 4px 0",
              }}
            >
              {activeTab.header}
            </h3>
            <p
              style={{
                fontSize: "0.88rem",
                color: "#171e19",
                margin: 0,
                lineHeight: 1.4,
                fontWeight: 500,
              }}
            >
              {activeTab.description}
            </p>
          </div>

          <AnimatePresence mode="popLayout" initial={false}>
            <motion.div
              key={activeTab.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18 }}
              style={{ flex: 1 }}
            >
              {content}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default BentoCard;

/* ==========================================================================
   Sub-Views for Tabs in Neo-Brutalism
   ========================================================================== */

/* ---------- Agent Swarm Tab ---------- */
const AgentSwarmDashboard = () => (
  <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
    {/* Consensus Health Bar */}
    <div
      style={{
        padding: "16px",
        borderRadius: "6px",
        border: "2px solid #000000",
        backgroundColor: "#ffe17c",
        boxShadow: "4px 4px 0px 0px #000000",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span
          style={{
            fontSize: "0.78rem",
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: "0.04em",
            color: "#000000",
            fontFamily: fonts.heading,
          }}
        >
          Swarm Consensus Health
        </span>
        <span
          style={{
            fontSize: "0.82rem",
            fontWeight: 800,
            color: "#000000",
            fontFamily: fonts.mono,
            backgroundColor: "#ffffff",
            padding: "2px 8px",
            border: "2px solid #000000",
            borderRadius: "4px",
            boxShadow: "2px 2px 0px 0px #000000",
          }}
        >
          98.4% Synchronized
        </span>
      </div>
      <div
        style={{
          width: "100%",
          height: "14px",
          borderRadius: "4px",
          border: "2px solid #000000",
          backgroundColor: "#ffffff",
          overflow: "hidden",
        }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "98.4%" }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{
            height: "100%",
            backgroundColor: "#2ec4b6",
            borderRight: "2px solid #000000",
          }}
        />
      </div>
      <span
        style={{
          fontSize: "0.78rem",
          color: "#000000",
          fontWeight: 600,
          lineHeight: 1.4,
          fontFamily: fonts.body,
        }}
      >
        Disease AI (MobileNetV2) · Weather Risk (Open-Meteo) · Market Regression · Bayesian Priors
      </span>
    </div>

    {/* Stats grid */}
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
      <StatMiniCard label="Specialized Agents" value="8 of 8" bg="#ffffff" pulse />
      <StatMiniCard label="Inference Latency" value="< 140 ms" bg="#b7c6c2" />
    </div>
  </div>
);

/* ---------- Plantation Blocks Tab ---------- */
const PlantationDashboard = () => (
  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
    {[
      {
        name: "Block A – Mature Plantation",
        variety: "Mangala",
        trees: "450 Palms",
        status: "Optimal",
        bg: "#ffffff",
      },
      {
        name: "Block B – High-Density Riverfront",
        variety: "South Kanara",
        trees: "320 Palms",
        status: "Koliroga Monitored",
        bg: "#ffe17c",
      },
      {
        name: "Block C – Intercrop Plantation",
        variety: "Mohitnagar",
        trees: "180 Palms",
        status: "Healthy",
        bg: "#b7c6c2",
      },
    ].map((b, i) => (
      <div
        key={i}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 16px",
          borderRadius: "6px",
          border: "2px solid #000000",
          backgroundColor: b.bg,
          boxShadow: "3px 3px 0px 0px #000000",
          cursor: "default",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              backgroundColor: "#000000",
              flexShrink: 0,
            }}
          />
          <div>
            <div
              style={{
                fontSize: "0.85rem",
                fontWeight: 800,
                color: "#000000",
                fontFamily: fonts.heading,
              }}
            >
              {b.name}
            </div>
            <div
              style={{
                fontSize: "0.75rem",
                color: "#171e19",
                fontWeight: 500,
                marginTop: "1px",
              }}
            >
              {b.variety} · {b.trees}
            </div>
          </div>
        </div>
        <span
          style={{
            fontSize: "0.7rem",
            fontWeight: 800,
            fontFamily: fonts.mono,
            textTransform: "uppercase",
            padding: "4px 8px",
            borderRadius: "4px",
            border: "1px solid #000000",
            backgroundColor: "#ffffff",
            color: "#000000",
            boxShadow: "1px 1px 0px 0px #000000",
          }}
        >
          {b.status}
        </span>
      </div>
    ))}
  </div>
);

/* ---------- Quick Actions Tab ---------- */
const QuickActionsDashboard = () => (
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
    {[
      {
        title: "Run Leaf Pathology",
        desc: "Upload or capture palm photo",
        emoji: "🔬",
        bg: "#ffe17c",
      },
      {
        title: "Check Rain Risk",
        desc: "72h precipitation outlook",
        emoji: "🌧️",
        bg: "#ffffff",
      },
      {
        title: "Log Spray Activity",
        desc: "Record 1% Bordeaux spray",
        emoji: "✅",
        bg: "#b7c6c2",
      },
      {
        title: "Mandi Price Trend",
        desc: "Shivamogga & Sirsi APMC",
        emoji: "📈",
        bg: "#ffffff",
      },
    ].map((act, i) => (
      <div
        key={i}
        style={{
          padding: "14px 16px",
          borderRadius: "6px",
          border: "2px solid #000000",
          backgroundColor: act.bg,
          boxShadow: "4px 4px 0px 0px #000000",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          gap: "10px",
          cursor: "pointer",
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
        <div>
          <div
            style={{
              fontSize: "0.9rem",
              fontWeight: 800,
              color: "#000000",
              fontFamily: fonts.heading,
              marginBottom: "3px",
            }}
          >
            {act.title}
          </div>
          <div
            style={{
              fontSize: "0.75rem",
              color: "#171e19",
              lineHeight: 1.35,
              fontWeight: 500,
            }}
          >
            {act.desc}
          </div>
        </div>
        <span style={{ fontSize: "1.3rem", alignSelf: "flex-end" }}>{act.emoji}</span>
      </div>
    ))}
  </div>
);

/* ---------- Telemetry Logs Tab ---------- */
const TelemetryLogsDashboard = () => (
  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
    {[
      {
        log: "Open-Meteo Telemetry Sync",
        time: "2 min ago",
        status: "28.4°C / 78% RH",
      },
      {
        log: "Bayesian Prior Update",
        time: "14 min ago",
        status: "Koleroga Prior: 0.18",
      },
      {
        log: "APMC Daily Auction Rates",
        time: "1h ago",
        status: "₹480/kg Avg",
      },
      {
        log: "Coordinator Synthesis Matrix",
        time: "3h ago",
        status: "Score: 24.2 / 100",
      },
    ].map((item, i) => (
      <div
        key={i}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 14px",
          borderRadius: "4px",
          border: "2px solid #000000",
          backgroundColor: "#ffffff",
          boxShadow: "3px 3px 0px 0px #000000",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "0.82rem",
              fontWeight: 800,
              color: "#000000",
              fontFamily: fonts.heading,
            }}
          >
            {item.log}
          </div>
          <div
            style={{
              fontSize: "0.68rem",
              color: "#64748b",
              fontFamily: fonts.mono,
              marginTop: "2px",
              fontWeight: 600,
            }}
          >
            {item.time}
          </div>
        </div>
        <span
          style={{
            fontSize: "0.72rem",
            fontWeight: 800,
            fontFamily: fonts.mono,
            color: "#000000",
            backgroundColor: "#ffe17c",
            padding: "3px 8px",
            borderRadius: "4px",
            border: "1px solid #000000",
          }}
        >
          {item.status}
        </span>
      </div>
    ))}
  </div>
);

/* ---------- Stat card helper ---------- */
const StatMiniCard = ({
  label,
  value,
  bg = "#ffffff",
  pulse,
}: {
  label: string;
  value: string;
  bg?: string;
  pulse?: boolean;
}) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "12px 16px",
      borderRadius: "6px",
      border: "2px solid #000000",
      backgroundColor: bg,
      boxShadow: "3px 3px 0px 0px #000000",
    }}
  >
    <div>
      <div
        style={{
          fontSize: "0.92rem",
          fontWeight: 800,
          color: "#000000",
          fontFamily: fonts.mono,
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: "0.7rem",
          fontWeight: 800,
          textTransform: "uppercase",
          letterSpacing: "0.04em",
          color: "#171e19",
          marginTop: "2px",
          fontFamily: fonts.heading,
        }}
      >
        {label}
      </div>
    </div>
    {pulse && (
      <span
        style={{
          width: "10px",
          height: "10px",
          borderRadius: "50%",
          backgroundColor: "#2ec4b6",
          border: "2px solid #000000",
        }}
      />
    )}
  </div>
);
