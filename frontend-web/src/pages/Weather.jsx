import React, { useState, useEffect } from "react";
import { CloudSun, Droplets, Thermometer, Wind, AlertTriangle, ShieldCheck, RefreshCw, Calendar, Clock, Sun, CloudRain, CloudLightning, Cloud } from "lucide-react";
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

  const riskScore = weatherData?.disease_risk?.score ?? weatherData?.disease_risk?.disease_risk_score ?? weatherData?.disease_risk_score ?? 20.0;
  const riskLevel = weatherData?.disease_risk?.level ?? weatherData?.disease_risk_level ?? "low";

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
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", margin: 0 }}>Weather & Disease Risk Forecast</h1>
          <p style={{ fontSize: "0.9rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
            Live Open-Meteo meteorological telemetry & high-resolution forecast for <strong>{selectedFarm?.farm_name || "Plantation"}</strong>
          </p>
        </div>
        <button className="btn btn-outline" onClick={() => fetchWeather(true)} disabled={loading}>
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Refreshing..." : "Force Live Update"}
        </button>
      </div>

      {error && (
        <div style={{ padding: "0.75rem 1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "8px", fontSize: "0.85rem", marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      {/* Main 4 Metric Cards */}
      <div className="grid-4" style={{ marginBottom: "1.5rem" }}>
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Temperature</span>
            <Thermometer size={18} color="#f97316" />
          </div>
          <h2 style={{ fontSize: "1.75rem", margin: 0, color: "#0f172a" }}>
            {weatherData?.temperature !== undefined ? `${Number(weatherData.temperature).toFixed(1)}°C` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.25rem", display: "block" }}>
            Source: {weatherData?.source || "Open-Meteo API"}
          </span>
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Relative Humidity</span>
            <Droplets size={18} color="#0284c7" />
          </div>
          <h2 style={{ fontSize: "1.75rem", margin: 0, color: "#0f172a" }}>
            {weatherData?.humidity !== undefined ? `${Number(weatherData.humidity).toFixed(0)}%` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.25rem", display: "block" }}>
            Optimal: 60-80%
          </span>
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Rainfall (Live)</span>
            <CloudSun size={18} color="#3b82f6" />
          </div>
          <h2 style={{ fontSize: "1.75rem", margin: 0, color: "#0f172a" }}>
            {weatherData?.rainfall_mm !== undefined ? `${Number(weatherData.rainfall_mm).toFixed(1)} mm` : "--"}
          </h2>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.25rem", display: "block" }}>
            Current precipitation
          </span>
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Fungal Risk Index</span>
            <AlertTriangle size={18} color="#eab308" />
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h2 style={{ fontSize: "1.75rem", margin: 0, color: "#0f172a" }}>
              {Number(riskScore).toFixed(1)}/100
            </h2>
            <span className={`badge ${getUrgencyBadgeClass(riskLevel)}`}>
              {String(riskLevel).toUpperCase()}
            </span>
          </div>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "0.25rem", display: "block" }}>
            Fungal sporulation potential
          </span>
        </div>
      </div>

      {/* 24-Hour Hourly Forecast Strip */}
      {weatherData?.hourly_forecast && weatherData.hourly_forecast.length > 0 && (
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <div className="card-header" style={{ marginBottom: "0.75rem" }}>
            <div className="card-title">
              <Clock size={18} color="#0284c7" />
              <span>24-Hour Hourly Meteorological Forecast</span>
            </div>
            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Scroll horizontally to view next 24 hours</span>
          </div>
          <div
            style={{
              display: "flex",
              gap: "0.75rem",
              overflowX: "auto",
              paddingBottom: "0.75rem",
              scrollbarWidth: "thin",
            }}
          >
            {weatherData.hourly_forecast.map((h, idx) => (
              <div
                key={idx}
                style={{
                  minWidth: "90px",
                  padding: "0.75rem 0.5rem",
                  borderRadius: "10px",
                  backgroundColor: idx === 0 ? "#eff6ff" : "#f8fafc",
                  border: idx === 0 ? "1px solid #bfdbfe" : "1px solid #e2e8f0",
                  textAlign: "center",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "0.25rem",
                }}
              >
                <span style={{ fontSize: "0.8rem", color: "#475569", fontWeight: 600 }}>{h.time}</span>
                <span style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a" }}>{Number(h.temperature).toFixed(0)}°C</span>
                <div style={{ display: "flex", alignItems: "center", gap: "0.2rem", fontSize: "0.75rem", color: "#0284c7" }}>
                  <Droplets size={12} />
                  <span>{Number(h.humidity).toFixed(0)}%</span>
                </div>
                {h.precipitation_probability > 0 && (
                  <span style={{ fontSize: "0.7rem", color: "#2563eb", background: "#dbeafe", padding: "0.1rem 0.3rem", borderRadius: "4px", marginTop: "0.2rem" }}>
                    {Number(h.precipitation_probability).toFixed(0)}% rain
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7-Day Extended Weekly Forecast */}
      {weatherData?.weekly_forecast && weatherData.weekly_forecast.length > 0 && (
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <div className="card-header" style={{ marginBottom: "1rem" }}>
            <div className="card-title">
              <Calendar size={18} color="#16a34a" />
              <span>7-Day Extended Weather & Fungal Risk Outlook</span>
            </div>
            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Daily High/Low, Precipitation Probability, and Disease Pressure</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
            {weatherData.weekly_forecast.map((d, i) => (
              <div
                key={i}
                style={{
                  padding: "1rem",
                  borderRadius: "12px",
                  backgroundColor: i === 0 ? "#f0fdf4" : "#f8fafc",
                  border: i === 0 ? "1.5px solid #86efac" : "1px solid #e2e8f0",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.5rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <span style={{ fontSize: "0.95rem", fontWeight: 700, color: "#0f172a" }}>{d.day_name}</span>
                    <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block" }}>{d.date}</span>
                  </div>
                  {getWeatherIcon(d.weather_condition)}
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", margin: "0.25rem 0" }}>
                  <span style={{ fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>{Number(d.temp_max).toFixed(0)}°</span>
                  <span style={{ fontSize: "0.9rem", color: "#64748b" }}>/ {Number(d.temp_min).toFixed(0)}°C</span>
                  <span style={{ fontSize: "0.8rem", color: "#475569" }}>{d.weather_condition}</span>
                </div>

                <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem" }}>
                    <span style={{ color: "#64748b" }}>Rain Chance:</span>
                    <span style={{ fontWeight: 600, color: d.precipitation_probability_max > 50 ? "#2563eb" : "#475569" }}>
                      {Number(d.precipitation_probability_max).toFixed(0)}% ({Number(d.precipitation_sum_mm).toFixed(1)} mm)
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem" }}>
                    <span style={{ color: "#64748b" }}>Disease Risk:</span>
                    <span className={`badge ${getUrgencyBadgeClass(d.disease_risk_level)}`} style={{ fontSize: "0.7rem", padding: "0.15rem 0.4rem" }}>
                      {Number(d.disease_risk_score).toFixed(0)}/100 {d.disease_risk_level.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Spraying Timing & Protection Advisory Box */}
      <div
        className="card"
        style={{
          borderLeft: "4px solid #0284c7",
          backgroundColor: "#f0f9ff",
        }}
      >
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
          <ShieldCheck size={24} color="#0284c7" style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <h3 style={{ margin: "0 0 0.25rem 0", fontSize: "1rem", color: "#0369a1" }}>
              Agronomic Spray Window Guidance
            </h3>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#334155", lineHeight: "1.4" }}>
              {riskScore >= 70
                ? "Elevated humidity and rainfall conditions favor Phytophthora fruit rot (Koleroga) spore germination. Apply 1% Bordeaux mixture to bunches immediately during clear weather intervals."
                : riskScore >= 45
                ? "Moderate fungal pressure observed. Ensure drainage channels are unblocked and monitor developing nut bunches for early water-soaked lesions."
                : "Weather conditions are currently optimal with low fungal sporulation pressure. Maintain standard orchard scouting and irrigation."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
