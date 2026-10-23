// Mock Data Provider for Frontend Standalone / Demo Mode
export const mockData = {
  profile: {
    id: "farmer-uuid-demo-1",
    user_id: "user-uuid-demo-1",
    full_name: "Ramesh Gowda",
    phone: "9876543210",
    state: "Karnataka",
    district: "Shivamogga",
    taluk: "Thirthahalli",
    village: "Agumbe",
    preferred_mandi: "Shivamogga APMC",
    preferred_language: "en",
  },

  farms: [
    {
      id: "farm-uuid-1",
      farmer_id: "farmer-uuid-demo-1",
      farm_name: "Sahyadri Bio-Plantation",
      total_area_acres: 12.5,
      latitude: 13.518,
      longitude: 75.244,
      irrigation_type: "drip",
      soil_type: "laterite",
      elevation_m: 650,
      active: true,
    },
  ],

  cropBlocks: [
    {
      id: "block-uuid-1",
      farm_id: "farm-uuid-1",
      block_name: "Arecanut Canopy Block A",
      crop_type: "Arecanut",
      variety: "Mangala",
      plant_count: 850,
      planted_year: 2018,
      current_stage: "fruiting",
      spacing_meters: "2.7x2.7",
    },
    {
      id: "block-uuid-2",
      farm_id: "farm-uuid-1",
      block_name: "Tomato Experimental Field",
      crop_type: "Tomato",
      variety: "Arka Rakshak",
      plant_count: 2200,
      planted_year: 2025,
      current_stage: "flowering",
      spacing_meters: "0.6x0.4",
    },
  ],

  synthesis: {
    situation_score: {
      overall_risk_score: 34,
      risk_level: "low",
      risk_factors: [
        "Optimal daytime photosynthetic solar exposure (680 W/m²)",
        "Microclimate relative humidity within safe threshold (62%)",
        "Recent 1% Bordeaux mixture spray maintained effective protection",
      ],
      suggested_immediate_action: "Maintain scheduled drip fertigation cycle and inspect fronds for early spore traces.",
    },
    diagnosis: {
      detected: false,
      disease_name: "Healthy Plant Foliage",
      scientific_name: "Areca catechu",
      confidence: 0.982,
      severity: "low",
      symptoms: ["Lush frond greening", "No necrotic margins", "Intact photosynthetic lamina"],
    },
    weather: {
      temperature_c: 26.4,
      humidity_pct: 62.0,
      rainfall_mm_24h: 0.0,
      wind_speed_kmh: 5.4,
      solar_radiation_wm2: 680,
      dew_point_c: 18.2,
      spore_germination_risk: "low",
      spray_window_status: "optimal",
    },
    market: {
      mandi_name: "Shivamogga APMC",
      commodity: "Arecanut (Rashi)",
      modal_price: 52400,
      min_price: 49800,
      max_price: 54200,
      unit: "₹ / Quintal",
      trend: "upward",
      trend_pct: "+2.4% vs last week",
    },
    advisory: {
      id: "advisory-uuid-101",
      crop_block_id: "block-uuid-1",
      urgency: "low",
      headline: "Favorable Climatic Conditions Across Canopy Block A",
      recommendations: [
        {
          action: "Soil Potassium & Boron Booster",
          timing: "Tomorrow morning (06:30 - 08:30)",
          dosage: "250g SOP + 15g Solubor per palm",
          notes: "Aids nut retention and shell hardening during fruiting stage.",
        },
        {
          action: "Preventive Koleroga Phytophthora Surveillance",
          timing: "Pre-monsoon schedule",
          dosage: "1% Neutral Bordeaux mixture spray onto bunches",
          notes: "Ensure complete coverage of fruit bunches and crown joints.",
        },
      ],
      created_at: new Date().toISOString(),
    },
  },

  notifications: [
    {
      id: "notif-1",
      channel: "in_app",
      content: "Weather Alert: Favorable spraying window detected between 06:00 - 10:00 tomorrow.",
      sent_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
      status: "sent",
    },
    {
      id: "notif-2",
      channel: "sms",
      content: "Shivamogga APMC Arecanut modal rate rose to ₹52,400/Qtl (+2.4%).",
      sent_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
      status: "sent",
    },
  ],

  sampleImages: [
    {
      id: "sample-1",
      label: "Tomato Early Blight (Alternaria solani)",
      crop: "Tomato",
      disease: "Early Blight",
      imageUrl: "https://images.unsplash.com/photo-1592417817098-8f3d6910a39a?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "sample-2",
      label: "Corn Common Rust (Puccinia sorghi)",
      crop: "Corn",
      disease: "Common Rust",
      imageUrl: "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "sample-3",
      label: "Healthy Arecanut Frond (Areca catechu)",
      crop: "Arecanut",
      disease: "Healthy",
      imageUrl: "https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?auto=format&fit=crop&w=600&q=80",
    },
  ],

  activities: [
    {
      id: "act-1",
      crop_block_id: "block-uuid-1",
      activity_type: "spraying",
      description: "Preventive Bordeaux 1% spray on palm crowns",
      logged_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    },
    {
      id: "act-2",
      crop_block_id: "block-uuid-1",
      activity_type: "irrigation",
      description: "Drip irrigation cycle 180 minutes with micro-fertigation",
      logged_at: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
    },
  ],
};

