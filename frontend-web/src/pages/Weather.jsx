import React, { useState, useEffect } from "react";
import {
  CloudSun,
  Droplets,
  Thermometer,
  Wind,
  AlertTriangle,
  ShieldCheck,
  RefreshCw,
  Calendar,
  Clock,
  Sun,
  CloudRain,
  CloudLightning,
  Cloud,
  Compass,
} from "lucide-react";
import { weatherApi } from "../api/weather";
import { useFarm } from "../context/FarmContext";

export const Weather = () => {
  const { selectedFarm } = useFarm();
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchWeather = async (force = false) => {
    if (!selectedFarm?.id) return;
    setLoading(true);
    setError("");
    try {
      const data = await weatherApi.getCurrentWeather(selectedFarm.id, force);
      setWeatherData(data);
    } catch (err) {
      console.warn("Weather fetch failed:", err.message);
      setError(err.message || "Failed to load weather telemetry");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather(false);
  }, [selectedFarm?.id]);

  const riskScore =
    weatherData?.disease_risk?.score ??
    weatherData?.disease_risk?.disease_risk_score ??
    weatherData?.disease_risk_score ??
    20.0;
  const riskLevel =
    weatherData?.disease_risk?.level ??
    weatherData?.disease_risk_level ??
    "low";

  const getUrgencyBadgeClass = (lvl) => {
    switch (lvl?.toLowerCase()) {
      case "urgent":
        return "badge-urgent";
      case "high":
        return "badge-high";
      case "moderate":
      case "medium":
        return "badge-moderate";
      default:
        return "badge-low";
    }
  };

  const getWeatherIcon = (condition) => {
    switch (condition?.toLowerCase()) {
      case "sunny":
        return <Sun size={20} color="#eab308" />;
      case "rainy":
        return <CloudRain size={20} color="#0284c7" />;
      case "thunderstorm":
        return <CloudLightning size={20} color="#7c3aed" />;
      case "overcast":
      case "cloudy":
        return <Cloud size={20} color="#64748b" />;
      default:
        return <CloudSun size={20} color="#f59e0b" />;
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.85rem", margin: 0, fontWeight: 800 }}>Weather & Disease Risk Forecast</h1>
          <p style={{ fontSize: "0.925rem", color: "#64748b", margin: "0.3rem 0 0 0" }}>
            Live Open-Meteo meteorological telemetry & high-resolution forecast for{" "}
            <strong style={{ color: "#0a1a0f" }}>{selectedFarm?.farm_name || "Plantation"}</strong>
          </p>
        </div>
        <button className="btn btn-outline" onClick={() => fetchWeather(true)} disabled={loading}>
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Refreshing..." : "Force Live Update"}
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: "1rem 1.25rem",
            background: "#fff1f2",
            border: "1px solid #fecdd3",
            color: "#be123c",
            borderRadius: "12px",
            fontSize: "0.9rem",
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
          }}
        >
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Main 4 Metric Cards */}
      <div className="grid-4">
        {/* Temperature */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>Temperature</span>
            <div style={{ background: "#fff7ed", padding: "0.4rem", borderRadius: "8px" }}>
              <Thermometer size={18} color="#f97316" />
            </div>
          </div>
          <h2 style={{ fontSize: "1.85rem", margin: 0, color: "#0a1a0f", fontWeight: 800, letterSpacing: "-0.03em" }}>
            {weatherData?.temperature !== undefined ? `${Number(weatherData.temperature).toFixed(1)}°C` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.35rem", display: "block", fontFamily: "var(--font-mono)" }}>
            Source: {weatherData?.source || "Open-Meteo API"}
          </span>
        </div>

        {/* Humidity */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>Relative Humidity</span>
            <div style={{ background: "#f0f9ff", padding: "0.4rem", borderRadius: "8px" }}>
              <Droplets size={18} color="#0284c7" />
            </div>
          </div>
          <h2 style={{ fontSize: "1.85rem", margin: 0, color: "#0a1a0f", fontWeight: 800, letterSpacing: "-0.03em" }}>
            {weatherData?.humidity !== undefined ? `${Math.round(weatherData.humidity)}%` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.35rem", display: "block" }}>
            {weatherData?.humidity > 85 ? "High fungal incubation risk" : "Moderate moisture level"}
          </span>
        </div>

        {/* Rainfall */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>Precipitation (24h)</span>
            <div style={{ background: "#eff6ff", padding: "0.4rem", borderRadius: "8px" }}>
              <CloudRain size={18} color="#3b82f6" />
            </div>
          </div>
          <h2 style={{ fontSize: "1.85rem", margin: 0, color: "#0a1a0f", fontWeight: 800, letterSpacing: "-0.03em" }}>
            {weatherData?.rainfall_mm !== undefined ? `${Number(weatherData.rainfall_mm).toFixed(1)} mm` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.35rem", display: "block" }}>
            Western Ghats monsoon pattern
          </span>
        </div>

        {/* Wind Speed */}
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>Wind Velocity</span>
            <div style={{ background: "#f0fdf4", padding: "0.4rem", borderRadius: "8px" }}>
              <Wind size={18} color="#15803d" />
            </div>
          </div>
          <h2 style={{ fontSize: "1.85rem", margin: 0, color: "#0a1a0f", fontWeight: 800, letterSpacing: "-0.03em" }}>
            {weatherData?.wind_speed !== undefined ? `${Number(weatherData.wind_speed).toFixed(1)} km/h` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.35rem", display: "block" }}>
            Direction: {weatherData?.wind_direction || "SW"}
          </span>
        </div>
      </div>

      {/* Disease Risk Index & Spore Incubation Analysis */}
      <div className="grid-2">
        {/* Risk Analysis Card */}
        <div
          className="card"
          style={{
            background: "linear-gradient(135deg, #ffffff 0%, #fbfdfb 100%)",
            borderLeft: riskScore >= 60 ? "5px solid #e11d48" : "5px solid #15803d",
          }}
        >
          <div className="card-header">
            <div className="card-title">
              <ShieldCheck size={20} color={riskScore >= 60 ? "#e11d48" : "#15803d"} />
              <span>Arecanut Disease Risk Analysis</span>
            </div>
            <span className={`badge ${getUrgencyBadgeClass(riskLevel)}`}>
              <span className="badge-dot" />
              {riskLevel} Risk
            </span>
          </div>

          <p style={{ fontSize: "0.95rem", color: "#334155", marginBottom: "1.25rem", lineHeight: 1.55 }}>
            {weatherData?.disease_risk?.summary ||
              "Current microclimate shows normal physiological parameters. Continue standard surveillance for Mahali (Koleroga) fruit rot spores."}
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
                <span style={{ fontWeight: 600, color: "#0a1a0f" }}>Integrated Weather-Disease Vulnerability</span>
                <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: riskScore >= 60 ? "#e11d48" : "#15803d" }}>
                  {riskScore.toFixed(1)} / 100
                </span>
              </div>
              <div style={{ height: "8px", background: "#edf2f7", borderRadius: "999px", overflow: "hidden" }}>
                <div
                  style={{
                    width: `${Math.min(100, Math.max(0, riskScore))}%`,
                    height: "100%",
                    background: riskScore >= 60 ? "linear-gradient(90deg, #f97316, #e11d48)" : "linear-gradient(90deg, #22c55e, #15803d)",
                    borderRadius: "999px",
                    transition: "width 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
                  }}
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginTop: "0.5rem" }}>
              <div style={{ padding: "0.75rem 1rem", background: "#f8faf8", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
                <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block" }}>Koleroga Incubation Window</span>
                <strong style={{ fontSize: "0.95rem", color: "#0a1a0f" }}>
                  {weatherData?.humidity > 80 && weatherData?.rainfall_mm > 5 ? "Active (High)" : "Suppressed"}
                </strong>
              </div>
              <div style={{ padding: "0.75rem 1rem", background: "#f8faf8", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
                <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block" }}>Recommended Protective Action</span>
                <strong style={{ fontSize: "0.95rem", color: "#0a1a0f" }}>
                  {riskScore >= 50 ? "1% Bordeaux Mixture" : "Routine Observation"}
                </strong>
              </div>
            </div>
          </div>
        </div>

        {/* 7-Day Microclimate Outlook */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Calendar size={18} color="#15803d" />
              <span>7-Day Agro-Climate Outlook</span>
            </div>
            <span style={{ fontSize: "0.75rem", color: "#64748b", fontFamily: "var(--font-mono)" }}>
              Updated Hourly
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "280px", overflowY: "auto" }}>
            {(weatherData?.forecast || [
              { day: "Today", condition: "Sunny", high: 29, low: 22, rainProb: "10%" },
              { day: "Tomorrow", condition: "Cloudy", high: 28, low: 21, rainProb: "25%" },
              { day: "Day 3", condition: "Rainy", high: 26, low: 21, rainProb: "75%" },
              { day: "Day 4", condition: "Rainy", high: 25, low: 20, rainProb: "85%" },
              { day: "Day 5", condition: "Thunderstorm", high: 24, low: 20, rainProb: "90%" },
              { day: "Day 6", condition: "Cloudy", high: 27, low: 21, rainProb: "40%" },
              { day: "Day 7", condition: "Sunny", high: 29, low: 22, rainProb: "15%" },
            ]).map((f, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.55rem 0.85rem",
                  borderRadius: "8px",
                  background: i === 0 ? "#f0fdf4" : "#ffffff",
                  border: i === 0 ? "1px solid #bbf7d0" : "1px solid #f1f5f2",
                  transition: "background 0.15s ease",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", minWidth: "120px" }}>
                  {getWeatherIcon(f.condition)}
                  <span style={{ fontSize: "0.875rem", fontWeight: i === 0 ? 700 : 500, color: "#0a1a0f" }}>
                    {f.day || `Day +${i + 1}`}
                  </span>
                </div>
                <span style={{ fontSize: "0.825rem", color: "#64748b" }}>{f.condition}</span>
                <span style={{ fontSize: "0.85rem", fontFamily: "var(--font-mono)", fontWeight: 600, color: "#1e293b" }}>
                  {f.high}° / {f.low}°
                </span>
                <span
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    fontFamily: "var(--font-mono)",
                    color: parseInt(f.rainProb || "0") > 60 ? "#e11d48" : "#15803d",
                  }}
                >
                  {f.rainProb}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
