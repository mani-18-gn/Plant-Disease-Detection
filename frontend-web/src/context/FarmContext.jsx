import React, { createContext, useContext, useState, useEffect } from "react";
import { farmerApi } from "../api/farmer";
import { useAuth } from "./AuthContext";

const FarmContext = createContext(null);

export const FarmProvider = ({ children }) => {
  const { isAuthenticated, profile } = useAuth();
  const [farms, setFarms] = useState([]);
  const [cropBlocks, setCropBlocks] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [selectedCropBlock, setSelectedCropBlock] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSetupModal, setShowSetupModal] = useState(false);

  const loadFarmsAndBlocks = async () => {
    if (!isAuthenticated || !profile) return;
    setLoading(true);
    try {
      const farmsList = await farmerApi.listFarms();
      setFarms(farmsList);

      if (farmsList.length === 0) {
        setShowSetupModal(true);
        setCropBlocks([]);
        setSelectedFarm(null);
        setSelectedCropBlock(null);
        setLoading(false);
        return;
      }

      // Pick first farm or retain selected
      const currentFarm = selectedFarm && farmsList.find((f) => f.id === selectedFarm.id)
        ? selectedFarm
        : farmsList[0];
      setSelectedFarm(currentFarm);

      // Load crop blocks for current farm
      const blocks = await farmerApi.listCropBlocks(currentFarm.id);
      setCropBlocks(blocks);

      if (blocks.length === 0) {
        setShowSetupModal(true);
        setSelectedCropBlock(null);
      } else {
        setShowSetupModal(false);
        const currentBlock = selectedCropBlock && blocks.find((b) => b.id === selectedCropBlock.id)
          ? selectedCropBlock
          : blocks[0];
        setSelectedCropBlock(currentBlock);
      }
    } catch (err) {
      console.warn("Failed to load farms/blocks:", err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && profile) {
      loadFarmsAndBlocks();
    } else {
      setFarms([]);
      setCropBlocks([]);
      setSelectedFarm(null);
      setSelectedCropBlock(null);
    }
  }, [isAuthenticated, profile]);

  const selectCropBlockById = (blockId) => {
    const found = cropBlocks.find((b) => b.id === blockId);
    if (found) {
      setSelectedCropBlock(found);
    }
  };

  const selectFarmById = async (farmId) => {
    const found = farms.find((f) => f.id === farmId);
    if (found) {
      setSelectedFarm(found);
      const blocks = await farmerApi.listCropBlocks(found.id);
      setCropBlocks(blocks);
      if (blocks.length > 0) {
        setSelectedCropBlock(blocks[0]);
      } else {
        setSelectedCropBlock(null);
        setShowSetupModal(true);
      }
    }
  };

  return (
    <FarmContext.Provider
      value={{
        farms,
        cropBlocks,
        selectedFarm,
        selectedCropBlock,
        loading,
        showSetupModal,
        setShowSetupModal,
        loadFarmsAndBlocks,
        selectCropBlockById,
        selectFarmById,
        setSelectedCropBlock,
      }}
    >
      {children}
    </FarmContext.Provider>
  );
};

export const useFarm = () => {
  const context = useContext(FarmContext);
  if (!context) {
    throw new Error("useFarm must be used within a FarmProvider");
  }
  return context;
};
