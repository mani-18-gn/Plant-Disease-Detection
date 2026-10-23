import React, { useState } from "react";
import { Sparkles, RefreshCw, AlertCircle, CheckCircle2, ShieldAlert } from "lucide-react";
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
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", margin: 0 }}>Agronomic Advisory Agent</h1>
          <p style={{ fontSize: "0.9rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
            Autonomous Gemini 2.0 Flash agronomic synthesis for <strong>{selectedCropBlock?.block_name || "Crop Block"}</strong>
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={loading || !selectedCropBlock}
          style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
        >
          <Sparkles size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Synthesizing with Gemini..." : "Generate New Advisory"}
        </button>
      </div>

      {error && (
        <div style={{ padding: "1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "10px", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {advisory ? (
        <div className="card" style={{ borderLeft: "4px solid #10b981" }}>
          <div className="card-header">
            <div className="card-title">
              <Sparkles size={20} color="#10b981" />
              <span>Priority: {advisory.priority?.toUpperCase()}</span>
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <span className={`badge ${getUrgencyBadgeClass(advisory.priority)}`}>
                {advisory.priority} Priority
              </span>
              <span className="badge badge-low">
                Engine: {advisory.generated_by}
              </span>
            </div>
          </div>

          <p style={{ fontSize: "1.05rem", fontWeight: 500, color: "#1e293b", marginBottom: "1.25rem" }}>
            {advisory.message}
          </p>

          {advisory.recommended_actions?.length > 0 && (
            <div style={{ marginBottom: "1.25rem" }}>
              <h4 style={{ fontSize: "0.95rem", color: "#334155", marginBottom: "0.5rem" }}>
                Recommended Action Steps:
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {advisory.recommended_actions.map((act, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "0.75rem 1rem",
                      background: "#f8fafc",
                      borderRadius: "8px",
                      border: "1px solid #e2e8f0",
                      fontSize: "0.9rem",
                      color: "#1e293b",
                    }}
                  >
                    {act}
                  </div>
                ))}
              </div>
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
        </div>
      ) : (
        <div className="card" style={{ padding: "3rem 2rem", textAlign: "center" }}>
          <Sparkles size={36} color="#10b981" style={{ margin: "0 auto 1rem auto" }} />
          <h3 style={{ fontSize: "1.1rem", color: "#1e293b", margin: 0 }}>Ready to Generate Live Agronomic Synthesis</h3>
          <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0.5rem 0 1.25rem 0" }}>
            Click "Generate New Advisory" above to synthesize Vision detection, live Open-Meteo weather telemetry, and APMC market prices.
          </p>
        </div>
      )}
    </div>
  );
};
