import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Lock, User, Phone, MapPin, Building, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const Register = () => {
  const [username, setUsername] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [district, setDistrict] = useState("Shivamogga");
  const [taluk, setTaluk] = useState("Thirthahalli");
  const [preferredMandi, setPreferredMandi] = useState("Shivamogga APMC");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({
        username,
        phone,
        password,
        full_name: fullName,
        state: "Karnataka",
        district,
        taluk,
        preferred_mandi: preferredMandi,
      });
      navigate("/");
    } catch (err) {
      setError(err.message || "Registration failed. Please check inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#0f172a", padding: "1.5rem" }}>
      <div
        className="card"
        style={{
          width: "100%",
          maxWidth: "520px",
          padding: "2.5rem",
          backgroundColor: "#ffffff",
          borderRadius: "20px",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{ display: "inline-flex", background: "linear-gradient(135deg, #10b981 0%, #059669 100%)", padding: "0.7rem", borderRadius: "14px", marginBottom: "0.5rem", boxShadow: "0 6px 14px rgba(16, 185, 129, 0.2)" }}>
            <ShieldCheck size={30} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: "1.6rem", color: "#0f172a", margin: 0, fontWeight: 800 }}>Register Farmer Account</h2>
          <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0.2rem 0 0 0" }}>PlantGuard Agricultural Intelligence Network</p>
        </div>

        {error && (
          <div style={{ padding: "0.75rem 1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "8px", fontSize: "0.85rem", marginBottom: "1rem" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                required
                placeholder="Ramesh Gowda"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-input"
                required
                placeholder="ramesh_gowda"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Mobile Phone (10 digits)</label>
              <input
                type="tel"
                className="form-input"
                required
                placeholder="9880123456"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
            <label className="form-label">Preferred APMC Mandi</label>
            <select className="form-select" value={preferredMandi} onChange={(e) => setPreferredMandi(e.target.value)}>
              <option value="Shivamogga APMC">Shivamogga APMC</option>
              <option value="Sagar APMC">Sagar APMC</option>
              <option value="Mangalore APMC">Mangalore APMC</option>
              <option value="Sirsi APMC">Sirsi APMC</option>
              <option value="Channagiri APMC">Channagiri APMC</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: "100%", padding: "0.75rem", marginTop: "0.5rem" }} disabled={loading}>
            {loading ? "Registering..." : "Create Account & Launch"}
            <ArrowRight size={18} />
          </button>
        </form>

        <p style={{ textAlign: "center", fontSize: "0.875rem", color: "#64748b", marginTop: "1.25rem", marginBottom: 0 }}>
          Already registered?{" "}
          <Link to="/login" style={{ color: "#10b981", fontWeight: 600, textDecoration: "none" }}>
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};
