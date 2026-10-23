import React, { useState, useEffect } from "react";
import { TrendingUp, Building, Calendar, ArrowUpRight, ArrowDownRight, RefreshCw, Layers, LineChart, Info } from "lucide-react";
import { marketApi } from "../api/market";
import { useAuth } from "../context/AuthContext";

const KARNATAKA_MANDIS = [
  "Shivamogga APMC",
  "Mangalore APMC",
  "Sirsi APMC",
  "Sagar APMC",
  "Tumkur APMC",
  "Channagiri APMC",
];

export const Market = () => {
  const { profile } = useAuth();
  const [selectedMandi, setSelectedMandi] = useState(profile?.preferred_mandi || "Shivamogga APMC");
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hoveredPoint, setHoveredPoint] = useState(null);

  useEffect(() => {
    if (profile?.preferred_mandi) {
      setSelectedMandi(profile.preferred_mandi);
    }
  }, [profile?.preferred_mandi]);

  const fetchMarket = async (mandiToFetch = selectedMandi) => {
    setLoading(true);
    setError("");
    try {
      const data = await marketApi.getPrices(mandiToFetch);
      setMarketData(data);
    } catch (err) {
      console.warn("Market fetch failed:", err.message);
      setError(err.message || "Failed to load market data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarket(selectedMandi);
  }, [selectedMandi]);

  const currentPrice = marketData?.current_price_per_kg ?? 475.0;
  const forecastList = marketData?.forecast || [];
  const historicalList = marketData?.historical_prices || [];
  const varietyList = marketData?.variety_prices || [];
  const modelUsed = forecastList[0]?.forecast_model || "linear_trend_regression";

  const finalForecastPrice = forecastList.length > 0
    ? forecastList[forecastList.length - 1].predicted_price_per_kg
    : currentPrice;
  const isRising = finalForecastPrice >= currentPrice;

  // Build combined chart points (Historical + Forecast)
  const chartPoints = [];
  const recentHistory = [...historicalList].reverse().slice(-5);
  recentHistory.forEach((h, idx) => {
    chartPoints.push({
      date: h.price_date,
      label: new Date(h.price_date).toLocaleDateString([], { month: "short", day: "numeric" }),
      price: Number(h.price_per_kg),
      type: "history",
    });
  });

  if (chartPoints.length === 0) {
    chartPoints.push({
      date: marketData?.price_date || "Today",
      label: "Today",
      price: currentPrice,
      type: "history",
    });
  }

  forecastList.forEach((f, idx) => {
    chartPoints.push({
      date: f.forecast_date,
      label: new Date(f.forecast_date).toLocaleDateString([], { month: "short", day: "numeric" }),
      price: Number(f.predicted_price_per_kg),
      lower: Number(f.lower_bound),
      upper: Number(f.upper_bound),
      type: "forecast",
    });
  });

  // Calculate SVG scales
  const chartW = 700;
  const chartH = 220;
  const padX = 50;
  const padY = 30;
  const innerW = chartW - padX * 2;
  const innerH = chartH - padY * 2;

  const allPrices = chartPoints.map((p) => p.price);
  const minP = Math.min(...allPrices, ...chartPoints.filter((p) => p.lower).map((p) => p.lower)) * 0.96;
  const maxP = Math.max(...allPrices, ...chartPoints.filter((p) => p.upper).map((p) => p.upper)) * 1.04;

  const getX = (idx) => padX + (idx / Math.max(1, chartPoints.length - 1)) * innerW;
  const getY = (price) => padY + innerH - ((price - minP) / Math.max(1, maxP - minP)) * innerH;

  const svgPointsStr = chartPoints.map((p, idx) => `${getX(idx)},${getY(p.price)}`).join(" ");

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", margin: 0 }}>APMC Market Trends & Forecasts</h1>
          <p style={{ fontSize: "0.9rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
            Live mandi prices from data.gov.in with multi-variety breakdowns & 7-day predictive forecasting
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <select
            value={selectedMandi}
            onChange={(e) => setSelectedMandi(e.target.value)}
            style={{
              padding: "0.5rem 0.75rem",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "0.9rem",
              fontWeight: 500,
              backgroundColor: "#fff",
              cursor: "pointer",
            }}
          >
            {KARNATAKA_MANDIS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>

          <button className="btn btn-outline" onClick={() => fetchMarket(selectedMandi)} disabled={loading}>
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ padding: "0.75rem 1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "8px", fontSize: "0.85rem", marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      {/* Main 2 Hero Cards */}
      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Building size={18} color="#10b981" />
              <span>Modal Spot Price ({marketData?.mandi_name || selectedMandi})</span>
            </div>
            <span className={`badge ${isRising ? "badge-low" : "badge-urgent"}`}>
              {isRising ? "Rising Trend" : "Softening Trend"}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
            <h2 style={{ fontSize: "2.25rem", margin: 0, color: "#0f172a" }}>₹{currentPrice.toFixed(2)}</h2>
            <span style={{ fontSize: "1rem", color: "#64748b" }}>/ kg ({marketData?.commodity || "Arecanut"})</span>
          </div>
          <p style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.5rem", marginBottom: 0 }}>
            Model: <strong>{modelUsed}</strong> | Source: <strong>{marketData?.source || "data.gov.in"}</strong>
          </p>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <TrendingUp size={18} color="#0284c7" />
              <span>7-Day Harvest Timing Recommendation</span>
            </div>
          </div>
          <p style={{ fontSize: "0.95rem", color: "#334155", margin: 0, lineHeight: "1.5" }}>
            {isRising
              ? `Prices at ${selectedMandi} are trending upward over the upcoming week (+₹${(finalForecastPrice - currentPrice).toFixed(2)}/kg projected). Farmers are advised to hold mature cured stock for staggered mandi delivery to capture peak pricing.`
              : `Prices at ${selectedMandi} are projected to soften slightly. Consider completing harvest and releasing cured lots in the next 48-72 hours before local arrival volume peaks.`}
          </p>
        </div>
      </div>

      {/* Multi-Variety Price Breakdown Cards */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="card-header" style={{ marginBottom: "1rem" }}>
          <div className="card-title">
            <Layers size={18} color="#0284c7" />
            <span>Karnataka Arecanut Variety Price Breakdown ({marketData?.mandi_name || selectedMandi})</span>
          </div>
          <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Spot prices by processed grade</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
          {varietyList.length > 0 ? (
            varietyList.map((v, idx) => {
              const diff = v.price_per_kg - currentPrice;
              return (
                <div
                  key={idx}
                  style={{
                    padding: "1rem",
                    borderRadius: "10px",
                    backgroundColor: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>{v.variety}</span>
                      <span style={{ fontSize: "0.75rem", color: "#64748b" }}>{v.price_date}</span>
                    </div>
                    <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block", marginTop: "0.2rem" }}>
                      {v.description || `${v.variety} grade arecanut`}
                    </span>
                  </div>

                  <div style={{ marginTop: "0.75rem", display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                    <span style={{ fontSize: "1.4rem", fontWeight: 700, color: "#0f172a" }}>
                      ₹{Number(v.price_per_kg).toFixed(2)}
                    </span>
                    <span style={{ fontSize: "0.75rem", color: "#64748b" }}>/ kg</span>
                  </div>
                </div>
              );
            })
          ) : (
            <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "1.5rem", color: "#64748b" }}>
              Loading variety price data...
            </div>
          )}
        </div>
      </div>

      {/* Interactive Price Trend Chart */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="card-header" style={{ marginBottom: "0.5rem" }}>
          <div className="card-title">
            <LineChart size={18} color="#16a34a" />
            <span>Price Trajectory & LSTM Confidence Interval ({marketData?.mandi_name || selectedMandi})</span>
          </div>
          <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Past Arrivals & 7-Day Forecast</span>
        </div>

        {chartPoints.length > 1 && (
          <div style={{ position: "relative", width: "100%", overflowX: "auto" }}>
            <svg
              viewBox={`0 0 ${chartW} ${chartH}`}
              style={{ width: "100%", maxHeight: "260px", display: "block" }}
            >
              {/* Grid Lines */}
              <line x1={padX} y1={padY} x2={chartW - padX} y2={padY} stroke="#f1f5f9" strokeWidth="1" />
              <line x1={padX} y1={padY + innerH / 2} x2={chartW - padX} y2={padY + innerH / 2} stroke="#f1f5f9" strokeWidth="1" />
              <line x1={padX} y1={padY + innerH} x2={chartW - padX} y2={padY + innerH} stroke="#e2e8f0" strokeWidth="1" />

              {/* Shaded Area under Curve */}
              <polygon
                points={`${padX},${padY + innerH} ${svgPointsStr} ${chartW - padX},${padY + innerH}`}
                fill="url(#priceGrad)"
                opacity="0.25"
              />

              <defs>
                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Connecting Line */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={svgPointsStr}
              />

              {/* Interactive Data Points */}
              {chartPoints.map((p, idx) => {
                const cx = getX(idx);
                const cy = getY(p.price);
                const isHovered = hoveredPoint?.idx === idx;
                const isForecast = p.type === "forecast";

                return (
                  <g key={idx}>
                    <circle
                      cx={cx}
                      cy={cy}
                      r={isHovered ? 6 : 4}
                      fill={isForecast ? "#0284c7" : "#10b981"}
                      stroke="#fff"
                      strokeWidth="2"
                      style={{ cursor: "pointer", transition: "all 0.15s ease" }}
                      onMouseEnter={() => setHoveredPoint({ ...p, idx, cx, cy })}
                      onMouseLeave={() => setHoveredPoint(null)}
                    />
                    {/* X-Axis Date Labels */}
                    {(idx % 2 === 0 || idx === chartPoints.length - 1) && (
                      <text
                        x={cx}
                        y={chartH - 8}
                        textAnchor="middle"
                        fontSize="10"
                        fill="#64748b"
                      >
                        {p.label}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Y-Axis Price Labels */}
              <text x={padX - 8} y={padY + 4} textAnchor="end" fontSize="10" fill="#94a3b8">
                ₹{maxP.toFixed(0)}
              </text>
              <text x={padX - 8} y={padY + innerH / 2 + 4} textAnchor="end" fontSize="10" fill="#94a3b8">
                ₹{((minP + maxP) / 2).toFixed(0)}
              </text>
              <text x={padX - 8} y={padY + innerH + 4} textAnchor="end" fontSize="10" fill="#94a3b8">
                ₹{minP.toFixed(0)}
              </text>
            </svg>

            {/* Hover Tooltip */}
            {hoveredPoint && (
              <div
                style={{
                  position: "absolute",
                  left: `${(hoveredPoint.cx / chartW) * 100}%`,
                  top: `${(hoveredPoint.cy / chartH) * 100 - 25}%`,
                  transform: "translate(-50%, -100%)",
                  backgroundColor: "#0f172a",
                  color: "#fff",
                  padding: "0.4rem 0.6rem",
                  borderRadius: "6px",
                  fontSize: "0.75rem",
                  pointerEvents: "none",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.2)",
                  whiteSpace: "nowrap",
                  zIndex: 10,
                }}
              >
                <div style={{ fontWeight: 600 }}>{hoveredPoint.label} ({hoveredPoint.type === "forecast" ? "Forecast" : "Actual"})</div>
                <div style={{ color: "#34d399", fontWeight: 700 }}>₹{hoveredPoint.price.toFixed(2)}/kg</div>
                {hoveredPoint.lower && hoveredPoint.upper && (
                  <div style={{ fontSize: "0.65rem", color: "#94a3b8" }}>
                    Band: ₹{hoveredPoint.lower.toFixed(0)} - ₹{hoveredPoint.upper.toFixed(0)}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 7-Day Forecast Grid Cards */}
      {forecastList.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Calendar size={18} color="#10b981" />
              <span>7-Day Projected Mandi Prices ({marketData?.mandi_name || selectedMandi})</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "0.75rem" }}>
            {forecastList.map((item, idx) => {
              const diff = item.predicted_price_per_kg - currentPrice;
              return (
                <div
                  key={idx}
                  style={{
                    padding: "0.85rem",
                    borderRadius: "10px",
                    backgroundColor: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    textAlign: "center",
                  }}
                >
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600, display: "block" }}>
                    Day {idx + 1} ({new Date(item.forecast_date).toLocaleDateString([], { month: "short", day: "numeric" })})
                  </span>
                  <div style={{ fontSize: "1.15rem", fontWeight: 700, color: "#0f172a", margin: "0.25rem 0" }}>
                    ₹{item.predicted_price_per_kg.toFixed(2)}
                  </div>
                  <span
                    style={{
                      fontSize: "0.7rem",
                      fontWeight: 600,
                      color: diff >= 0 ? "#16a34a" : "#dc2626",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "2px",
                    }}
                  >
                    {diff >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                    {diff >= 0 ? `+₹${diff.toFixed(2)}` : `-₹${Math.abs(diff).toFixed(2)}`}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default Market;
