import React, { useState, useEffect } from "react";
import { User, MapPin, Building, Phone, CheckCircle2, Save } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { farmerApi } from "../api/farmer";

export const FarmerProfile = () => {
  const { profile, refreshProfile } = useAuth();
  const [fullName, setFullName] = useState("");
  const [district, setDistrict] = useState("Shivamogga");
  const [taluk, setTaluk] = useState("Thirthahalli");
  const [preferredMandi, setPreferredMandi] = useState("Shivamogga APMC");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setDistrict(profile.district || "Shivamogga");
      setTaluk(profile.taluk || "Thirthahalli");
      setPreferredMandi(profile.preferred_mandi || "Shivamogga APMC");
    }
  }, [profile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);
    try {
      await farmerApi.updateProfile({
        full_name: fullName,
        state: "Karnataka",
        district,
        taluk,
        preferred_mandi: preferredMandi,
      });
      await refreshProfile();
      setSuccess(true);
    } catch (err) {
      setError(err.message || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "720px", margin: "0 auto" }}>
      <div style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.75rem", margin: 0 }}>Farmer Profile & Preferences</h1>
        <p style={{ fontSize: "0.9rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
          Manage your regional settings and APMC mandi market preferences
        </p>
      </div>

      <div className="card">
        {success && (
          <div style={{ padding: "0.75rem 1rem", background: "#d1fae5", color: "#047857", borderRadius: "8px", fontSize: "0.875rem", marginBottom: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <CheckCircle2 size={16} />
            <span>Profile settings updated successfully!</span>
          </div>
        )}

        {error && (
          <div style={{ padding: "0.75rem 1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "8px", fontSize: "0.875rem", marginBottom: "1.25rem" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div style={{ position: "relative" }}>
              <User size={18} color="#94a3b8" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <input
                type="text"
                className="form-input"
                style={{ paddingLeft: "2.5rem" }}
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">District (Karnataka)</label>
              <select className="form-select" value={district} onChange={(e) => setDistrict(e.target.value)}>
                <option value="Shivamogga">Shivamogga</option>
                <option value="Chikkamagaluru">Chikkamagaluru</option>
                <option value="Dakshina Kannada">Dakshina Kannada</option>
                <option value="Uttara Kannada">Uttara Kannada</option>
                <option value="Udupi">Udupi</option>
                <option value="Davanagere">Davanagere</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Taluk</label>
              <input
                type="text"
                className="form-input"
                required
                value={taluk}
                onChange={(e) => setTaluk(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Preferred APMC Mandi for Price Forecasts</label>
            <div style={{ position: "relative" }}>
              <Building size={18} color="#94a3b8" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <select
                className="form-select"
                style={{ paddingLeft: "2.5rem" }}
                value={preferredMandi}
                onChange={(e) => setPreferredMandi(e.target.value)}
              >
                <option value="Shivamogga APMC">Shivamogga APMC</option>
                <option value="Sagar APMC">Sagar APMC</option>
                <option value="Mangalore APMC">Mangalore APMC</option>
                <option value="Sirsi APMC">Sirsi APMC</option>
                <option value="Channagiri APMC">Channagiri APMC</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ marginTop: "0.5rem" }} disabled={loading}>
            <Save size={16} />
            {loading ? "Saving Changes..." : "Save Preferences"}
          </button>
        </form>
      </div>
    </div>
  );
};
