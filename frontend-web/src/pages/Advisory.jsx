import React, { useState } from "react";
import { Sparkles, RefreshCw, AlertCircle, CheckCircle2, ShieldAlert, Cpu, ArrowRight } from "lucide-react";
import { advisoryApi } from "../api/advisory";
import { useFarm } from "../context/FarmContext";

export const Advisory = () => {
  const { selectedCropBlock } = useFarm();
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!selectedCropBlock) return;
    setLoading(true);
    setError("");
    try {
      const data = await advisoryApi.generateAdvisory(selectedCropBlock.id);
      setAdvisory(data);
    } catch (err) {
      console.warn("Advisory generation error:", err);
      setError(err.message || "Failed to synthesize advisory");
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyBadgeClass = (priority) => {
    switch (priority?.toLowerCase()) {
      case "urgent":
        return "badge-urgent";
      case "high":
        return "badge-high";
      case "medium":
      case "moderate":
        return "badge-moderate";
      default:
        return "badge-low";
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.85rem", margin: 0, fontWeight: 800 }}>Agronomic Advisory Agent</h1>
          <p style={{ fontSize: "0.925rem", color: "#64748b", margin: "0.3rem 0 0 0" }}>
            Autonomous Gemini 2.0 Flash agronomic synthesis for{" "}
            <strong style={{ color: "#0a1a0f" }}>{selectedCropBlock?.block_name || "Crop Block"}</strong>
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={loading || !selectedCropBlock}
          style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}
        >
          <Sparkles size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Synthesizing with Gemini..." : "Generate New Advisory"}
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
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
          }}
        >
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {advisory ? (
        <div
          className="card"
          style={{
            borderLeft: "5px solid #15803d",
            background: "linear-gradient(135deg, #ffffff 0%, #f9fdfa 100%)",
            boxShadow: "0 6px 20px -2px rgba(21, 128, 61, 0.08)",
          }}
        >
          <div className="card-header">
            <div className="card-title">
              <div
                style={{
                  background: "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                  padding: "0.45rem",
                  borderRadius: "10px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "1px solid #bbf7d0",
                }}
              >
                <Sparkles size={18} color="#15803d" />
              </div>
              <span>Priority: {advisory.priority?.toUpperCase()}</span>
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <span className={`badge ${getUrgencyBadgeClass(advisory.priority)}`}>
                <span className="badge-dot" />
                {advisory.priority} Priority
              </span>
              <span className="badge badge-low">
                Engine: {advisory.generated_by || "Gemini 2.0 Flash"}
              </span>
            </div>
          </div>

          <p style={{ fontSize: "1.1rem", fontWeight: 600, color: "#0a1a0f", marginBottom: "1.35rem", lineHeight: 1.55 }}>
            {advisory.message}
          </p>

          {advisory.recommended_actions?.length > 0 && (
            <div style={{ marginBottom: "1.35rem" }}>
              <h4 style={{ fontSize: "1rem", color: "#1e293b", marginBottom: "0.65rem", fontWeight: 700 }}>
                Recommended Action Steps:
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.55rem" }}>
                {advisory.recommended_actions.map((act, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "0.85rem 1.15rem",
                      background: "#f8faf8",
                      borderRadius: "10px",
                      border: "1px solid #e2e8f0",
                      fontSize: "0.925rem",
                      color: "#1e293b",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
                    }}
                  >
                    <CheckCircle2 size={16} color="#15803d" style={{ flexShrink: 0 }} />
                    <span>{act}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {advisory.reasoning_summary && (
            <div
              style={{
                background: "#f1f5f9",
                padding: "0.85rem 1.15rem",
                borderRadius: "10px",
                fontSize: "0.875rem",
                color: "#475569",
                marginBottom: "1.15rem",
                borderLeft: "3px solid #94a3b8",
              }}
            >
              <strong style={{ color: "#0f172a" }}>Agronomic Reasoning:</strong> {advisory.reasoning_summary}
            </div>
          )}

          <p style={{ fontSize: "0.775rem", color: "#94a3b8", fontStyle: "italic", margin: 0 }}>
            {advisory.disclaimer ||
              "Chemical and dosage recommendations follow standard ICAR-CPCRI guidelines. Consult local extension officers before application."}
          </p>
        </div>
      ) : (
        <div
          className="card"
          style={{
            textAlign: "center",
            padding: "4.5rem 2rem",
            background: "linear-gradient(135deg, #ffffff 0%, #fbfdfb 100%)",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "1rem",
              borderRadius: "16px",
              background: "#f0fdf4",
              border: "1px solid #bbf7d0",
              marginBottom: "1rem",
              boxShadow: "0 4px 12px rgba(34, 197, 94, 0.15)",
            }}
          >
            <Sparkles size={32} color="#15803d" />
          </div>
          <h3 style={{ fontSize: "1.3rem", color: "#0a1a0f", margin: "0 0 0.5rem 0", fontWeight: 700 }}>
            Ready to Synthesize Fresh Farm Advisory
          </h3>
          <p style={{ color: "#64748b", maxWidth: "480px", margin: "0 auto 1.5rem auto", fontSize: "0.925rem" }}>
            Click the button above to run Gemini 2.0 Flash agronomic intelligence on current leaf pathology, weather
            sensors, and market trends.
          </p>
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={loading || !selectedCropBlock}
          >
            <Sparkles size={16} />
            Generate Advisory Now
          </button>
        </div>
      )}
    </div>
  );
};
