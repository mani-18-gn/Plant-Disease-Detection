import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Leaf, Lock, User, ArrowRight, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setUsername("farmer_demo");
    setPassword("password123");
    setError("");
    setLoading(true);
    try {
      await login("farmer_demo", "password123");
      navigate("/");
    } catch (err) {
      setError(err.message || "Failed to login with demo account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#0f172a", padding: "1rem" }}>
      <div
        className="card"
        style={{
          width: "100%",
          maxWidth: "440px",
          padding: "2.5rem",
          backgroundColor: "#ffffff",
          borderRadius: "20px",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
        }}
      >
        {/* Brand */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{ display: "inline-flex", background: "linear-gradient(135deg, #10b981 0%, #059669 100%)", padding: "0.75rem", borderRadius: "14px", marginBottom: "0.75rem" }}>
            <Leaf size={32} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: "1.75rem", color: "#0f172a", margin: "0 0 0.25rem 0" }}>ArecaAgent</h2>
          <p style={{ fontSize: "0.9rem", color: "#64748b", margin: 0 }}>Autonomous Multi-Agent Farm Advisory</p>
        </div>

        {error && (
          <div style={{ padding: "0.75rem 1rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "8px", fontSize: "0.875rem", marginBottom: "1.25rem" }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <div style={{ position: "relative" }}>
              <User size={18} color="#94a3b8" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <input
                type="text"
                className="form-input"
                style={{ paddingLeft: "2.5rem" }}
                required
                placeholder="e.g. farmer_demo"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: "relative" }}>
              <Lock size={18} color="#94a3b8" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
              <input
                type="password"
                className="form-input"
                style={{ paddingLeft: "2.5rem" }}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: "100%", padding: "0.75rem", marginTop: "0.5rem" }} disabled={loading}>
            {loading ? "Signing in..." : "Sign In to Farm Dashboard"}
            <ArrowRight size={18} />
          </button>
        </form>

        {/* Demo Quick Fill */}
        <div style={{ marginTop: "1.25rem", paddingTop: "1.25rem", borderTop: "1px solid #f1f5f9", textAlign: "center" }}>
          <button
            type="button"
            onClick={handleDemoLogin}
            className="btn btn-secondary"
            style={{ width: "100%", fontSize: "0.85rem", gap: "0.4rem" }}
            disabled={loading}
          >
            <Sparkles size={16} color="#059669" />
            Quick Demo Login (farmer_demo)
          </button>
        </div>

        <p style={{ textAlign: "center", fontSize: "0.875rem", color: "#64748b", marginTop: "1.5rem", marginBottom: 0 }}>
          New plantation?{" "}
          <Link to="/register" style={{ color: "#10b981", fontWeight: 600, textDecoration: "none" }}>
            Register New Farmer
          </Link>
        </p>
      </div>
    </div>
  );
};
