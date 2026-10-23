import React, { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../api/auth";
import { farmerApi } from "../api/farmer";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem("areca_token"));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("areca_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch farmer profile whenever token is valid
  useEffect(() => {
    const loadProfile = async () => {
      if (token) {
        try {
          const prof = await farmerApi.getProfile();
          setProfile(prof);
        } catch (err) {
          console.warn("Farmer profile not found or expired:", err.message);
          setProfile(null);
        }
      } else {
        setProfile(null);
      }
      setLoading(false);
    };
    loadProfile();
  }, [token]);

  const login = async (username, password) => {
    const data = await authApi.login(username, password);
    const accessToken = data.access_token;
    localStorage.setItem("areca_token", accessToken);
    setToken(accessToken);

    // Fetch user profile immediately
    try {
      const prof = await farmerApi.getProfile();
      setProfile(prof);
      const userInfo = {
        id: prof.user_id,
        farmer_id: prof.id,
        username,
        full_name: prof.full_name,
        role: "farmer",
      };
      localStorage.setItem("areca_user", JSON.stringify(userInfo));
      setUser(userInfo);
    } catch (err) {
      // If user has no profile yet, set basic user
      const userInfo = { username, role: "farmer" };
      localStorage.setItem("areca_user", JSON.stringify(userInfo));
      setUser(userInfo);
    }
  };

  const register = async ({
    username,
    phone,
    password,
    full_name,
    state = "Karnataka",
    district = "Shivamogga",
    taluk = "Thirthahalli",
    preferred_mandi = "Shivamogga APMC",
  }) => {
    // 1. Call backend register (creates User + FarmerProfile and returns TokenResponse)
    const data = await authApi.register({
      username,
      phone,
      password,
      full_name,
      state,
      district,
      taluk,
      village: taluk,
      preferred_mandi,
      preferred_language: "en",
    });

    const accessToken = data.access_token;
    localStorage.setItem("areca_token", accessToken);
    setToken(accessToken);

    // 2. Fetch full profile and update state
    try {
      const prof = await farmerApi.getProfile();
      setProfile(prof);
      const userInfo = {
        id: prof.user_id,
        farmer_id: prof.id,
        username,
        full_name: prof.full_name,
        role: "farmer",
      };
      localStorage.setItem("areca_user", JSON.stringify(userInfo));
      setUser(userInfo);
    } catch (err) {
      const userInfo = { username, full_name, role: "farmer" };
      localStorage.setItem("areca_user", JSON.stringify(userInfo));
      setUser(userInfo);
    }
  };

  const logout = () => {
    localStorage.removeItem("areca_token");
    localStorage.removeItem("areca_user");
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    try {
      const prof = await farmerApi.getProfile();
      setProfile(prof);
      return prof;
    } catch (err) {
      console.warn("Could not refresh profile:", err);
      return null;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        profile,
        loading,
        login,
        register,
        logout,
        refreshProfile,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
