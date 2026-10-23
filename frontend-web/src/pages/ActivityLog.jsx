import React, { useState, useEffect } from "react";
import { ClipboardList, Plus, CheckCircle2 } from "lucide-react";
import { activityApi } from "../api/activity";
import { useFarm } from "../context/FarmContext";

export const ActivityLog = () => {
  const { selectedCropBlock } = useFarm();
  const [activities, setActivities] = useState([]);
  const [activityType, setActivityType] = useState("SPRAYING");
  const [activityDate, setActivityDate] = useState(new Date().toISOString().split("T")[0]);
  const [notes, setNotes] = useState("");
  const [chemicalName, setChemicalName] = useState("1% Bordeaux mixture");
  const [loading, setLoading] = useState(false);

  const fetchActivities = async () => {
    if (!selectedCropBlock?.id) return;
    try {
      const list = await activityApi.listActivities(selectedCropBlock.id);
      setActivities(list);
    } catch (err) {
      console.warn("Activities fetch failed:", err.message);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, [selectedCropBlock]);

  const handleLog = async (e) => {
    e.preventDefault();
    if (!selectedCropBlock) return;
    setLoading(true);
    try {
      await activityApi.logActivity({
        crop_block_id: selectedCropBlock.id,
        activity_type: activityType,
        activity_date: activityDate,
        notes,
        chemical_name: activityType === "SPRAYING" || activityType === "FERTILIZER" ? chemicalName : null,
      });
      setNotes("");
      await fetchActivities();
    } catch (err) {
      alert("Failed to log activity: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.75rem", margin: 0 }}>Farm Activity & Agrochemical Log</h1>
        <p style={{ fontSize: "0.9rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
          Track spraying, fertilization, and irrigation history for advisory context
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Log New Activity</h3>
          <form onSubmit={handleLog}>
            <div className="form-group">
              <label className="form-label">Activity Type</label>
              <select className="form-select" value={activityType} onChange={(e) => setActivityType(e.target.value)}>
                <option value="SPRAYING">Spraying (Fungicide / Pesticide)</option>
                <option value="FERTILIZER">Fertilizer Application</option>
                <option value="IRRIGATION">Irrigation</option>
                <option value="HARVEST">Harvest</option>
                <option value="PRUNING">Pruning / Sanitation</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Date</label>
              <input type="date" className="form-input" required value={activityDate} onChange={(e) => setActivityDate(e.target.value)} />
            </div>

            {(activityType === "SPRAYING" || activityType === "FERTILIZER") && (
              <div className="form-group">
                <label className="form-label">Chemical / Fertilizer Name</label>
                <input type="text" className="form-input" value={chemicalName} onChange={(e) => setChemicalName(e.target.value)} />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Notes</label>
              <input type="text" className="form-input" placeholder="e.g. Applied foliar spray on 450 palms" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              <Plus size={16} />
              {loading ? "Recording..." : "Log Activity"}
            </button>
          </form>
        </div>

        <div className="card">
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Recent Activity History</h3>
          <div style={{ maxHeight: "360px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {activities.length === 0 ? (
              <p style={{ color: "#94a3b8", textAlign: "center", padding: "2rem" }}>No activities recorded yet.</p>
            ) : (
              activities.map((a) => (
                <div key={a.id} style={{ padding: "0.75rem", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "#64748b", marginBottom: "0.2rem" }}>
                    <strong style={{ color: "#1e293b" }}>{a.activity_type}</strong>
                    <span>{a.activity_date}</span>
                  </div>
                  {a.chemical_name && <p style={{ fontSize: "0.85rem", color: "#059669", margin: "0 0 0.2rem 0" }}>{a.chemical_name}</p>}
                  {a.notes && <p style={{ fontSize: "0.8rem", color: "#475569", margin: 0 }}>{a.notes}</p>}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