export const handleMockRequest = async (config) => {
  const url = config.url || "";
  const method = (config.method || "get").toLowerCase();

  // Auth
  if (url.includes("/api/v1/auth/login") || url.includes("/api/v1/auth/register")) {
    return {
      access_token: "mock-jwt-token-arecaagent-2026",
      token_type: "bearer",
      user: {
        id: "user-uuid-demo-1",
        username: "farmer_demo",
        role: "farmer",
      },
    };
  }

  // Profile
  if (url.includes("/api/v1/core/profile")) {
    return mockData.profile;
  }

  // Farms
  if (url.includes("/api/v1/core/farms") && !url.includes("crop-blocks")) {
    return mockData.farms;
  }

  // Crop blocks
  if (url.includes("crop-blocks")) {
    if (url.includes("/activities")) {
      return mockData.activities;
    }
    return mockData.cropBlocks;
  }

  // Coordinator synthesis
  if (url.includes("/api/v1/agents/coordinator/synthesize")) {
    return mockData.synthesis;
  }

  // Weather
  if (url.includes("/api/v1/agents/weather/current")) {
    return mockData.synthesis.weather;
  }

  // Market
  if (url.includes("/api/v1/agents/market/prices")) {
    return [mockData.synthesis.market];
  }

  // Advisory
  if (url.includes("/api/v1/agents/advisory/generate")) {
    return mockData.synthesis.advisory;
  }

  // Notifying
  if (url.includes("/api/v1/agents/notifying")) {
    return mockData.notifications;
  }

  // Vision
  if (url.includes("/api/v1/agents/vision/sample-images")) {
    return mockData.sampleImages;
  }
  if (url.includes("/api/v1/agents/vision/status")) {
    return {
      status: "online",
      model: "MobileNetV2-PlantVillage-38Classes",
      supported_crops: ["Tomato", "Potato", "Corn", "Grape", "Apple", "Arecanut"],
    };
  }
  if (url.includes("/api/v1/agents/vision/detect")) {
    return {
      detection_id: "det-mock-" + Date.now(),
      crop: "Tomato",
      disease: "Early Blight (Alternaria solani)",
      confidence: 0.965,
      severity: "moderate",
      bayesian_confidence: 0.984,
      symptoms: ["Concentric ring lesions", "Chlorotic halos", "Foliar spotting"],
      treatment_summary: "Apply copper oxychloride or Bacillus subtilis foliar spray.",
    };
  }

  return {};
};
