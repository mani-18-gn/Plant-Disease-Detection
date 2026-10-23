import React, { useState } from "react";
import { Sprout, MapPin, Layers, CheckCircle2, ArrowRight } from "lucide-react";
import { farmerApi } from "../api/farmer";
import { useFarm } from "../context/FarmContext";

export const FarmSetupModal = () => {
  const { farms, loadFarmsAndBlocks, setShowSetupModal } = useFarm();
  const [step, setStep] = useState(farms.length === 0 ? 1 : 2);
  const [createdFarmId, setCreatedFarmId] = useState(farms.length > 0 ? farms[0].id : null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Farm Form
  const [farmName, setFarmName] = useState("Main Arecanut Estate");
  const [lat, setLat] = useState("13.9299");
  const [lon, setLon] = useState("75.5681");
  const [soilType, setSoilType] = useState("Red Laterite");
  const [irrigationType, setIrrigationType] = useState("drip");

  // Crop Block Form
  const [blockName, setBlockName] = useState("Block A - Mature Plantation");
  const [variety, setVariety] = useState("Mangala");
  const [plantingDate, setPlantingDate] = useState("2018-05-15");
  const [palmCount, setPalmCount] = useState("450");
  const [areaAcres, setAreaAcres] = useState("1.75");

  const handleCreateFarm = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const farm = await farmerApi.createFarm({
        farm_name: farmName,
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        soil_type: soilType,
        irrigation_type: irrigationType,
      });
      setCreatedFarmId(farm.id);
      setStep(2);
    } catch (err) {
      setError(err.message || "Failed to create farm");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCropBlock = async (e) => {
    e.preventDefault();
    if (!createdFarmId) return;
    setError("");
    setLoading(true);
    try {
      await farmerApi.createCropBlock(createdFarmId, {
        farm_id: createdFarmId,
        block_name: blockName,
        variety,
        planting_date: plantingDate,
        number_of_trees: parseInt(palmCount, 10) || 0,
        notes: `Area: ${areaAcres} acres`,
      });
      await loadFarmsAndBlocks();
      setShowSetupModal(false);
    } catch (err) {
      setError(err.message || "Failed to create crop block");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(15, 23, 42, 0.75)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        padding: "1rem",
      }}
    >
      <div
        className="card"
        style={{
          width: "100%",
          maxWidth: "540px",
          padding: "2rem",
          backgroundColor: "#ffffff",
          borderRadius: "16px",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
          <div style={{ background: "#d1fae5", padding: "0.5rem", borderRadius: "10px" }}>
            <Sprout size={24} color="#059669" />
          </div>
          <div>
            <h3 style={{ fontSize: "1.25rem", margin: 0 }}>Initial Plantation Setup</h3>
            <p style={{ fontSize: "0.85rem", color: "#64748b", margin: 0 }}>
              Step {step} of 2: {step === 1 ? "Register Farm Location" : "Add Initial Crop Block"}
            </p>
          </div>
        </div>

        {error && (
          <div style={{ padding: "0.75rem", background: "#fee2e2", color: "#b91c1c", borderRadius: "8px", fontSize: "0.85rem", marginBottom: "1rem" }}>
            {error}
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleCreateFarm}>
            <div className="form-group">
              <label className="form-label">Farm / Estate Name</label>
              <input
                type="text"
                className="form-input"
                required
                value={farmName}
                onChange={(e) => setFarmName(e.target.value)}
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Latitude (°N)</label>
                <input
                  type="number"
                  step="0.0001"
                  className="form-input"
                  required
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Longitude (°E)</label>
                <input
                  type="number"
                  step="0.0001"
                  className="form-input"
                  required
                  value={lon}
                  onChange={(e) => setLon(e.target.value)}
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Soil Type</label>
                <select className="form-select" value={soilType} onChange={(e) => setSoilType(e.target.value)}>
                  <option value="Red Laterite">Red Laterite</option>
                  <option value="Alluvial Loam">Alluvial Loam</option>
                  <option value="Clay Loam">Clay Loam</option>
                  <option value="Gravelly Red">Gravelly Red</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Irrigation System</label>
                <select className="form-select" value={irrigationType} onChange={(e) => setIrrigationType(e.target.value)}>
                  <option value="drip">Drip Irrigation</option>
                  <option value="sprinkler">Sprinkler System</option>
                  <option value="flood">Flood / Basin</option>
                  <option value="rainfed">Rainfed</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: "100%", marginTop: "0.5rem" }} disabled={loading}>
              {loading ? "Registering Farm..." : "Next: Add Crop Block"}
              <ArrowRight size={18} />
            </button>
          </form>
        ) : (
          <form onSubmit={handleCreateCropBlock}>
            <div className="form-group">
              <label className="form-label">Block Name</label>
              <input
                type="text"
                className="form-input"
                required
                value={blockName}
                onChange={(e) => setBlockName(e.target.value)}
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Palm Variety</label>
                <select className="form-select" value={variety} onChange={(e) => setVariety(e.target.value)}>
                  <option value="Mangala">Mangala</option>
                  <option value="Sumangala">Sumangala</option>
                  <option value="Sreemangala">Sreemangala</option>
                  <option value="Mohitnagar">Mohitnagar</option>
                  <option value="South Kanara Local">South Kanara Local</option>
                  <option value="Thirthahalli Local">Thirthahalli Local</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Planting Date</label>
                <input
                  type="date"
                  className="form-input"
                  required
                  value={plantingDate}
                  onChange={(e) => setPlantingDate(e.target.value)}
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Number of Palms</label>
                <input
                  type="number"
                  className="form-input"
                  required
                  value={palmCount}
                  onChange={(e) => setPalmCount(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Area (Acres)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  required
                  value={areaAcres}
                  onChange={(e) => setAreaAcres(e.target.value)}
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: "100%", marginTop: "0.5rem" }} disabled={loading}>
              {loading ? "Completing Setup..." : "Complete Setup & Launch Dashboard"}
              <CheckCircle2 size={18} />
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
