import React, { useState, useEffect } from "react";
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  CloudRain,
  TrendingUp,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  Star,
  Send,
} from "lucide-react";
import { coordinatorApi } from "../api/coordinator";
import { learningApi } from "../api/learning";
import { useFarm } from "../context/FarmContext";

export const Dashboard = () => {
  const { selectedCropBlock } = useFarm();
  const [synthesisData, setSynthesisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Feedback State
  const [rating, setRating] = useState(5);
  const [outcomeNotes, setOutcomeNotes] = useState("");
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  const fetchSynthesis = async () => {
    if (!selectedCropBlock?.id) return;
    setLoading(true);
    setError("");
    try {
      const data = await coordinatorApi.synthesizeStatus(selectedCropBlock.id);
      setSynthesisData(data);
    } catch (err) {
      setError(err.message || "Failed to load multi-agent synthesis status");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSynthesis();
    setFeedbackSuccess(false);
  }, [selectedCropBlock?.id]);

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!synthesisData?.advisory?.id) return;
    setFeedbackLoading(true);
    try {
      await learningApi.submitFeedback(synthesisData.advisory.id, rating, outcomeNotes);
      setFeedbackSuccess(true);
    } catch (err) {
      alert("Failed to submit feedback: " + err.message);
    } finally {
      setFeedbackLoading(false);
    }
  };

  if (!selectedCropBlock) {
    return (
      <div style={{ textAlign: "center", padding: "4rem 2rem" }}>
        <p style={{ color: "#64748b" }}>Please select or register a crop block to view farm synthesis.</p>
      </div>
    );
  }

  const situation = synthesisData?.situation_score;
  const diag = synthesisData?.diagnosis;
  const weather = synthesisData?.weather;
  const market = synthesisData?.market;
  const advisory = synthesisData?.advisory;

  const getUrgencyBadgeClass = (level) => {
    switch (level?.toLowerCase()) {
      case "urgent":
        return "badge-urgent";
      case "high":
        return "badge-high";
      case "moderate":
        return "badge-moderate";
      default:
        return "badge-low";
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return "#ef4444";
    if (score >= 60) return "#f97316";
    if (score >= 40) return "#f59e0b";
    return "#10b981";
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header with Refresh */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", margin: 0 }}>Farm Synthesis Overview</h1>
          <p style={{ fontSize: "0.9rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
            Real-time multi-agent orchestration for <strong>{selectedCropBlock.block_name}</strong>
          </p>
        </div>
        <button className="btn btn-outline" onClick={fetchSynthesis} disabled={loading}>
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Synthesizing..." : "Refresh Status"}
        </button>
      </div>

      {error && (
        <div style={{ padding: "1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "10px", display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {loading && !synthesisData ? (
        <div className="card" style={{ padding: "3rem", textAlign: "center" }}>
          <p style={{ color: "#10b981", fontWeight: 600 }}>Executing Coordinator Consensus Across 8 Agents...</p>
        </div>
      ) : synthesisData ? (
        <>
          {/* Situation Urgency Score Card (Table 4.6) */}
          <div className="card" style={{ background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)" }}>
            <div className="card-header">
              <div className="card-title">
                <Activity size={20} color="#10b981" />
                <span>Overall Situation Score (Table 4.6 Consensus)</span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <span className={`badge ${getUrgencyBadgeClass(situation?.urgency_level)}`}>
                  {situation?.urgency_level} Urgency
                </span>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "2rem", alignItems: "center" }}>
              {/* Gauge */}
              <div style={{ textAlign: "center" }}>
                <div
                  className="score-circle"
                  style={{
                    border: `8px solid ${getScoreColor(situation?.composite_score || 0)}`,
                    boxShadow: `0 0 15px ${getScoreColor(situation?.composite_score || 0)}33`,
                  }}
                >
                  <span style={{ fontSize: "2rem", fontWeight: 800, color: "#0f172a" }}>
                    {situation?.composite_score?.toFixed(1) || 0}
                  </span>
                  <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 600 }}>OUT OF 100</span>
                </div>
                {situation?.urgency_drivers?.length > 0 && (
                  <div style={{ marginTop: "0.75rem" }}>
                    <span style={{ fontSize: "0.75rem", color: "#64748b", display: "block" }}>Urgency Drivers:</span>
                    <div style={{ display: "flex", gap: "0.25rem", justifyContent: "center", flexWrap: "wrap", marginTop: "0.2rem" }}>
                      {situation.urgency_drivers.map((d) => (
                        <span key={d} className="badge badge-urgent" style={{ fontSize: "0.7rem", padding: "0.15rem 0.4rem" }}>
                          {d}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Sub-Score Breakdown */}
              <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                {situation?.components &&
                  Object.entries(situation.components).map(([key, comp]) => (
                    <div key={key}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.25rem" }}>
                        <span style={{ fontWeight: 600, textTransform: "capitalize" }}>
                          {key} ({Math.round(comp.weight * 100)}% Weight)
                        </span>
                        <span style={{ color: "#64748b" }}>
                          Raw: <strong>{comp.raw_score.toFixed(1)}</strong> → Weighted:{" "}
                          <strong>{comp.weighted_score.toFixed(2)}</strong>
                        </span>
                      </div>
                      <div style={{ background: "#e2e8f0", height: "8px", borderRadius: "999px", overflow: "hidden" }}>
                        <div
                          style={{
                            width: `${Math.min(100, Math.max(0, comp.raw_score))}%`,
                            background: getScoreColor(comp.raw_score),
                            height: "100%",
                            borderRadius: "999px",
                            transition: "width 0.5s ease",
                          }}
                        />
                      </div>
                      <span style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.15rem", display: "block" }}>
                        {comp.summary}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          {/* Three Domain Cards */}
          <div className="grid-3">
            {/* Diagnosis Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <ShieldAlert size={18} color="#ef4444" />
                  <span>Disease Status</span>
                </div>
                <span className={`badge ${diag?.validated ? "badge-urgent" : "badge-low"}`}>
                  {diag?.validated ? "Validated" : "Pending"}
                </span>
              </div>
              <h3 style={{ fontSize: "1.2rem", color: "#0f172a", marginBottom: "0.5rem" }}>
                {diag?.predicted_disease || "No Disease Detected"}
              </h3>
              <div style={{ fontSize: "0.85rem", color: "#475569", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                <div>CNN Visual Confidence: <strong>{((diag?.cnn_confidence || 0) * 100).toFixed(1)}%</strong></div>
                <div>Bayesian Posterior P(D): <strong>{diag?.posterior_probability !== null ? `${((diag?.posterior_probability || 0) * 100).toFixed(1)}%` : "N/A"}</strong></div>
              </div>
            </div>

            {/* Weather Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <CloudRain size={18} color="#0284c7" />
                  <span>Weather Risk</span>
                </div>
                <span className={`badge ${getUrgencyBadgeClass(weather?.disease_risk_level)}`}>
                  {weather?.disease_risk_level} Risk
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "1.75rem", fontWeight: 700 }}>{weather?.temperature}°C</span>
                <span style={{ fontSize: "0.9rem", color: "#64748b" }}>{weather?.humidity}% Humidity</span>
              </div>
              <div style={{ fontSize: "0.85rem", color: "#475569", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                <div>Rainfall (24h): <strong>{weather?.rainfall_mm} mm</strong></div>
                <div>Risk Index: <strong>{weather?.disease_risk_score} / 100</strong></div>
              </div>
            </div>

            {/* Market Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <TrendingUp size={18} color="#10b981" />
                  <span>Market Timing</span>
                </div>
                <span className={`badge ${market?.price_trend === "rising" ? "badge-low" : "badge-moderate"}`}>
                  {market?.price_trend}
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "1.75rem", fontWeight: 700 }}>₹{market?.current_price_per_kg}</span>
                <span style={{ fontSize: "0.9rem", color: "#64748b" }}>/ kg</span>
              </div>
              <div style={{ fontSize: "0.85rem", color: "#475569", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                <div>Mandi: <strong>{market?.mandi_name}</strong></div>
                <div>Forecast: <strong>{market?.forecast_model}</strong></div>
              </div>
            </div>
          </div>

          {/* Synthesized Advisory Recommendations */}
          {advisory && (
            <div className="card" style={{ borderLeft: "4px solid #10b981" }}>
              <div className="card-header">
                <div className="card-title">
                  <Sparkles size={20} color="#10b981" />
                  <span>Synthesized Agronomic Advisory</span>
                </div>
                <span className={`badge ${getUrgencyBadgeClass(advisory.priority)}`}>
                  {advisory.priority} Priority
                </span>
              </div>

              <p style={{ fontSize: "1.05rem", fontWeight: 500, color: "#1e293b", marginBottom: "1rem" }}>
                {advisory.message}
              </p>

              {/* Action Steps */}
              {advisory.recommended_actions?.length > 0 && (
                <div style={{ marginBottom: "1.25rem" }}>
                  <h4 style={{ fontSize: "0.95rem", color: "#334155", marginBottom: "0.5rem" }}>
                    Recommended Action Steps:
                  </h4>
                  <ul style={{ listStyleType: "none", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {advisory.recommended_actions.map((act, idx) => (
                      <li
                        key={idx}
                        style={{
                          padding: "0.75rem 1rem",
                          backgroundColor: "#f8fafc",
                          borderRadius: "8px",
                          border: "1px solid #e2e8f0",
                          fontSize: "0.9rem",
                          color: "#1e293b",
                        }}
                      >
                        {act}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {advisory.reasoning_summary && (
                <div style={{ background: "#f1f5f9", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.85rem", color: "#475569", marginBottom: "1rem" }}>
                  <strong>Agronomic Reasoning:</strong> {advisory.reasoning_summary}
                </div>
              )}

              <p style={{ fontSize: "0.75rem", color: "#94a3b8", fontStyle: "italic", margin: 0 }}>
                {advisory.disclaimer || "Chemical and dosage recommendations follow standard ICAR-CPCRI guidelines. Consult local extension officers before application."}
              </p>

              {/* Feedback Loop for Learning Agent */}
              <div style={{ marginTop: "1.5rem", paddingTop: "1.25rem", borderTop: "1px solid #f1f5f9" }}>
                <h4 style={{ fontSize: "0.9rem", marginBottom: "0.5rem" }}>
                  Rate this Advisory (Learning Agent Feedback Loop):
                </h4>
                {feedbackSuccess ? (
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#047857", background: "#d1fae5", padding: "0.5rem 0.75rem", borderRadius: "8px", fontSize: "0.85rem" }}>
                    <CheckCircle2 size={16} />
                    <span>Feedback recorded! Q-learning value updated for this state-action context.</span>
                  </div>
                ) : (
                  <form onSubmit={handleFeedbackSubmit} style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
                    <div style={{ display: "flex", gap: "0.25rem" }}>
                      {[1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => setRating(s)}
                          style={{ background: "none", border: "none", cursor: "pointer", padding: "0.2rem" }}
                        >
                          <Star size={20} fill={s <= rating ? "#f59e0b" : "none"} color={s <= rating ? "#f59e0b" : "#cbd5e1"} />
                        </button>
                      ))}
                    </div>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Optional notes (e.g. spray controlled rot)"
                      style={{ flex: 1, minWidth: "200px", padding: "0.4rem 0.75rem", fontSize: "0.85rem" }}
                      value={outcomeNotes}
                      onChange={(e) => setOutcomeNotes(e.target.value)}
                    />
                    <button type="submit" className="btn btn-secondary" style={{ fontSize: "0.85rem", padding: "0.4rem 0.85rem" }} disabled={feedbackLoading}>
                      <Send size={14} />
                      {feedbackLoading ? "Saving..." : "Submit Feedback"}
                    </button>
                  </form>
                )}
              </div>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
};
