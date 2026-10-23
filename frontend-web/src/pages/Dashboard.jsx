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
  Zap,
} from "lucide-react";
import { coordinatorApi } from "../api/coordinator";
import { learningApi } from "../api/learning";
import { useFarm } from "../context/FarmContext";
import BentoCard from "@/components/ui/bento-card";

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
        <p style={{ color: "#000000", fontWeight: 700, fontSize: "1.1rem" }}>
          Please select or register a crop block to view farm synthesis.
        </p>
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
    if (score >= 75) return "#ff5252";
    if (score >= 60) return "#ff9f1c";
    if (score >= 40) return "#ffe17c";
    return "#2ec4b6";
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header with Title and Quick Refresh */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "1.5rem",
          paddingBottom: "0.5rem",
          flexWrap: "wrap",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "2.1rem",
              margin: 0,
              fontWeight: 800,
              fontFamily: "var(--font-heading)",
              letterSpacing: "-0.04em",
              color: "#000000",
              lineHeight: 1.15,
            }}
          >
            Farm Synthesis Overview
          </h1>
          <p
            style={{
              fontSize: "0.95rem",
              color: "#171e19",
              margin: "0.4rem 0 0 0",
              fontWeight: 500,
              lineHeight: 1.5,
              fontFamily: "var(--font-body)",
            }}
          >
            Real-time multi-agent orchestration for{" "}
            <strong
              style={{
                color: "#000000",
                fontWeight: 800,
                backgroundColor: "#ffe17c",
                padding: "0.1rem 0.4rem",
                border: "1px solid #000000",
                borderRadius: "3px",
              }}
            >
              {selectedCropBlock.block_name}
            </strong>
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={fetchSynthesis}
          disabled={loading}
          style={{
            flexShrink: 0,
            marginTop: "0.25rem",
          }}
        >
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} strokeWidth={2.5} />
          {loading ? "Synthesizing..." : "Refresh Swarm"}
        </button>
      </div>

      {/* Bento Interactive Project & Team Performance Hub */}
      <BentoCard />

      {error && (
        <div
          style={{
            padding: "1rem 1.25rem",
            backgroundColor: "#ff5252",
            border: "2px solid #000000",
            color: "#ffffff",
            borderRadius: "6px",
            display: "flex",
            gap: "0.75rem",
            alignItems: "center",
            boxShadow: "4px 4px 0px 0px #000000",
            fontFamily: "var(--font-heading)",
            fontWeight: 800,
          }}
        >
          <AlertCircle size={22} strokeWidth={2.5} />
          <span style={{ fontSize: "0.95rem" }}>{error}</span>
        </div>
      )}

      {loading && !synthesisData ? (
        <div
          className="card card-large"
          style={{ padding: "3.5rem", textAlign: "center", backgroundColor: "#ffffff" }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "1rem",
              borderRadius: "8px",
              backgroundColor: "#ffe17c",
              border: "2px solid #000000",
              boxShadow: "4px 4px 0px 0px #000000",
              marginBottom: "1.25rem",
            }}
          >
            <Zap size={32} color="#000000" className="animate-spin" strokeWidth={2.5} />
          </div>
          <p
            style={{
              color: "#000000",
              fontWeight: 800,
              fontSize: "1.2rem",
              fontFamily: "var(--font-heading)",
              letterSpacing: "-0.02em",
            }}
          >
            Executing Coordinator Consensus Across 8 Specialized Agents...
          </p>
          <span
            style={{
              fontSize: "0.9rem",
              color: "#171e19",
              marginTop: "0.4rem",
              display: "block",
              fontWeight: 500,
            }}
          >
            Synthesizing pathology inference, meteorological outlook, and APMC trends
          </span>
        </div>
      ) : synthesisData ? (
        <>
          {/* Situation Urgency Score Card: Large Container with 8px hard shadow */}
          <div
            className="card card-large"
            style={{
              backgroundColor: "#ffffff",
              padding: "1.75rem",
            }}
          >
            <div className="card-header">
              <div className="card-title">
                <div
                  style={{
                    backgroundColor: "#ffe17c",
                    padding: "0.45rem",
                    borderRadius: "4px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "2px solid #000000",
                    boxShadow: "2px 2px 0px 0px #000000",
                  }}
                >
                  <Activity size={20} color="#000000" strokeWidth={2.5} />
                </div>
                <span>Overall Situation Score</span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <span className={`badge ${getUrgencyBadgeClass(situation?.urgency_level)}`}>
                  <span className="badge-dot" />
                  {situation?.urgency_level} Urgency
                </span>
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "200px 1fr",
                gap: "2.5rem",
                alignItems: "center",
                padding: "0.5rem 0",
              }}
            >
              {/* Score Gauge */}
              <div style={{ textAlign: "center" }}>
                <div
                  className="score-circle"
                  style={{
                    backgroundColor: getScoreColor(situation?.composite_score || 0),
                  }}
                >
                  <span
                    style={{
                      fontSize: "2.6rem",
                      fontWeight: 800,
                      color: "#000000",
                      letterSpacing: "-0.04em",
                      fontFamily: "var(--font-heading)",
                      lineHeight: 1,
                    }}
                  >
                    {situation?.composite_score?.toFixed(1) || 0}
                  </span>
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "#000000",
                      fontWeight: 800,
                      fontFamily: "var(--font-mono)",
                      letterSpacing: "0.06em",
                      marginTop: "4px",
                      textTransform: "uppercase",
                    }}
                  >
                    Out of 100
                  </span>
                </div>
                {situation?.urgency_drivers?.length > 0 && (
                  <div style={{ marginTop: "1rem" }}>
                    <span
                      style={{
                        fontSize: "0.75rem",
                        color: "#000000",
                        display: "block",
                        fontWeight: 800,
                        textTransform: "uppercase",
                        letterSpacing: "0.04em",
                        fontFamily: "var(--font-heading)",
                      }}
                    >
                      Urgency Drivers:
                    </span>
                    <div
                      style={{
                        display: "flex",
                        gap: "0.4rem",
                        justifyContent: "center",
                        flexWrap: "wrap",
                        marginTop: "0.4rem",
                      }}
                    >
                      {situation.urgency_drivers.map((d) => (
                        <span
                          key={d}
                          className="badge badge-urgent"
                          style={{ fontSize: "0.72rem", padding: "0.2rem 0.5rem" }}
                        >
                          {d}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Sub-Score Breakdown */}
              <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                {situation?.components &&
                  Object.entries(situation.components).map(([key, comp]) => (
                    <div key={key}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "0.9rem",
                          marginBottom: "0.45rem",
                          alignItems: "baseline",
                        }}
                      >
                        <span
                          style={{
                            fontWeight: 800,
                            textTransform: "capitalize",
                            color: "#000000",
                            fontFamily: "var(--font-heading)",
                            letterSpacing: "-0.02em",
                          }}
                        >
                          {key}
                          <span
                            style={{
                              fontWeight: 600,
                              color: "#64748b",
                              marginLeft: "8px",
                              fontSize: "0.8rem",
                              fontFamily: "var(--font-body)",
                            }}
                          >
                            ({Math.round(comp.weight * 100)}% Weight)
                          </span>
                        </span>
                        <span
                          style={{
                            color: "#000000",
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.82rem",
                            fontWeight: 700,
                          }}
                        >
                          Raw: <strong>{comp.raw_score.toFixed(1)}</strong> → Weighted:{" "}
                          <strong style={{ backgroundColor: "#ffe17c", padding: "1px 5px", border: "1px solid #000000", borderRadius: "3px" }}>
                            {comp.weighted_score.toFixed(2)}
                          </strong>
                        </span>
                      </div>
                      <div
                        style={{
                          backgroundColor: "#f0f0f0",
                          border: "2px solid #000000",
                          height: "12px",
                          borderRadius: "4px",
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            width: `${Math.min(100, Math.max(0, comp.raw_score))}%`,
                            backgroundColor: getScoreColor(comp.raw_score),
                            borderRight: "2px solid #000000",
                            height: "100%",
                            transition: "width 0.4s ease",
                          }}
                        />
                      </div>
                      <span
                        style={{
                          fontSize: "0.82rem",
                          color: "#171e19",
                          marginTop: "0.35rem",
                          display: "block",
                          lineHeight: 1.45,
                          fontWeight: 500,
                        }}
                      >
                        {comp.summary}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </div>

          {/* Three Domain Telemetry Cards: 4px 4px hard shadow */}
          <div className="grid-3">
            {/* Diagnosis Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <div
                    style={{
                      backgroundColor: "#ff5252",
                      padding: "0.4rem",
                      borderRadius: "4px",
                      border: "2px solid #000000",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "2px 2px 0px 0px #000000",
                    }}
                  >
                    <ShieldAlert size={18} color="#ffffff" strokeWidth={2.5} />
                  </div>
                  <span>Disease Status</span>
                </div>
                <span className={`badge ${diag?.validated ? "badge-urgent" : "badge-low"}`}>
                  <span className="badge-dot" />
                  {diag?.validated ? "Validated" : "Pending"}
                </span>
              </div>
              <h3
                style={{
                  fontSize: "1.3rem",
                  color: "#000000",
                  marginBottom: "0.85rem",
                  fontWeight: 800,
                  fontFamily: "var(--font-heading)",
                  letterSpacing: "-0.03em",
                }}
              >
                {diag?.predicted_disease || "No Disease Detected"}
              </h3>
              <div
                style={{
                  fontSize: "0.875rem",
                  color: "#171e19",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.6rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600 }}>CNN Visual Confidence</span>
                  <strong
                    style={{
                      color: "#000000",
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.85rem",
                      backgroundColor: "#b7c6c2",
                      padding: "2px 6px",
                      border: "1px solid #000000",
                      borderRadius: "3px",
                    }}
                  >
                    {((diag?.cnn_confidence || 0) * 100).toFixed(1)}%
                  </strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600 }}>Bayesian Posterior P(D)</span>
                  <strong
                    style={{
                      color: "#000000",
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.85rem",
                      backgroundColor: "#ffe17c",
                      padding: "2px 6px",
                      border: "1px solid #000000",
                      borderRadius: "3px",
                    }}
                  >
                    {diag?.posterior_probability !== null ? `${((diag?.posterior_probability || 0) * 100).toFixed(1)}%` : "N/A"}
                  </strong>
                </div>
              </div>
            </div>

            {/* Weather Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <div
                    style={{
                      backgroundColor: "#70d6ff",
                      padding: "0.4rem",
                      borderRadius: "4px",
                      border: "2px solid #000000",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "2px 2px 0px 0px #000000",
                    }}
                  >
                    <CloudRain size={18} color="#000000" strokeWidth={2.5} />
                  </div>
                  <span>Weather Risk</span>
                </div>
                <span className={`badge ${getUrgencyBadgeClass(weather?.disease_risk_level)}`}>
                  <span className="badge-dot" />
                  {weather?.disease_risk_level} Risk
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.6rem", marginBottom: "0.85rem" }}>
                <span
                  style={{
                    fontSize: "2rem",
                    fontWeight: 800,
                    color: "#000000",
                    letterSpacing: "-0.04em",
                    fontFamily: "var(--font-heading)",
                  }}
                >
                  {weather?.temperature}°C
                </span>
                <span
                  style={{
                    fontSize: "0.85rem",
                    color: "#000000",
                    fontWeight: 700,
                    fontFamily: "var(--font-mono)",
                    backgroundColor: "#b7c6c2",
                    padding: "2px 6px",
                    border: "1px solid #000000",
                    borderRadius: "3px",
                  }}
                >
                  {weather?.humidity}% Humidity
                </span>
              </div>
              <div
                style={{
                  fontSize: "0.875rem",
                  color: "#171e19",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.6rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600 }}>Rainfall (24h)</span>
                  <strong
                    style={{
                      color: "#000000",
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.85rem",
                    }}
                  >
                    {weather?.rainfall_mm} mm
                  </strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600 }}>Risk Index</span>
                  <strong
                    style={{
                      color: "#000000",
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.85rem",
                      backgroundColor: "#ffe17c",
                      padding: "2px 6px",
                      border: "1px solid #000000",
                      borderRadius: "3px",
                    }}
                  >
                    {weather?.disease_risk_score} / 100
                  </strong>
                </div>
              </div>
            </div>

            {/* Market Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <div
                    style={{
                      backgroundColor: "#ffe17c",
                      padding: "0.4rem",
                      borderRadius: "4px",
                      border: "2px solid #000000",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "2px 2px 0px 0px #000000",
                    }}
                  >
                    <TrendingUp size={18} color="#000000" strokeWidth={2.5} />
                  </div>
                  <span>Market Timing</span>
                </div>
                <span className={`badge ${market?.price_trend === "rising" ? "badge-low" : "badge-moderate"}`}>
                  <span className="badge-dot" />
                  {market?.price_trend}
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "0.4rem", marginBottom: "0.85rem" }}>
                <span
                  style={{
                    fontSize: "2rem",
                    fontWeight: 800,
                    color: "#000000",
                    letterSpacing: "-0.04em",
                    fontFamily: "var(--font-heading)",
                  }}
                >
                  ₹{market?.current_price_per_kg}
                </span>
                <span style={{ fontSize: "0.9rem", color: "#171e19", fontWeight: 700 }}>/ kg</span>
              </div>
              <div
                style={{
                  fontSize: "0.875rem",
                  color: "#171e19",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.6rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600 }}>Mandi</span>
                  <strong style={{ color: "#000000", fontFamily: "var(--font-heading)", fontWeight: 800 }}>
                    {market?.mandi_name}
                  </strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 600 }}>Forecast Model</span>
                  <strong style={{ color: "#000000", fontFamily: "var(--font-mono)", fontSize: "0.82rem" }}>
                    {market?.forecast_model}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {/* Synthesized Advisory Recommendations: Large Container with 8px hard shadow */}
          {advisory && (
            <div
              className="card card-large"
              style={{
                backgroundColor: "#ffe17c",
                backgroundImage: "radial-gradient(rgba(0, 0, 0, 0.10) 2px, transparent 2px)",
                backgroundSize: "32px 32px",
                padding: "2rem",
              }}
            >
              <div className="card-header" style={{ borderBottomColor: "#000000" }}>
                <div className="card-title">
                  <div
                    style={{
                      backgroundColor: "#171e19",
                      padding: "0.4rem",
                      borderRadius: "4px",
                      border: "2px solid #000000",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "2px 2px 0px 0px #000000",
                    }}
                  >
                    <Sparkles size={20} color="#ffe17c" strokeWidth={2.5} />
                  </div>
                  <span>Synthesized Agronomic Advisory</span>
                </div>
                <span className={`badge ${getUrgencyBadgeClass(advisory.priority)}`}>
                  <span className="badge-dot" />
                  {advisory.priority} Priority
                </span>
              </div>

              <div
                style={{
                  backgroundColor: "#ffffff",
                  padding: "1.25rem 1.5rem",
                  borderRadius: "6px",
                  border: "2px solid #000000",
                  boxShadow: "4px 4px 0px 0px #000000",
                  marginBottom: "1.5rem",
                }}
              >
                <p
                  style={{
                    fontSize: "1.15rem",
                    fontWeight: 700,
                    color: "#000000",
                    lineHeight: 1.5,
                    margin: 0,
                  }}
                >
                  {advisory.message}
                </p>
              </div>

              {/* Action Steps */}
              {advisory.recommended_actions?.length > 0 && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <h4
                    style={{
                      fontSize: "1.05rem",
                      color: "#000000",
                      marginBottom: "0.75rem",
                      fontWeight: 800,
                      fontFamily: "var(--font-heading)",
                      letterSpacing: "-0.02em",
                    }}
                  >
                    Recommended Action Steps:
                  </h4>
                  <ul style={{ listStyleType: "none", display: "flex", flexDirection: "column", gap: "0.7rem" }}>
                    {advisory.recommended_actions.map((act, idx) => (
                      <li
                        key={idx}
                        style={{
                          padding: "0.9rem 1.25rem",
                          backgroundColor: "#ffffff",
                          borderRadius: "4px",
                          border: "2px solid #000000",
                          boxShadow: "3px 3px 0px 0px #000000",
                          fontSize: "0.95rem",
                          fontWeight: 600,
                          color: "#000000",
                          display: "flex",
                          alignItems: "center",
                          gap: "0.85rem",
                        }}
                      >
                        <CheckCircle2 size={18} color="#000000" strokeWidth={2.5} style={{ flexShrink: 0 }} />
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {advisory.reasoning_summary && (
                <div
                  style={{
                    backgroundColor: "#b7c6c2",
                    padding: "1rem 1.25rem",
                    borderRadius: "4px",
                    border: "2px solid #000000",
                    boxShadow: "3px 3px 0px 0px #000000",
                    fontSize: "0.9rem",
                    color: "#000000",
                    marginBottom: "1.25rem",
                    fontWeight: 500,
                  }}
                >
                  <strong style={{ fontFamily: "var(--font-heading)", fontWeight: 800 }}>Agronomic Reasoning: </strong>
                  {advisory.reasoning_summary}
                </div>
              )}

              <p style={{ fontSize: "0.8rem", color: "#171e19", fontWeight: 600, fontStyle: "italic", margin: 0 }}>
                {advisory.disclaimer ||
                  "Chemical and dosage recommendations follow standard ICAR-CPCRI guidelines. Consult local extension officers before application."}
              </p>

              {/* Feedback Loop for Learning Agent */}
              <div
                style={{
                  marginTop: "1.75rem",
                  paddingTop: "1.5rem",
                  borderTop: "2px solid #000000",
                }}
              >
                <h4
                  style={{
                    fontSize: "0.95rem",
                    marginBottom: "0.75rem",
                    fontWeight: 800,
                    fontFamily: "var(--font-heading)",
                  }}
                >
                  Rate this Advisory (Learning Agent Feedback Loop):
                </h4>
                {feedbackSuccess ? (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.6rem",
                      color: "#000000",
                      backgroundColor: "#ffffff",
                      border: "2px solid #000000",
                      boxShadow: "4px 4px 0px 0px #000000",
                      padding: "0.85rem 1.15rem",
                      borderRadius: "4px",
                      fontSize: "0.9rem",
                      fontWeight: 700,
                    }}
                  >
                    <CheckCircle2 size={20} strokeWidth={2.5} />
                    <span>Feedback recorded! Q-learning value updated for this state-action context.</span>
                  </div>
                ) : (
                  <form
                    onSubmit={handleFeedbackSubmit}
                    style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}
                  >
                    <div
                      style={{
                        display: "flex",
                        gap: "0.3rem",
                        backgroundColor: "#ffffff",
                        padding: "0.4rem 0.6rem",
                        border: "2px solid #000000",
                        boxShadow: "3px 3px 0px 0px #000000",
                        borderRadius: "4px",
                      }}
                    >
                      {[1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => setRating(s)}
                          style={{
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            padding: "0.2rem",
                            transition: "transform 0.12s ease",
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.2)")}
                          onMouseLeave={(e) => (e.currentTarget.style.transform = "none")}
                        >
                          <Star
                            size={22}
                            fill={s <= rating ? "#000000" : "none"}
                            color="#000000"
                            strokeWidth={2}
                          />
                        </button>
                      ))}
                    </div>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Optional notes (e.g. spray controlled fruit rot within 4 days)"
                      style={{ flex: 1, minWidth: "220px" }}
                      value={outcomeNotes}
                      onChange={(e) => setOutcomeNotes(e.target.value)}
                    />
                    <button
                      type="submit"
                      className="btn btn-dark"
                      disabled={feedbackLoading}
                    >
                      <Send size={15} strokeWidth={2.5} />
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
