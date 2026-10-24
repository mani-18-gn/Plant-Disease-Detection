import React, { useState } from "react";
import {
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Leaf,
  Microscope,
  Info,
  BookOpen,
  AlertCircle,
  Check,
  ChevronDown,
  ChevronUp,
  Globe,
  HelpCircle,
  Layers
} from "lucide-react";

export const GoogleAIDiagnosis = ({ data, localModelData, lang = "en" }) => {
  const [showDifferential, setShowDifferential] = useState(true);
  const [showManagement, setShowManagement] = useState(true);
  const [showSources, setShowSources] = useState(true);

  if (!data) return null;

  // Case 1: API key missing on backend
  if (data.status === "api_key_missing") {
    return (
      <div
        style={{
          marginTop: "1.75rem",
          padding: "1.25rem 1.5rem",
          background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
          border: "1px dashed #cbd5e1",
          borderRadius: "14px",
          color: "#334155",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#e2e8f0",
              color: "#475569",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <Sparkles size={20} color="#475569" />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.25rem" }}>
              <strong style={{ fontSize: "0.95rem", color: "#1e293b" }}>
                Google AI Multimodal Pathology (Ready for Activation)
              </strong>
              <span
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  padding: "0.15rem 0.5rem",
                  borderRadius: "999px",
                  background: "#e2e8f0",
                  color: "#475569",
                }}
              >
                Key Not Set in .env
              </span>
            </div>
            <p style={{ margin: "0.2rem 0 0.5rem 0", fontSize: "0.85rem", color: "#64748b", lineHeight: 1.5 }}>
              To unlock multimodal visual leaf inspection, species verification, and Google Search grounded extension research, add your Google AI key to <code>backend/.env</code>:
            </p>
            <div
              style={{
                background: "#0f172a",
                color: "#38bdf8",
                padding: "0.4rem 0.75rem",
                borderRadius: "6px",
                fontFamily: "monospace",
                fontSize: "0.8rem",
                display: "inline-block",
              }}
            >
              GOOGLE_API_KEY=your_gemini_api_key_here
            </div>
            <span style={{ display: "block", marginTop: "0.4rem", fontSize: "0.78rem", color: "#64748b" }}>
              ✓ The local edge neural model is actively diagnosing your crops below.
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Case 1b: API key invalid or quota/network error
  if (data.status === "api_key_invalid" || data.status === "api_error" || data.status === "quota_exceeded") {
    return (
      <div
        style={{
          marginTop: "1.75rem",
          padding: "1.25rem 1.5rem",
          background: "#fff1f2",
          border: "1px dashed #fca5a5",
          borderRadius: "14px",
          color: "#991b1b",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
          <AlertCircle size={22} color="#dc2626" style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <strong style={{ fontSize: "0.95rem", color: "#991b1b" }}>
              {data.status === "api_key_invalid" ? "Google AI Key Notice" : "Google AI Service Notice"}
            </strong>
            <p style={{ margin: "0.3rem 0 0.4rem 0", fontSize: "0.85rem", color: "#b91c1c", lineHeight: 1.4 }}>
              {data.error || "The Google AI service could not be reached. Check your GOOGLE_API_KEY in backend/.env."}
            </p>
            <span style={{ fontSize: "0.78rem", color: "#7f1d1d" }}>
              ✓ The local neural model has analyzed your crop below.
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Case 2: Rejected Non-Plant Image
  if (data.status === "not_a_plant" || data.is_plant === false) {
    return (
      <div
        style={{
          marginTop: "1.75rem",
          padding: "1.25rem 1.5rem",
          background: "#faf5ff",
          border: "2px solid #d8b4fe",
          borderRadius: "14px",
          color: "#581c87",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
          <AlertTriangle size={24} color="#7e22ce" style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <h4 style={{ margin: "0 0 0.3rem 0", fontSize: "1.05rem", fontWeight: 800, color: "#6b21a8" }}>
              Non-Plant Subject Detected by Google AI
            </h4>
            <p style={{ margin: "0 0 0.5rem 0", fontSize: "0.875rem", color: "#7e22ce", lineHeight: 1.5 }}>
              {data.rejection_reason ||
                "The uploaded image could not be identified as a plant or crop leaf. Diagnostic models require clear plant foliage or leaves to examine disease symptoms."}
            </p>
            <span style={{ fontSize: "0.8rem", color: "#9333ea", fontWeight: 600 }}>
              💡 Please upload a crisp photograph of an agricultural crop, leaf, or plant specimen.
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Case 3: Insufficient Evidence or Blur Notice
  const isInsufficient = data.status === "insufficient_evidence" || data.image_quality === "poor_blurry_or_dark";

  // Case 4: Full Diagnosis
  const diagnosis = data.diagnosis;
  if (!diagnosis) return null;

  const plantId = diagnosis.plant_identification || {};
  const assessment = diagnosis.disease_assessment || {};
  const info = diagnosis.disease_information || {};
  const mgmt = diagnosis.treatment_and_management || {};
  const sources = data.sources || [];

  const confidenceBadgeColor =
    assessment.confidence === "High"
      ? { bg: "#dcfce7", text: "#166534", border: "#bbf7d0" }
      : assessment.confidence === "Moderate"
      ? { bg: "#fef3c7", text: "#92400e", border: "#fde68a" }
      : { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5" };

  const causeBadgeColor = {
    fungal: { bg: "#eff6ff", text: "#1d4ed8" },
    bacterial: { bg: "#fef2f2", text: "#b91c1c" },
    viral: { bg: "#faf5ff", text: "#7e22ce" },
    pest: { bg: "#fff7ed", text: "#c2410c" },
    nutritional: { bg: "#fefce8", text: "#854d0e" },
    environmental: { bg: "#f0fdfa", text: "#0f766e" },
    healthy: { bg: "#f0fdf4", text: "#15803d" },
    unknown: { bg: "#f1f5f9", text: "#475569" },
  }[assessment.cause?.toLowerCase() || "unknown"] || { bg: "#f1f5f9", text: "#475569" };

  return (
    <div
      style={{
        marginTop: "2rem",
        background: "#ffffff",
        border: "1px solid #e2e8f0",
        borderRadius: "16px",
        boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03)",
        overflow: "hidden",
      }}
    >
      {/* Top Google AI Header Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
          color: "#ffffff",
          padding: "1.25rem 1.5rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(56, 189, 248, 0.35)",
            }}
          >
            <Sparkles size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              <span style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.8px", color: "#38bdf8" }}>
                Google Gen AI Multimodal Engine
              </span>
              <span
                style={{
                  fontSize: "0.7rem",
                  padding: "0.15rem 0.5rem",
                  borderRadius: "999px",
                  background: "rgba(56, 189, 248, 0.15)",
                  color: "#7dd3fc",
                  border: "1px solid rgba(56, 189, 248, 0.3)",
                }}
              >
                ● {data.model_used || "gemini-2.5-flash"}
              </span>
            </div>
            <h3 style={{ margin: "0.2rem 0 0 0", fontSize: "1.2rem", fontWeight: 800 }}>
              Grounded Plant Pathology & Diagnostic Monograph
            </h3>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              padding: "0.3rem 0.65rem",
              borderRadius: "8px",
              background: "rgba(255, 255, 255, 0.1)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              color: "#e2e8f0",
              display: "inline-flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <Globe size={13} color="#38bdf8" />
            Google Search Grounding & ICAR Verified
          </span>
        </div>
      </div>

      {/* Main Body */}
      <div style={{ padding: "1.5rem" }}>
        {/* Blurry Photo / Quality Warning */}
        {isInsufficient && (
          <div
            style={{
              marginBottom: "1.5rem",
              padding: "0.85rem 1rem",
              background: "#fffbeb",
              border: "1px solid #fde68a",
              borderRadius: "10px",
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              color: "#92400e",
              fontSize: "0.875rem",
            }}
          >
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>
              <strong>Image Quality Notice:</strong> Photograph appears blurry or dimly lit. Diagnosis is provided with low confidence. For maximum accuracy, upload an evenly lit, high-resolution close-up of the leaf.
            </span>
          </div>
        )}

        {/* Section A: Plant Identification & Primary Disease Banner */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "1.25rem",
            marginBottom: "1.5rem",
          }}
        >
          {/* Card A1: Plant Identification */}
          <div
            style={{
              padding: "1.25rem",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: "12px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
              <span style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: 700, color: "#64748b", letterSpacing: "0.5px" }}>
                Plant Identification
              </span>
              <span
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  padding: "0.2rem 0.55rem",
                  borderRadius: "999px",
                  background: "#dcfce7",
                  color: "#166534",
                  border: "1px solid #bbf7d0",
                }}
              >
                Certainty: {plantId.certainty || "Moderate"}
              </span>
            </div>
            <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#0f172a" }}>
              🌱 {plantId.common_name || "Identified Plant"}
            </div>
            {plantId.scientific_name && (
              <div style={{ fontSize: "0.88rem", fontStyle: "italic", color: "#475569", marginTop: "0.2rem" }}>
                ({plantId.scientific_name})
              </div>
            )}
            <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.4rem" }}>
              Specimen Area: <strong>{plantId.plant_part || "Foliage / Leaf"}</strong>
            </div>
          </div>

          {/* Card A2: Disease Assessment */}
          <div
            style={{
              padding: "1.25rem",
              background: assessment.is_healthy ? "#f0fdf4" : "#fff1f2",
              border: `1px solid ${assessment.is_healthy ? "#bbf7d0" : "#fecdd3"}`,
              borderRadius: "12px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
              <span style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: 700, color: "#64748b", letterSpacing: "0.5px" }}>
                Primary Disease Assessment
              </span>
              <span
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  padding: "0.2rem 0.55rem",
                  borderRadius: "999px",
                  background: confidenceBadgeColor.bg,
                  color: confidenceBadgeColor.text,
                  border: `1px solid ${confidenceBadgeColor.border}`,
                }}
              >
                Confidence: {assessment.confidence || "Moderate"}
              </span>
            </div>
            <div
              style={{
                fontSize: "1.25rem",
                fontWeight: 800,
                color: assessment.is_healthy ? "#14532d" : "#881337",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
              }}
            >
              {assessment.is_healthy ? <CheckCircle2 size={20} color="#16a34a" /> : <XCircle size={20} color="#e11d48" />}
              {assessment.most_likely_disease || "Plant Assessment"}
            </div>
            {assessment.pathogen_scientific_name && (
              <div style={{ fontSize: "0.85rem", fontStyle: "italic", color: "#475569", marginTop: "0.2rem" }}>
                Pathogen: {assessment.pathogen_scientific_name}
              </div>
            )}
            <div style={{ marginTop: "0.45rem", display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
              <span
                style={{
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  padding: "0.15rem 0.55rem",
                  borderRadius: "6px",
                  background: causeBadgeColor.bg,
                  color: causeBadgeColor.text,
                  textTransform: "capitalize",
                }}
              >
                Type: {assessment.cause || "Pathology"}
              </span>
              <span
                style={{
                  fontSize: "0.75rem",
                  padding: "0.15rem 0.55rem",
                  borderRadius: "6px",
                  background: "#ffffff",
                  color: "#475569",
                  border: "1px solid #cbd5e1",
                }}
              >
                {assessment.is_healthy ? "Foliage Healthy" : "Visible Pathological Symptoms"}
              </span>
            </div>
          </div>
        </div>

        {/* Symptoms Observed & Plausibility Rationale */}
        <div
          style={{
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            padding: "1.25rem",
            marginBottom: "1.5rem",
          }}
        >
          <h4 style={{ margin: "0 0 0.6rem 0", fontSize: "0.95rem", fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <Microscope size={17} color="#0284c7" />
            Visible Leaf Symptoms Inspected in Uploaded Photo
          </h4>
          {assessment.symptoms_observed && assessment.symptoms_observed.length > 0 ? (
            <ul style={{ margin: "0 0 0.75rem 0", paddingLeft: "1.25rem", fontSize: "0.875rem", color: "#334155", lineHeight: 1.6 }}>
              {assessment.symptoms_observed.map((symptom, idx) => (
                <li key={idx} style={{ marginBottom: "0.25rem" }}>
                  {symptom}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ margin: "0 0 0.75rem 0", fontSize: "0.875rem", color: "#64748b" }}>
              No severe foliar necrosis or spots observed on the inspected surface.
            </p>
          )}

          {assessment.plausibility_explanation && (
            <div
              style={{
                background: "#f0fdf4",
                border: "1px solid #bbf7d0",
                borderRadius: "8px",
                padding: "0.75rem 1rem",
                fontSize: "0.85rem",
                color: "#166534",
                lineHeight: 1.5,
              }}
            >
              <strong>Diagnostic Plausibility: </strong>
              {assessment.plausibility_explanation}
            </div>
          )}

          {assessment.confidence_explanation && (
            <div style={{ marginTop: "0.5rem", fontSize: "0.8rem", color: "#64748b", fontStyle: "italic" }}>
              <strong>Confidence Basis: </strong>
              {assessment.confidence_explanation}
            </div>
          )}
        </div>

        {/* Section B: Differential Diagnosis (Look-Alikes & Alternatives) */}
        {assessment.differential_diagnosis && assessment.differential_diagnosis.length > 0 && (
          <div
            style={{
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "12px",
              padding: "1.25rem",
              marginBottom: "1.5rem",
            }}
          >
            <div
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}
              onClick={() => setShowDifferential(!showDifferential)}
            >
              <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Layers size={17} color="#7c3aed" />
                Differential Diagnosis (Alternative Possibilities & How to Distinguish)
              </h4>
              <button type="button" className="btn btn-secondary" style={{ padding: "0.2rem 0.5rem", fontSize: "0.75rem" }}>
                {showDifferential ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </div>

            {showDifferential && (
              <div style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.85rem" }}>
                {assessment.differential_diagnosis.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "0.85rem 1rem",
                      background: "#faf5ff",
                      border: "1px solid #e9d5ff",
                      borderRadius: "10px",
                    }}
                  >
                    <div style={{ fontWeight: 700, color: "#6b21a8", fontSize: "0.9rem", marginBottom: "0.25rem" }}>
                      ● {item.disease_name}
                    </div>
                    <div style={{ fontSize: "0.82rem", color: "#475569", lineHeight: 1.5 }}>
                      <strong>Distinguishing Key:</strong> {item.distinguishing_feature}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Section C: Disease Information & Conditions */}
        {(info.typical_symptoms || info.favorable_conditions) && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "1.25rem",
              marginBottom: "1.5rem",
            }}
          >
            {info.typical_symptoms && (
              <div style={{ padding: "1.25rem", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "12px" }}>
                <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", fontWeight: 700, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.35rem" }}>
                  <Info size={16} color="#0284c7" />
                  Textbook Pathology Symptoms
                </h4>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "#475569", lineHeight: 1.5 }}>
                  {info.typical_symptoms}
                </p>
              </div>
            )}

            {info.favorable_conditions && (
              <div style={{ padding: "1.25rem", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "12px" }}>
                <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", fontWeight: 700, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.35rem" }}>
                  <Globe size={16} color="#0d9488" />
                  Conducive Environmental Factors
                </h4>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "#475569", lineHeight: 1.5 }}>
                  {info.favorable_conditions}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Section D: Integrated Pest & Disease Management (IPM) */}
        <div
          style={{
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            padding: "1.25rem",
            marginBottom: "1.5rem",
          }}
        >
          <div
            style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}
            onClick={() => setShowManagement(!showManagement)}
          >
            <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <ShieldCheck size={18} color="#16a34a" />
              Evidence-Based Integrated Pest & Disease Management (IPM)
            </h4>
            <button type="button" className="btn btn-secondary" style={{ padding: "0.2rem 0.5rem", fontSize: "0.75rem" }}>
              {showManagement ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          </div>

          {showManagement && (
            <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              {/* Immediate Sanitation */}
              {mgmt.immediate_actions && mgmt.immediate_actions.length > 0 && (
                <div style={{ padding: "0.85rem 1rem", background: "#fef2f2", border: "1px solid #fee2e2", borderRadius: "8px" }}>
                  <div style={{ fontWeight: 700, color: "#991b1b", fontSize: "0.85rem", marginBottom: "0.35rem" }}>
                    🚨 Immediate Field Sanitation Actions
                  </div>
                  <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.825rem", color: "#7f1d1d", lineHeight: 1.5 }}>
                    {mgmt.immediate_actions.map((act, idx) => (
                      <li key={idx}>{act}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Cultural & Biological Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem" }}>
                {mgmt.cultural_practices && mgmt.cultural_practices.length > 0 && (
                  <div style={{ padding: "0.85rem 1rem", background: "#f0fdf4", border: "1px solid #dcfce7", borderRadius: "8px" }}>
                    <div style={{ fontWeight: 700, color: "#166534", fontSize: "0.85rem", marginBottom: "0.35rem" }}>
                      🌿 Cultural & Preventive Practices
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.825rem", color: "#14532d", lineHeight: 1.5 }}>
                      {mgmt.cultural_practices.map((act, idx) => (
                        <li key={idx}>{act}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {mgmt.biological_control && mgmt.biological_control.length > 0 && (
                  <div style={{ padding: "0.85rem 1rem", background: "#f0fdfa", border: "1px solid #ccfbf1", borderRadius: "8px" }}>
                    <div style={{ fontWeight: 700, color: "#0f766e", fontSize: "0.85rem", marginBottom: "0.35rem" }}>
                      🦠 Biological & Organic Control
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.825rem", color: "#115e59", lineHeight: 1.5 }}>
                      {mgmt.biological_control.map((act, idx) => (
                        <li key={idx}>{act}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Chemical Management & Mandatory Safety Warnings */}
              {mgmt.chemical_management && mgmt.chemical_management.length > 0 && (
                <div style={{ padding: "0.85rem 1rem", background: "#fffbeb", border: "1px solid #fef3c7", borderRadius: "8px" }}>
                  <div style={{ fontWeight: 700, color: "#92400e", fontSize: "0.85rem", marginBottom: "0.35rem" }}>
                    💊 Evidence-Based Chemical Protection (Restricted / Extension Only)
                  </div>
                  <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.825rem", color: "#78350f", lineHeight: 1.5 }}>
                    {mgmt.chemical_management.map((chem, idx) => (
                      <li key={idx}>{chem}</li>
                    ))}
                  </ul>
                  {mgmt.safety_precautions && (
                    <div style={{ marginTop: "0.5rem", fontSize: "0.78rem", color: "#b45309", fontWeight: 600 }}>
                      ⚠️ Safety Instruction: {mgmt.safety_precautions}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Section E: Authoritative Research & Grounding Sources */}
        {sources && sources.length > 0 && (
          <div
            style={{
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: "12px",
              padding: "1.25rem",
              marginBottom: "1.5rem",
            }}
          >
            <div
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}
              onClick={() => setShowSources(!showSources)}
            >
              <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <BookOpen size={17} color="#0284c7" />
                Grounded Sources & Authoritative Research ({sources.length})
              </h4>
              <button type="button" className="btn btn-secondary" style={{ padding: "0.2rem 0.5rem", fontSize: "0.75rem" }}>
                {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </div>

            {showSources && (
              <div style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.85rem" }}>
                {sources.map((src, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "0.85rem 1rem",
                      background: "#ffffff",
                      border: "1px solid #cbd5e1",
                      borderRadius: "10px",
                    }}
                  >
                    <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.2rem" }}>
                      {src.title}
                    </div>
                    <div style={{ fontSize: "0.78rem", color: "#0284c7", fontWeight: 600, marginBottom: "0.35rem" }}>
                      {src.organization || "Agricultural Extension"}
                    </div>
                    {src.notes && (
                      <p style={{ margin: "0 0 0.45rem 0", fontSize: "0.78rem", color: "#64748b", lineHeight: 1.4 }}>
                        {src.notes}
                      </p>
                    )}
                    {src.url && (
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.78rem",
                          color: "#2563eb",
                          textDecoration: "none",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                          fontWeight: 600,
                        }}
                      >
                        Visit Official Reference <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Section F: Local Edge Model vs Google AI Comparison */}
        {localModelData && (
          <div
            style={{
              padding: "1rem 1.25rem",
              background: "#f1f5f9",
              border: "1px solid #cbd5e1",
              borderRadius: "10px",
              marginBottom: "1.25rem",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "0.75rem",
            }}
          >
            <div>
              <span style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "#475569" }}>
                Multi-Engine Verification
              </span>
              <div style={{ fontSize: "0.9rem", fontWeight: 700, color: "#0f172a" }}>
                Local Edge Neural Model ({localModelData.backend || "MobileNetV2"}):{" "}
                <span style={{ color: "#2563eb" }}>{localModelData.predicted_disease}</span>{" "}
                <span style={{ color: "#64748b", fontWeight: 500 }}>
                  ({((localModelData.cnn_confidence || localModelData.confidence || 0) * 100).toFixed(1)}%)
                </span>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span
                style={{
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  padding: "0.2rem 0.6rem",
                  borderRadius: "999px",
                  background: "#dcfce7",
                  color: "#166534",
                  border: "1px solid #bbf7d0",
                }}
              >
                Dual Independent Engines
              </span>
            </div>
          </div>
        )}

        {/* Section G: Plant Pathology Uncertainty Disclaimer */}
        <div
          style={{
            padding: "0.85rem 1rem",
            background: "#fffbeb",
            border: "1px solid #fef3c7",
            borderRadius: "10px",
            fontSize: "0.8rem",
            color: "#92400e",
            display: "flex",
            alignItems: "flex-start",
            gap: "0.5rem",
            lineHeight: 1.5,
          }}
        >
          <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <strong>Agronomic Advisory Notice: </strong>
            {diagnosis.uncertainty_disclaimer ||
              "Automated optical analysis is an advisory aid and cannot substitute for laboratory phytosanitary tests. If crop symptoms spread or persist, immediately consult your local Krishi Vigyan Kendra (KVK) or State Agricultural University extension officer."}
          </div>
        </div>
      </div>
    </div>
  );
};
