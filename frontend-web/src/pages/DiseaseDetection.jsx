import React, { useState, useRef, useEffect } from "react";
import {
  Camera,
  Upload,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Leaf,
  Languages,
  Info,
  Sparkles,
  ChevronRight,
  ExternalLink,
  Layers,
  HelpCircle,
  ArrowRight,
  Sliders,
  History,
  Calendar,
  BookOpen,
  Search,
  Check,
  AlertCircle,
  Eye,
  Microscope,
  Tag,
  Smartphone,
  SwitchCamera,
  RotateCcw,
} from "lucide-react";
import { diseaseApi } from "../api/disease";
import { useFarm } from "../context/FarmContext";

// Bilingual translations dictionary
const I18N = {
  en: {
    title: "Universal Plant Disease Intelligence AI",
    subtitle: "Evidence-backed neural pathology diagnosis & integrated management for Indian agriculture",
    langButton: "ಕನ್ನಡ (Kannada)",
    selectBlockAlert: "Please select an active Crop Block before running diagnosis.",
    blockLabel: "Crop Block:",
    noBlockSelected: "Preview Mode (No Crop Block selected — Results display immediately)",
    supportedCropsBtn: "Supported Crops Catalog",
    kbExplorerBtn: "Verified Knowledge Base (38+ Conditions)",
    quickTestTitle: "Quick Test Verified Benchmark Field Samples",
    quickTestSubtitle: "Click any benchmark leaf sample below for instant 1-click evaluation",
    tabUpload: "Upload Photo",
    tabCamera: "Live Camera Capture",
    dropText: "Drag & drop plant leaf photograph here, or click to browse",
    fileFormats: "Supports JPG, JPEG, PNG, WEBP (Max 15MB)",
    startCamera: "Start Camera",
    snapPhoto: "Capture Leaf Photo",
    stopCamera: "Close Camera",
    switchCamera: "Flip / Switch Camera",
    nativeCamera: "Use Phone Camera (Ultra-Res)",
    startingCamera: "Initializing Camera Stream...",
    cameraActivePill: "Live Camera Active (HD)",
    reticlePrompt: "Center diseased leaf inside this reticle",
    cameraPermissionTip: "If video doesn't appear, click the lock or camera icon in your browser URL bar to allow camera access.",
    changePhoto: "Choose Different Photo",
    runDiagnosis: "Run Neural AI Diagnosis",
    analyzing: "Analyzing Leaf Pathology...",
    analyzingSub: "Executing 8-stage verification pipeline & MobileNetV2 feature extraction...",
    predictionTitle: "Diagnostic Assessment",
    healthyLabel: "Healthy Foliage",
    diseaseLabel: "Disease Detected",
    uncertainLabel: "Inconclusive / Low Statistical Confidence",
    nonPlantLabel: "Non-Plant Subject Detected",
    confidence: "Model Confidence",
    foliageCoverage: "Plant Foliage Area",
    posterior: "Agro-Climate Posterior",
    validateBtn: "Validate with Local Climate Priors",
    validating: "Cross-verifying with Weather & Priors...",
    validatedSuccess: "Validated by Bayesian Diagnostic Engine",
    symptomsTitle: "Observed Visible Symptoms",
    diffTitle: "Differential Diagnosis (Visual Look-Alikes)",
    favorableTitle: "Favorable Agro-Climatic Conditions",
    managementTitle: "Integrated Disease Management (IPM)",
    preventionTitle: "1. Preventive & Cultural Practices",
    biologicalTitle: "2. Biological & Organic Measures",
    chemicalTitle: "3. Scientifically Verified Chemical Management (CIBRC / ICAR)",
    causalAgent: "Causal Pathogen",
    affectedParts: "Affected Plant Organs",
    scientificName: "Botanical Taxon",
    topCandidates: "Differential Diagnostic Alternatives (Top-3)",
    expertWarningTitle: "Mandatory Expert Confirmation Notice",
    sourcesTitle: "Verified Agricultural Sources & Citations",
    qualityTitle: "Input Image Quality & Foliage Validation",
    limitationsTitle: "Model Limitations & Advisory Disclaimer",
    limitationsText: "This AI diagnosis is an assistive decision-support platform powered by deep neural networks. Raw softmax probabilities reflect feature match, not definitive laboratory proof. In cases of severe or unfamiliar infestation, please verify with your local Krishi Vigyan Kendra (KVK) or State Horticulture Department before intensive spraying.",
    closeModal: "Close",
    cameraError: "Unable to access camera. Please check browser permissions or upload an image file instead.",
    historyTitle: "Diagnosis History for this Block",
    historyEmpty: "No prior diagnoses recorded for this crop block.",
    historyDate: "Date & Time",
    historyCrop: "Crop / Pathology",
    historyConfidence: "CNN Confidence",
    historyStatus: "Bayesian Validation",
    historyViewBtn: "View Advisory",
    historyLoading: "Loading block diagnosis records...",
    validatedBadge: "Validated",
    pendingBadge: "Pending Validation",
    searchKbPlaceholder: "Search by crop, disease, pathogen, or symptoms...",
    allCrops: "All Indian Crops",
  },
  kn: {
    title: "ಸಾರ್ವತ್ರಿಕ ಸಸ್ಯ ರೋಗ ಪತ್ತೆ ಮತ್ತು ಕೃಷಿ ಸಲಹಾ AI",
    subtitle: "ಭಾರತೀಯ ಕೃಷಿ ಮತ್ತು ತೋಟಗಾರಿಕಾ ಬೆಳೆಗಳಿಗೆ ವೈಜ್ಞಾನಿಕ ಆಧಾರಿತ ಎಲೆ ರೋಗ ಪತ್ತೆ ಮತ್ತು ಸಮಗ್ರ ನಿರ್ವಹಣಾ ವೇದಿಕೆ",
    langButton: "English",
    selectBlockAlert: "ರೋಗ ಪತ್ತೆ ಹಚ್ಚುವ ಮುನ್ನ ದಯವಿಟ್ಟು ಸಕ್ರಿಯ ಕ್ರಾಪ್ ಬ್ಲಾಕ್ ಆಯ್ಕೆಮಾಡಿ.",
    blockLabel: "ಕ್ರಾಪ್ ಬ್ಲಾಕ್:",
    noBlockSelected: "ಪೂರ್ವವೀಕ್ಷಣೆ ಮೋಡ್ (ಕ್ರಾಪ್ ಬ್ಲಾಕ್ ಆಯ್ಕೆಯಾಗಿಲ್ಲ — ಫಲಿತಾಂಶ ತಕ್ಷಣ ಕಾಣುತ್ತದೆ)",
    supportedCropsBtn: "ಬೆಂಬಲಿತ ಬೆಳೆಗಳ ಪಟ್ಟಿ",
    kbExplorerBtn: "ರೋಗ ಜ್ಞಾನ ಭಂಡಾರ (38+ ರೋಗಗಳು)",
    quickTestTitle: "ಪರೀಕ್ಷಾ ಮಾದರಿ ಎಲೆಗಳು (1-ಕ್ಲಿಕ್ ಪರೀಕ್ಷೆ)",
    quickTestSubtitle: "ನೈಜ AI ಪರೀಕ್ಷೆಗಾಗಿ ಕೆಳಗಿನ ಯಾವುದೇ ಮಾದರಿ ಎಲೆಯನ್ನು ಕ್ಲಿಕ್ ಮಾಡಿ",
    tabUpload: "ಫೋಟೋ ಅಪ್‌ಲೋಡ್",
    tabCamera: "ಲೈವ್ ಕ್ಯಾಮೆರಾ",
    dropText: "ಗಿಡದ ಎಲೆಯ ಫೋಟೋವನ್ನು ಇಲ್ಲಿಗೆ ಎಳೆಯಿರಿ ಅಥವಾ ಫೈಲ್ ಆರಿಸಿ",
    fileFormats: "JPG, JPEG, PNG, WEBP ಫೈಲ್ ಸಮ್ಮತ (ಗರಿಷ್ಠ 15MB)",
    startCamera: "ಕ್ಯಾಮೆರಾ ಆರಂಭಿಸಿ",
    snapPhoto: "ಎಲೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ",
    stopCamera: "ಕ್ಯಾಮೆರಾ ಮುಚ್ಚಿ",
    switchCamera: "ಕ್ಯಾಮೆರಾ ಬದಲಿಸಿ (ಮುಂಭಾಗ/ಹಿಂಭಾಗ)",
    nativeCamera: "ಮೊಬೈಲ್ ಕ್ಯಾಮೆರಾ ಬಳಸಿ (ಸ್ಪಷ್ಟ ಫೋಟೋ)",
    startingCamera: "ಕ್ಯಾಮೆರಾ ಆರಂಭಿಸಲಾಗುತ್ತಿದೆ...",
    cameraActivePill: "ಲೈವ್ ಕ್ಯಾಮೆರಾ ಸಕ್ರಿಯವಾಗಿದೆ (HD)",
    reticlePrompt: "ರೋಗಪೀಡಿತ ಎಲೆಯನ್ನು ಈ ಚೌಕಟ್ಟಿನ ಮಧ್ಯದಲ್ಲಿ ಇರಿಸಿ",
    cameraPermissionTip: "ಕ್ಯಾಮೆರಾ ಕಾಣಿಸದಿದ್ದರೆ, ಬ್ರೌಸರ್ URL ಬಾರ್‌ನಲ್ಲಿರುವ ಲಾಕ್ ಅಥವಾ ಕ್ಯಾಮೆರಾ ಐಕಾನ್ ಕ್ಲಿಕ್ ಮಾಡಿ ಅನುಮತಿ ನೀಡಿ.",
    changePhoto: "ಬೇರೆ ಫೋಟೋ ಬದಲಾಯಿಸಿ",
    runDiagnosis: "AI ರೋಗ ತಪಾಸಣೆ ನಡೆಸಿ",
    analyzing: "ಎಲೆಯ ರೋಗ ತಪಾಸಣೆ ನಡೆಯುತ್ತಿದೆ...",
    analyzingSub: "8-ಹಂತದ ತಪಾಸಣೆ ಮತ್ತು ಮೊಬೈಲ್‌ನೆಟ್‌ವಿ2 ವಿಶ್ಲೇಷಣೆ ಪ್ರಕ್ರಿಯೆ ಪ್ರಗತಿಯಲ್ಲಿದೆ...",
    predictionTitle: "ತಪಾಸಣಾ ವರದಿ",
    healthyLabel: "ಆರೋಗ್ಯಕರ ಸಸ್ಯ",
    diseaseLabel: "ರೋಗದ ಲಕ್ಷಣ ಪತ್ತೆಯಾಗಿದೆ",
    uncertainLabel: "ಅನಿಶ್ಚಿತ / ಕಡಿಮೆ ನಿಖರತೆ",
    nonPlantLabel: "ಸಸ್ಯವಲ್ಲದ ಚಿತ್ರ",
    confidence: "ಮಾದರಿ ವಿಶ್ವಾಸಾರ್ಹತೆ",
    foliageCoverage: "ಎಲೆಯ ವ್ಯಾಪ್ತಿ",
    posterior: "ಹವಾಮಾನ ದೃಢೀಕರಣ",
    validateBtn: "ಸ್ಥಳೀಯ ಹವಾಮಾನದೊಂದಿಗೆ ದೃಢೀಕರಿಸಿ",
    validating: "ಹವಾಮಾನ ಪರೀಕ್ಷಿಸಲಾಗುತ್ತಿದೆ...",
    validatedSuccess: "ಬೇಸಿಯನ್ ಎಂಜಿನ್‌ನಿಂದ ದೃಢೀಕರಿಸಲಾಗಿದೆ",
    symptomsTitle: "ಕಂಡುಬಂದ ರೋಗ ಲಕ್ಷಣಗಳು",
    diffTitle: "ವಿಭಿನ್ನ ರೋಗ ನಿರ್ಣಯ (ಹೋಲುವ ರೋಗಗಳು)",
    favorableTitle: "ರೋಗ ಉಲ್ಬಣಕ್ಕೆ ಅನುಕೂಲಕರ ಹವಾಮಾನ",
    managementTitle: "ಸಮಗ್ರ ರೋಗ ನಿರ್ವಹಣಾ ಕ್ರಮಗಳು (IPM)",
    preventionTitle: "1. ಮುಂಜಾಗ್ರತಾ ಕ್ರಮಗಳು ಮತ್ತು ನೈರ್ಮಲ್ಯ",
    biologicalTitle: "2. ಜೈವಿಕ ಮತ್ತು ಸಾವಯವ ವಿಧಾನಗಳು",
    chemicalTitle: "3. ICAR ಅನುಮೋದಿತ ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ",
    causalAgent: "ರೋಗಕಾರಕ ಜೀವಿ",
    affectedParts: "ಬಾಧಿತ ಭಾಗಗಳು",
    scientificName: "ವೈಜ್ಞಾನಿಕ ಸಸ್ಯಶಾಸ್ತ್ರೀಯ ಹೆಸರು",
    topCandidates: "ಅತ್ಯುನ್ನತ ಸಂಭವನೀಯತೆಗಳು (ಟಾಪ್-3)",
    expertWarningTitle: "ಕಡ್ಡಾಯ ತಜ್ಞರ ದೃಢೀಕರಣ ಎಚ್ಚರಿಕೆ",
    sourcesTitle: "ವಿಶ್ವಾಸಾರ್ಹ ಕೃಷಿ ಸಂಶೋಧನಾ ಮೂಲಗಳು",
    qualityTitle: "ಚಿತ್ರದ ಗುಣಮಟ್ಟ ಮತ್ತು ಎಲೆ ತಪಾಸಣೆ",
    limitationsTitle: "ಮಾದರಿ ಮಿತಿಗಳು ಮತ್ತು ಎಚ್ಚರಿಕೆ",
    limitationsText: "ಈ AI ತಪಾಸಣೆಯು ಕೇವಲ ರೈತರಿಗೆ ಸಹಾಯಕಾರಿ ತಂತ್ರಜ್ಞಾನವಾಗಿದೆ. ಗಂಭೀರ ರೋಗಬಾಧೆ ಕಂಡುಬಂದಲ್ಲಿ ನಿಮ್ಮ ಸಮೀಪದ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಅಥವಾ ತೋಟಗಾರಿಕಾ ಅಧಿಕಾರಿಗಳನ್ನು ಸಂಪರ್ಕಿಸಿ ಸಲಹೆ ಪಡೆಯಿರಿ.",
    closeModal: "ಮುಚ್ಚಿ",
    cameraError: "ಕ್ಯಾಮೆರಾ ತೆರೆಯಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ. ಬ್ರೌಸರ್ ಅನುಮತಿಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಅಥವಾ ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
    historyTitle: "ಈ ಬ್ಲಾಕ್‌ನ ಹಿಂದಿನ ರೋಗ ತಪಾಸಣೆಗಳು",
    historyEmpty: "ಈ ಕ್ರಾಪ್ ಬ್ಲಾಕ್‌ಗೆ ಯಾವುದೇ ಹಿಂದಿನ ತಪಾಸಣಾ ದಾಖಲೆಗಳಿಲ್ಲ.",
    historyDate: "ದಿನಾಂಕ ಮತ್ತು ಸಮಯ",
    historyCrop: "ಬೆಳೆ / ರೋಗ",
    historyConfidence: "AI ನಿಖರತೆ",
    historyStatus: "ಹವಾಮಾನ ದೃಢೀಕರಣ",
    historyViewBtn: "ಸಲಹೆ ವೀಕ್ಷಿಸಿ",
    historyLoading: "ದಾಖಲೆಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...",
    validatedBadge: "ದೃಢೀಕರಿಸಲಾಗಿದೆ",
    pendingBadge: "ಬಾಕಿ ಉಳಿದಿದೆ",
    searchKbPlaceholder: "ಬೆಳೆ, ರೋಗ ಅಥವಾ ಲಕ್ಷಣಗಳ ಮೂಲಕ ಹುಡುಕಿ...",
    allCrops: "ಎಲ್ಲಾ ಬೆಳೆಗಳು",
  },
};

export const DiseaseDetection = () => {
  const { selectedCropBlock, cropBlocks, selectCropBlockById, setShowSetupModal } = useFarm();
  const [lang, setLang] = useState("en");
  const t = I18N[lang];

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [activeTab, setActiveTab] = useState("upload"); // "upload" | "camera"
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraLoading, setCameraLoading] = useState(false);
  const [cameraFacingMode, setCameraFacingMode] = useState("environment"); // "environment" | "user"
  const [hasMultipleCameras, setHasMultipleCameras] = useState(false);
  const nativeCameraInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [targetCrop, setTargetCrop] = useState("auto"); // "auto" | "Arecanut" | "Tomato" | "Potato" | "Corn" | "Grape" | "Apple" | "Pepper bell" | "Rice"
  const [showCatalogModal, setShowCatalogModal] = useState(false);
  const [showKbModal, setShowKbModal] = useState(false);
  const [visionStatus, setVisionStatus] = useState(null);
  const [sampleImages, setSampleImages] = useState([]);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Knowledge base modal state
  const [kbQuery, setKbQuery] = useState("");
  const [kbCropFilter, setKbCropFilter] = useState("");
  const [kbResults, setKbResults] = useState([]);
  const [kbLoading, setKbLoading] = useState(false);
  const [selectedKbMonograph, setSelectedKbMonograph] = useState(null);

  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Detect if user has multiple camera devices (e.g. mobile front/back, or multiple webcams)
  useEffect(() => {
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
      navigator.mediaDevices
        .enumerateDevices()
        .then((devices) => {
          const videoDevices = devices.filter((d) => d.kind === "videoinput");
          if (videoDevices.length > 1) {
            setHasMultipleCameras(true);
          }
        })
        .catch((err) => console.warn("Failed to enumerate media devices:", err));
    }
  }, []);

  // Bind media stream to video element whenever camera becomes active or facing changes
  useEffect(() => {
    if (isCameraActive && videoRef.current && streamRef.current) {
      const video = videoRef.current;
      video.srcObject = streamRef.current;
      video.muted = true;
      video.setAttribute("playsinline", "true");
      video.setAttribute("webkit-playsinline", "true");

      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          console.warn("Video play error on mount:", err);
        });
      }
    }
  }, [isCameraActive, cameraFacingMode]);

  // Fetch block history whenever selectedCropBlock changes
  const fetchHistory = (blockId) => {
    if (!blockId) {
      setHistory([]);
      return;
    }
    setHistoryLoading(true);
    diseaseApi
      .getHistory(blockId)
      .then((records) => {
        setHistory(Array.isArray(records) ? records : []);
      })
      .catch((err) => {
        console.warn("Failed to load block diagnosis history:", err.message);
      })
      .finally(() => setHistoryLoading(false));
  };

  useEffect(() => {
    if (selectedCropBlock?.id) {
      fetchHistory(selectedCropBlock.id);
    } else {
      setHistory([]);
    }
  }, [selectedCropBlock?.id]);

  // Load vision status and benchmark sample images on mount
  useEffect(() => {
    diseaseApi
      .getVisionStatus()
      .then((res) => setVisionStatus(res.data || res))
      .catch((err) => console.warn("Vision status check failed:", err.message));

    diseaseApi
      .getSampleImages()
      .then((res) => {
        const data = res.data || res;
        setSampleImages(Array.isArray(data) ? data : []);
      })
      .catch((err) => console.warn("Sample images load error:", err.message));
  }, []);

  // Cleanup camera stream
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // Search knowledge base
  const loadKnowledgeBase = (query = "", crop = "") => {
    setKbLoading(true);
    diseaseApi
      .getKnowledgeBase({ query: query || undefined, crop: crop || undefined, lang })
      .then((res) => {
        const data = res.data || res;
        setKbResults(data.results || []);
      })
      .catch((err) => console.warn("KB search failed:", err.message))
      .finally(() => setKbLoading(false));
  };

  useEffect(() => {
    if (showKbModal) {
      loadKnowledgeBase(kbQuery, kbCropFilter);
    }
  }, [showKbModal, kbQuery, kbCropFilter, lang]);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (e) {
          console.warn("Track stop error:", e);
        }
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setCameraLoading(false);
  };

  const startCamera = async (facing = cameraFacingMode) => {
    setError("");
    setCameraLoading(true);

    // Stop any existing stream first
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (e) {
          // ignore
        }
      });
      streamRef.current = null;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError(
        lang === "kn"
          ? "ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಲೈವ್ ಕ್ಯಾಮೆರಾ ಬೆಂಬಲವಿಲ್ಲ. ದಯವಿಟ್ಟು ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ Chrome/Edge ಬಳಸಿ."
          : "Live camera is not supported in this browser. Please use photo upload or native phone camera instead."
      );
      setCameraLoading(false);
      return;
    }

    let stream = null;
    // Attempt 1: High definition with ideal facing mode
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: facing },
          width: { ideal: 1920, max: 1920 },
          height: { ideal: 1080, max: 1080 },
        },
        audio: false,
      });
    } catch (e1) {
      console.warn("Attempt 1 (HD ideal facing) failed, trying fallback 2:", e1.name, e1.message);
      // Attempt 2: Basic with facing mode constraint
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: facing },
          audio: false,
        });
      } catch (e2) {
        console.warn("Attempt 2 (basic facing) failed, trying fallback 3 (any video device):", e2.name, e2.message);
        // Attempt 3: Any video device available (desktop webcams, virtual cameras)
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          });
        } catch (e3) {
          console.error("All camera constraints failed:", e3);
          let errText = t.cameraError;
          if (e3.name === "NotAllowedError" || e3.name === "PermissionDeniedError") {
            errText =
              lang === "kn"
                ? "ಕ್ಯಾಮೆರಾ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ. ಬ್ರೌಸರ್ URL ಬಾರ್‌ನಲ್ಲಿರುವ ಲಾಕ್ ಅಥವಾ ಕ್ಯಾಮೆರಾ ಐಕಾನ್ ಕ್ಲಿಕ್ ಮಾಡಿ ಅನುಮತಿ ನೀಡಿ."
                : "Camera permission denied. Click the lock or camera icon in your browser address bar to allow camera access.";
          } else if (e3.name === "NotFoundError" || e3.name === "DevicesNotFoundError") {
            errText =
              lang === "kn"
                ? "ಯಾವುದೇ ಕ್ಯಾಮೆರಾ ಸಾಧನ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ವೆಬ್‌ಕ್ಯಾಮ್ ಸಂಪರ್ಕಿಸಿ ಅಥವಾ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
                : "No camera device found on this system. Please connect a webcam or upload a photo instead.";
          }
          setError(errText);
          setIsCameraActive(false);
          setCameraLoading(false);
          return;
        }
      }
    }

    if (stream) {
      streamRef.current = stream;
      setIsCameraActive(true);
      setCameraLoading(false);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
        videoRef.current.play().catch((err) => console.warn("Video play error on start:", err));
      }
    }
  };

  const handleToggleFacingMode = () => {
    const nextMode = cameraFacingMode === "environment" ? "user" : "environment";
    setCameraFacingMode(nextMode);
    startCamera(nextMode);
  };

  const handleCapturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");

    if (cameraFacingMode === "user") {
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, width, height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setError("Failed to capture image frame. Please try again.");
          return;
        }
        const file = new File([blob], `leaf_capture_${Date.now()}.jpg`, { type: "image/jpeg" });
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(blob));
        setResult(null);
        setError("");
        setTargetCrop("auto");
        stopCamera();
        setActiveTab("upload");
      },
      "image/jpeg",
      0.95
    );
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 15 * 1024 * 1024) {
        setError("File size exceeds 15MB limit. Please upload a smaller image.");
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError("");
      // Reset targetCrop to auto so any previously clicked benchmark sample doesn't bias user uploads
      setTargetCrop("auto");
    }
  };

  // Quick-test 1-click sample loader
  const handleSelectSample = async (sample) => {
    try {
      setError("");
      setResult(null);
      if (sample.crop) {
        setTargetCrop(sample.crop);
      }
      const url = `/api/v1/agents/vision/sample-image-file/${encodeURIComponent(sample.filename)}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to load sample image.");
      const blob = await response.blob();
      const mimeType = sample.filename.endsWith(".webp") ? "image/webp" : "image/jpeg";
      const file = new File([blob], sample.filename, { type: mimeType });
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(blob));
      setActiveTab("upload");
    } catch (err) {
      setError(`Failed to load benchmark sample: ${err.message}`);
    }
  };

  const handleUpload = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile) {
      setError("Please select or capture a photograph first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const blockId = selectedCropBlock ? selectedCropBlock.id : null;
      // In auto mode, pass null cropContext so backend vision models classify without species bias
      const cropContext = targetCrop !== "auto" ? targetCrop : null;

      const response = await diseaseApi.detectDisease(blockId, selectedFile, cropContext);
      const detectionData = response.data || response;
      setResult(detectionData);
      if (blockId) {
        fetchHistory(blockId);
      }
    } catch (err) {
      console.error("Diagnosis error:", err);
      const detail = err.response?.data?.detail || err.message || "Diagnosis failed.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleValidateBayesian = async () => {
    if (!result?.id) return;
    setValidating(true);
    try {
      const response = await diseaseApi.validateDetection(result.id);
      const updated = response.data || response;
      setResult((prev) => ({
        ...prev,
        posterior_probability: updated.posterior_probability,
        validated: updated.validated,
      }));
      if (selectedCropBlock?.id) {
        fetchHistory(selectedCropBlock.id);
      }
    } catch (err) {
      console.error("Bayesian validation error:", err);
      setError("Failed to validate with local weather priors: " + (err.response?.data?.detail || err.message));
    } finally {
      setValidating(false);
    }
  };

  return (
    <div style={{ maxWidth: "1150px", margin: "0 auto", padding: "1.5rem" }}>
      {/* Top Header & Bilingual Toggle */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "1.75rem",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                padding: "0.2rem 0.6rem",
                borderRadius: "999px",
                background: "#dcfce7",
                color: "#166534",
                fontSize: "0.75rem",
                fontWeight: 700,
                letterSpacing: "0.5px",
                textTransform: "uppercase",
              }}
            >
              🇮🇳 India Agri-Intelligence
            </span>
            {visionStatus && (
              <span
                style={{
                  fontSize: "0.75rem",
                  padding: "0.2rem 0.55rem",
                  borderRadius: "999px",
                  background: visionStatus.status === "ready" ? "#ecfdf5" : "#fef2f2",
                  color: visionStatus.status === "ready" ? "#047857" : "#b91c1c",
                  fontWeight: 600,
                }}
              >
                ● {visionStatus.status === "ready" ? "Neural Model Loaded (38 Classes)" : "Model Offline"}
              </span>
            )}
          </div>
          <h1 style={{ fontSize: "1.9rem", fontWeight: 800, color: "#0f172a", margin: "0.35rem 0 0.25rem 0" }}>
            {t.title}
          </h1>
          <p style={{ color: "#475569", margin: 0, fontSize: "0.95rem" }}>{t.subtitle}</p>
        </div>

        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", alignItems: "center" }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setLang(lang === "en" ? "kn" : "en")}
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 700 }}
          >
            <Languages size={16} />
            {t.langButton}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowKbModal(true)}
            style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}
          >
            <BookOpen size={16} color="#0284c7" />
            {t.kbExplorerBtn}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowCatalogModal(true)}
            style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}
          >
            <Layers size={16} />
            {t.supportedCropsBtn}
          </button>
        </div>
      </div>

      {/* Active Crop Block Selection Banner */}
      <div
        className="card"
        style={{
          padding: "1rem 1.25rem",
          marginBottom: "1.5rem",
          background: "#ffffff",
          border: selectedCropBlock ? "1px solid #bbf7d0" : "1px solid #fed7aa",
          borderRadius: "12px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.85rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "10px",
              background: selectedCropBlock ? "#ecfdf5" : "#eff6ff",
              color: selectedCropBlock ? "#166534" : "#2563eb",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Leaf size={22} />
          </div>
          <div>
            <div style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 600 }}>
              {selectedCropBlock ? t.blockLabel : (lang === "kn" ? "ಕಾರ್ಯವಿಧಾನ:" : "Operating Mode:")}
            </div>
            <div style={{ fontSize: "1rem", fontWeight: 700, color: "#1e293b" }}>
              {selectedCropBlock ? (
                <>
                  {selectedCropBlock.name}
                  {selectedCropBlock.crop_type && (
                    <span style={{ fontWeight: 400, color: "#64748b", marginLeft: "0.35rem" }}>
                      ({selectedCropBlock.crop_type}
                      {selectedCropBlock.variety ? ` - ${selectedCropBlock.variety}` : ""})
                    </span>
                  )}
                </>
              ) : (
                <span style={{ color: "#2563eb", display: "inline-flex", alignItems: "center", gap: "0.4rem" }}>
                  <ShieldCheck size={18} />
                  {t.noBlockSelected}
                </span>
              )}
            </div>
          </div>
        </div>

        {cropBlocks && cropBlocks.length > 0 ? (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
              {lang === "kn" ? "ಬ್ಲಾಕ್ ಬದಲಿಸಿ:" : "Switch Block:"}
            </span>
            <select
              style={{
                padding: "0.4rem 0.75rem",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "0.85rem",
                fontWeight: 600,
                color: "#1e293b",
                background: "#ffffff",
              }}
              value={selectedCropBlock?.id || ""}
              onChange={(e) => selectCropBlockById(e.target.value)}
            >
              <option value="">-- {lang === "kn" ? "ಪೂರ್ವವೀಕ್ಷಣಾ ಮೋಡ್ (ಯಾವುದೇ ಬ್ಲಾಕ್ ಇಲ್ಲ)" : "Preview Mode (No Block)"} --</option>
              {cropBlocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name} ({b.crop_type || "Crop"})
                </option>
              ))}
            </select>
          </div>
        ) : (
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: "0.85rem", padding: "0.4rem 0.85rem" }}
            onClick={() => setShowSetupModal && setShowSetupModal(true)}
          >
            + {lang === "kn" ? "ಹೊಸ ಕ್ರಾಪ್ ಬ್ಲಾಕ್ ರಚಿಸಿ" : "Create Farm / Crop Block"}
          </button>
        )}
      </div>

      {/* Target Plant Species / Model Context Selector */}
      <div
        className="card"
        style={{
          padding: "0.9rem 1.25rem",
          marginBottom: "1.5rem",
          background: "#ffffff",
          borderRadius: "12px",
          border: targetCrop === "Arecanut" ? "1px solid #fde68a" : "1px solid #e2e8f0",
          boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.75rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              background: targetCrop === "Arecanut" ? "#fef3c7" : "#ecfdf5",
              color: targetCrop === "Arecanut" ? "#b45309" : "#059669",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Tag size={18} />
          </div>
          <div>
            <div style={{ fontSize: "0.78rem", color: "#64748b", fontWeight: 600 }}>
              {lang === "kn" ? "ರೋಗ ತಪಾಸಣಾ ಬೆಳೆ ವ್ಯಾಪ್ತಿ / ಸಂದರ್ಭ:" : "Diagnostic Target Species / Context:"}
            </div>
            <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#1e293b" }}>
              {targetCrop === "Arecanut"
                ? "🌴 Arecanut Palm (ICAR-CPCRI Monograph Mode)"
                : targetCrop === "auto"
                ? "🌐 Auto-Detect (38 Benchmark PlantVillage Classes)"
                : `${targetCrop} (MobileNetV2 Neural Model)`}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <select
            id="crop-target-select"
            style={{
              padding: "0.45rem 0.85rem",
              borderRadius: "8px",
              border: targetCrop === "Arecanut" ? "2px solid #f59e0b" : "1px solid #cbd5e1",
              fontSize: "0.85rem",
              fontWeight: 600,
              color: "#1e293b",
              background: targetCrop === "Arecanut" ? "#fffbeb" : "#ffffff",
              cursor: "pointer",
            }}
            value={targetCrop}
            onChange={(e) => setTargetCrop(e.target.value)}
          >
            <option value="auto">🌐 Auto-Detect (38 PlantVillage Classes)</option>
            <option value="Arecanut">🌴 Arecanut Palm (ಅಡಿಕೆ - ICAR-CPCRI Monograph)</option>
            <option value="Tomato">🍅 Tomato (ಟೊಮ್ಯಾಟೊ)</option>
            <option value="Potato">🥔 Potato (ಆಲೂಗಡ್ಡೆ)</option>
            <option value="Corn">🌽 Corn / Maize (ಮೆಕ್ಕೆಜೋಳ)</option>
            <option value="Grape">🍇 Grape (ದ್ರಾಕ್ಷಿ)</option>
            <option value="Apple">🍎 Apple (ಸೇಬು)</option>
            <option value="Pepper bell">🫑 Chilli / Pepper (ಮೆಣಸಿನಕಾಯಿ)</option>
            <option value="Rice">🌾 Rice / Paddy (ಭತ್ತ - ICAR Monograph)</option>
          </select>
        </div>
      </div>

      {/* Quick Test Benchmark Samples Pill Row */}
      {sampleImages.length > 0 && (
        <div
          style={{
            background: "linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%)",
            borderRadius: "14px",
            border: "1px solid #bbf7d0",
            padding: "1rem 1.25rem",
            marginBottom: "1.5rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <Sparkles size={16} color="#166534" />
              <strong style={{ fontSize: "0.9rem", color: "#166534" }}>{t.quickTestTitle}</strong>
            </div>
            <span style={{ fontSize: "0.75rem", color: "#64748b" }}>{t.quickTestSubtitle}</span>
          </div>

          <div
            style={{
              display: "flex",
              gap: "0.6rem",
              overflowX: "auto",
              paddingBottom: "0.35rem",
              scrollbarWidth: "thin",
            }}
          >
            {sampleImages.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSample(s)}
                style={{
                  flexShrink: 0,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0.45rem 0.85rem",
                  background: "#ffffff",
                  border: "1px solid #cbd5e1",
                  borderRadius: "999px",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  color: "#334155",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = "#16a34a";
                  e.currentTarget.style.background = "#f0fdf4";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = "#cbd5e1";
                  e.currentTarget.style.background = "#ffffff";
                }}
              >
                <span>{s.badge === "Healthy" ? "🟢" : "🍂"}</span>
                <span>{lang === "kn" && s.title_kn ? s.title_kn : s.title}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Upload / Live Camera Card */}
      <div
        className="card"
        style={{
          padding: "1.75rem",
          marginBottom: "1.75rem",
          background: "#ffffff",
          borderRadius: "16px",
          border: "1px solid #e2e8f0",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        }}
      >
        {/* Tab Toggle Buttons */}
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            marginBottom: "1.25rem",
            borderBottom: "1px solid #f1f5f9",
            paddingBottom: "0.75rem",
          }}
        >
          <button
            type="button"
            className={`btn ${activeTab === "upload" ? "btn-primary" : "btn-secondary"}`}
            style={{ fontSize: "0.9rem", padding: "0.5rem 1rem", display: "flex", alignItems: "center", gap: "0.4rem" }}
            onClick={() => {
              stopCamera();
              setActiveTab("upload");
            }}
          >
            <Upload size={16} />
            {t.tabUpload}
          </button>
          <button
            type="button"
            className={`btn ${activeTab === "camera" ? "btn-primary" : "btn-secondary"}`}
            style={{ fontSize: "0.9rem", padding: "0.5rem 1rem", display: "flex", alignItems: "center", gap: "0.4rem" }}
            onClick={() => {
              setActiveTab("camera");
              startCamera(cameraFacingMode);
            }}
          >
            <Camera size={16} />
            {t.tabCamera}
          </button>
        </div>

        {error && (
          <div
            style={{
              padding: "0.85rem 1rem",
              background: "#fee2e2",
              color: "#991b1b",
              borderRadius: "10px",
              marginBottom: "1.25rem",
              fontSize: "0.875rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Live Camera View Tab */}
        {activeTab === "camera" && (
          <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
            {/* Hidden Native Phone Camera File Input */}
            <input
              ref={nativeCameraInputRef}
              id="mobile-native-camera"
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: "none" }}
              onClick={(e) => {
                e.target.value = null;
              }}
              onChange={(e) => {
                handleFileChange(e);
                stopCamera();
                setActiveTab("upload");
              }}
            />

            {/* Camera Loading Splash */}
            {cameraLoading && (
              <div
                style={{
                  padding: "3rem 1.5rem",
                  background: "#0f172a",
                  borderRadius: "16px",
                  color: "#ffffff",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "1rem",
                }}
              >
                <RefreshCw size={36} className="spin" style={{ color: "#22c55e", animation: "spin 1s linear infinite" }} />
                <div style={{ fontWeight: 600, fontSize: "1.05rem" }}>{t.startingCamera}</div>
                <p style={{ fontSize: "0.85rem", color: "#94a3b8", maxWidth: "420px", margin: 0, lineHeight: 1.5 }}>
                  {t.cameraPermissionTip}
                </p>
              </div>
            )}

            {/* Active Live Video Stream */}
            {!cameraLoading && isCameraActive && (
              <div>
                <div
                  style={{
                    position: "relative",
                    maxWidth: "680px",
                    margin: "0 auto",
                    borderRadius: "16px",
                    overflow: "hidden",
                    boxShadow: "0 10px 25px -5px rgba(0,0,0,0.3)",
                    background: "#000000",
                    border: "2px solid #22c55e",
                  }}
                >
                  {/* Live Status Pill */}
                  <div
                    style={{
                      position: "absolute",
                      top: "12px",
                      left: "12px",
                      background: "rgba(0, 0, 0, 0.75)",
                      backdropFilter: "blur(4px)",
                      color: "#4ade80",
                      padding: "0.35rem 0.75rem",
                      borderRadius: "999px",
                      fontSize: "0.78rem",
                      fontWeight: 700,
                      display: "flex",
                      alignItems: "center",
                      gap: "0.45rem",
                      zIndex: 10,
                      boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
                    }}
                  >
                    <span
                      style={{
                        width: "8px",
                        height: "8px",
                        borderRadius: "50%",
                        background: "#22c55e",
                        display: "inline-block",
                        boxShadow: "0 0 8px #22c55e",
                      }}
                    />
                    {t.cameraActivePill}
                    <span style={{ color: "#94a3b8", fontWeight: 400 }}>
                      ({cameraFacingMode === "user" ? "Front" : "Rear"})
                    </span>
                  </div>

                  {/* Video Stream Element */}
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    onLoadedMetadata={() => {
                      if (videoRef.current) {
                        videoRef.current.play().catch((err) => console.warn("Video play error on loadedmetadata:", err));
                      }
                    }}
                    style={{
                      width: "100%",
                      maxHeight: "460px",
                      display: "block",
                      objectFit: "cover",
                      transform: cameraFacingMode === "user" ? "scaleX(-1)" : "none",
                    }}
                  />

                  {/* Aiming Reticle / Focus Brackets Overlay */}
                  <div
                    style={{
                      position: "absolute",
                      top: "15%",
                      left: "15%",
                      right: "15%",
                      bottom: "15%",
                      border: "2px dashed rgba(255,255,255,0.75)",
                      borderRadius: "16px",
                      pointerEvents: "none",
                      boxShadow: "0 0 0 9999px rgba(0, 0, 0, 0.25)",
                      display: "flex",
                      alignItems: "flex-end",
                      justifyContent: "center",
                      paddingBottom: "0.75rem",
                    }}
                  >
                    <span
                      style={{
                        background: "rgba(0,0,0,0.65)",
                        color: "#ffffff",
                        padding: "0.25rem 0.65rem",
                        borderRadius: "6px",
                        fontSize: "0.75rem",
                        fontWeight: 600,
                      }}
                    >
                      {t.reticlePrompt}
                    </span>
                  </div>
                </div>

                {/* Camera Control Action Buttons */}
                <div
                  style={{
                    marginTop: "1.25rem",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "0.75rem",
                  }}
                >
                  {/* Main Snap Photo Button */}
                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{
                      padding: "0.85rem 2rem",
                      fontSize: "1.05rem",
                      fontWeight: 700,
                      display: "flex",
                      alignItems: "center",
                      gap: "0.6rem",
                      borderRadius: "12px",
                      boxShadow: "0 4px 14px rgba(22, 163, 74, 0.4)",
                    }}
                    onClick={handleCapturePhoto}
                  >
                    <Camera size={22} />
                    {t.snapPhoto}
                  </button>

                  {/* Flip / Switch Camera Button */}
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{
                      padding: "0.85rem 1.25rem",
                      fontSize: "0.95rem",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      borderRadius: "12px",
                    }}
                    onClick={handleToggleFacingMode}
                    title={t.switchCamera}
                  >
                    <SwitchCamera size={18} />
                    {t.switchCamera}
                  </button>

                  {/* Native Phone Camera Option */}
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{
                      padding: "0.85rem 1.25rem",
                      fontSize: "0.95rem",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      borderRadius: "12px",
                      color: "#0369a1",
                      borderColor: "#bae6fd",
                      background: "#f0f9ff",
                    }}
                    onClick={() => nativeCameraInputRef.current && nativeCameraInputRef.current.click()}
                    title={t.nativeCamera}
                  >
                    <Smartphone size={18} />
                    {t.nativeCamera}
                  </button>

                  {/* Stop / Cancel Camera Button */}
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{
                      padding: "0.85rem 1.25rem",
                      fontSize: "0.95rem",
                      borderRadius: "12px",
                    }}
                    onClick={() => {
                      stopCamera();
                      setActiveTab("upload");
                    }}
                  >
                    <XCircle size={18} />
                    {t.stopCamera}
                  </button>
                </div>
              </div>
            )}

            {/* Inactive Camera State */}
            {!cameraLoading && !isCameraActive && (
              <div
                style={{
                  border: "2px dashed #cbd5e1",
                  borderRadius: "16px",
                  padding: "3rem 1.5rem",
                  textAlign: "center",
                  background: "#f8fafc",
                }}
              >
                <div
                  style={{
                    width: "68px",
                    height: "68px",
                    borderRadius: "50%",
                    background: "#ecfdf5",
                    color: "#16a34a",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    margin: "0 auto 1.25rem auto",
                    boxShadow: "0 4px 10px rgba(0,0,0,0.05)",
                  }}
                >
                  <Camera size={34} />
                </div>
                <h4 style={{ margin: "0 0 0.5rem 0", color: "#1e293b", fontSize: "1.15rem", fontWeight: 700 }}>
                  {lang === "kn" ? "ಲೈವ್ ಕ್ಯಾಮೆರಾ ವ್ಯೂಫೈಂಡರ್" : "Live Camera Viewfinder"}
                </h4>
                <p style={{ margin: "0 auto 1.5rem auto", color: "#64748b", fontSize: "0.9rem", maxWidth: "440px" }}>
                  {lang === "kn"
                    ? "ನಿಮ್ಮ ತೋಟದ ಎಲೆಯನ್ನು ನೇರವಾಗಿ ಕ್ಯಾಮೆರಾ ಮುಂದೆ ಹಿಡಿದು ಸ್ಪಷ್ಟ ರೋಗ ಲಕ್ಷಣಗಳನ್ನು ಸೆರೆಹಿಡಿಯಿರಿ."
                    : "Point your device camera directly at the affected crop leaf to capture clear pathology symptoms."}
                </p>

                <div style={{ display: "flex", justifyContent: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{
                      padding: "0.85rem 1.75rem",
                      fontSize: "1rem",
                      fontWeight: 700,
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      borderRadius: "12px",
                    }}
                    onClick={() => startCamera(cameraFacingMode)}
                  >
                    <Camera size={20} />
                    {t.startCamera}
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{
                      padding: "0.85rem 1.5rem",
                      fontSize: "0.95rem",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      borderRadius: "12px",
                      color: "#0369a1",
                      borderColor: "#bae6fd",
                      background: "#ffffff",
                    }}
                    onClick={() => nativeCameraInputRef.current && nativeCameraInputRef.current.click()}
                  >
                    <Smartphone size={18} />
                    {t.nativeCamera}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Upload / Preview View */}
        {activeTab === "upload" && (
          <form onSubmit={handleUpload}>
            <div
              style={{
                border: "2px dashed #94a3b8",
                borderRadius: "14px",
                padding: previewUrl ? "1rem" : "2.5rem 1.5rem",
                textAlign: "center",
                cursor: "pointer",
                backgroundColor: previewUrl ? "#ffffff" : "#f8fafc",
                marginBottom: "1.5rem",
                transition: "all 0.2s ease",
              }}
              onClick={() => document.getElementById("leaf-file-input").click()}
            >
              <input
                id="leaf-file-input"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                style={{ display: "none" }}
                onClick={(e) => {
                  e.target.value = null;
                }}
                onChange={handleFileChange}
              />

              {previewUrl ? (
                <div>
                  <img
                    src={previewUrl}
                    alt="Preview"
                    style={{
                      maxHeight: "340px",
                      maxWidth: "100%",
                      borderRadius: "10px",
                      objectFit: "contain",
                      boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
                      marginBottom: "0.75rem",
                    }}
                  />
                  <div>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ fontSize: "0.85rem", padding: "0.35rem 0.85rem" }}
                      onClick={(e) => {
                        e.stopPropagation();
                        document.getElementById("leaf-file-input").click();
                      }}
                    >
                      <RefreshCw size={14} />
                      {t.changePhoto}
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <div
                    style={{
                      width: "64px",
                      height: "64px",
                      borderRadius: "50%",
                      background: "#dcfce7",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      margin: "0 auto 1rem auto",
                    }}
                  >
                    <Upload size={30} color="#10b981" />
                  </div>
                  <p style={{ fontWeight: 700, color: "#1e293b", fontSize: "1.05rem", margin: "0 0 0.35rem 0" }}>
                    {t.dropText}
                  </p>
                  <span style={{ fontSize: "0.85rem", color: "#64748b" }}>{t.fileFormats}</span>
                </div>
              )}
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: "100%",
                padding: "0.85rem",
                fontSize: "1.05rem",
                fontWeight: 700,
                opacity: !selectedFile || loading ? 0.6 : 1,
              }}
              disabled={!selectedFile || loading}
            >
              {loading ? (
                <>
                  <RefreshCw size={20} className="spin" style={{ animation: "spin 1s linear infinite" }} />
                  {t.analyzing}
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  {t.runDiagnosis} {!selectedCropBlock && "(Quick Preview Mode)"}
                </>
              )}
            </button>
          </form>
        )}
      </div>

      {/* Loading Card */}
      {loading && (
        <div
          className="card"
          style={{
            padding: "2rem",
            textAlign: "center",
            background: "linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%)",
            border: "1px solid #bbf7d0",
            marginBottom: "2rem",
            borderRadius: "16px",
          }}
        >
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              background: "#10b981",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 1rem auto",
              boxShadow: "0 4px 14px rgba(16, 185, 129, 0.4)",
            }}
          >
            <RefreshCw size={28} style={{ animation: "spin 1.2s linear infinite" }} />
          </div>
          <h3 style={{ fontSize: "1.2rem", color: "#065f46", margin: "0 0 0.4rem 0" }}>{t.analyzing}</h3>
          <p style={{ fontSize: "0.9rem", color: "#047857", margin: 0 }}>{t.analyzingSub}</p>
        </div>
      )}

      {/* Diagnostic Result Section */}
      {result && !loading && (
        <div
          className="card"
          style={{
            padding: "2rem",
            border: `2px solid ${
              result.is_plant === false
                ? "#c084fc"
                : result.is_inconclusive
                ? "#fef08a"
                : result.is_healthy
                ? "#86efac"
                : "#fca5a5"
            }`,
            background:
              result.is_plant === false
                ? "#faf5ff"
                : result.is_inconclusive
                ? "#fffbeb"
                : result.is_healthy
                ? "#f0fdf4"
                : "#fff1f2",
            borderRadius: "16px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
            marginBottom: "2rem",
          }}
        >
          {/* Header of Result */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              borderBottom: "1px solid rgba(0,0,0,0.08)",
              paddingBottom: "1.25rem",
              marginBottom: "1.5rem",
              flexWrap: "wrap",
              gap: "1rem",
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.35rem", flexWrap: "wrap" }}>
                {result.is_plant === false ? (
                  <span className="badge" style={{ background: "#f3e8ff", color: "#6b21a8", border: "1px solid #d8b4fe" }}>
                    <AlertTriangle size={14} />
                    {t.nonPlantLabel}
                  </span>
                ) : result.is_inconclusive ? (
                  <span className="badge" style={{ background: "#fef3c7", color: "#b45309", border: "1px solid #fde68a" }}>
                    <AlertTriangle size={14} />
                    {t.uncertainLabel}
                  </span>
                ) : result.is_healthy ? (
                  <span className="badge" style={{ background: "#dcfce7", color: "#15803d", border: "1px solid #bbf7d0" }}>
                    <CheckCircle2 size={14} />
                    {t.healthyLabel}
                  </span>
                ) : (
                  <span className="badge" style={{ background: "#fee2e2", color: "#991b1b", border: "1px solid #fca5a5" }}>
                    <XCircle size={14} />
                    {t.diseaseLabel}
                  </span>
                )}

                {result.crop && !result.is_inconclusive && result.is_plant !== false && result.crop !== "Unverified Crop" && (
                  <span
                    style={{
                      fontSize: "0.85rem",
                      fontWeight: 700,
                      background: "#ffffff",
                      padding: "0.2rem 0.65rem",
                      borderRadius: "6px",
                      border: "1px solid #cbd5e1",
                      color: "#334155",
                    }}
                  >
                    🌱 {lang === "kn" && result.crop_kn ? result.crop_kn : result.crop}
                  </span>
                )}

                {result.scientific_name && !result.is_inconclusive && (
                  <span style={{ fontSize: "0.8rem", color: "#64748b", fontStyle: "italic" }}>
                    ({result.scientific_name})
                  </span>
                )}

                {!result.crop_block_id && (
                  <span
                    style={{
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      background: "#dbeafe",
                      color: "#1e40af",
                      padding: "0.2rem 0.65rem",
                      borderRadius: "6px",
                      border: "1px solid #bfdbfe",
                    }}
                  >
                    🔍 {lang === "kn" ? "ಪೂರ್ವವೀಕ್ಷಣಾ ಮೋಡ್" : "Quick Preview"}
                  </span>
                )}
              </div>

              <h2
                style={{
                  fontSize: "1.65rem",
                  margin: "0.25rem 0",
                  color:
                    result.is_plant === false
                      ? "#581c87"
                      : result.is_inconclusive
                      ? "#92400e"
                      : result.is_healthy
                      ? "#14532d"
                      : "#881337",
                  fontWeight: 800,
                }}
              >
                {result.is_inconclusive
                  ? (lang === "kn" ? (result.condition_kn || "ಅನಿಶ್ಚಿತ / ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹತೆ") : (result.predicted_disease || "Inconclusive / Low Statistical Confidence"))
                  : (lang === "kn" && result.condition_kn
                      ? `${result.crop_kn || result.crop} - ${result.condition_kn}`
                      : result.predicted_disease)}
              </h2>

              {result.causal_agent && !result.is_inconclusive && (
                <div style={{ fontSize: "0.875rem", color: "#475569", fontWeight: 600, marginTop: "0.2rem" }}>
                  <span style={{ color: "#0284c7" }}>🔬 {t.causalAgent}:</span> {result.causal_agent}
                </div>
              )}
            </div>

            {/* Confidence & Bayesian Scores */}
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <div
                style={{
                  background: "#ffffff",
                  padding: "0.75rem 1.15rem",
                  borderRadius: "10px",
                  border: "1px solid #e2e8f0",
                  textAlign: "center",
                  minWidth: "115px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                  {t.confidence}
                </div>
                <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
                  {((result.cnn_confidence || 0) * 100).toFixed(1)}%
                </div>
              </div>

              {result.plant_coverage_pct !== null && result.plant_coverage_pct !== undefined && (
                <div
                  style={{
                    background: "#ffffff",
                    padding: "0.75rem 1.15rem",
                    borderRadius: "10px",
                    border: "1px solid #e2e8f0",
                    textAlign: "center",
                    minWidth: "115px",
                  }}
                >
                  <div style={{ fontSize: "0.72rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                    {t.foliageCoverage}
                  </div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#166534" }}>
                    {result.plant_coverage_pct}%
                  </div>
                </div>
              )}

              {result.posterior_probability !== null && result.posterior_probability !== undefined && (
                <div
                  style={{
                    background: "#ecfdf5",
                    padding: "0.75rem 1.15rem",
                    borderRadius: "10px",
                    border: "1px solid #a7f3d0",
                    textAlign: "center",
                    minWidth: "115px",
                  }}
                >
                  <div style={{ fontSize: "0.72rem", color: "#047857", textTransform: "uppercase", fontWeight: 700 }}>
                    {t.posterior}
                  </div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#047857" }}>
                    {(result.posterior_probability * 100).toFixed(1)}%
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Low Confidence / Uncertain State Banner */}
          {result.is_inconclusive && (
            <div
              style={{
                marginBottom: "1.25rem",
                padding: "1rem 1.25rem",
                background: "#fef3c7",
                border: "1px solid #fde68a",
                borderRadius: "10px",
                display: "flex",
                alignItems: "flex-start",
                gap: "0.75rem",
                color: "#92400e",
              }}
            >
              <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                <strong style={{ fontSize: "0.95rem" }}>
                  {lang === "kn" ? "ಅನಿಶ್ಚಿತ ಫಲಿತಾಂಶ / ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹತೆ:" : "Uncertain Diagnosis / Low Statistical Confidence:"}
                </strong>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.875rem", lineHeight: 1.5 }}>
                  {lang === "kn"
                    ? "ಈ ಚಿತ್ರದ ರೋಗ ಲಕ್ಷಣಗಳನ್ನು ಖಚಿತವಾಗಿ ಗುರುತಿಸಲು ಮಾದರಿಯ ವಿಶ್ವಾಸಾರ್ಹತೆ ಸಾಲದು. ಅನಗತ್ಯ ಅಥವಾ ತಪ್ಪು ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆಯನ್ನು ತಡೆಯಲು ಕೀಟನಾಶಕಗಳ ಸಲಹೆಯನ್ನು ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ. ದಯವಿಟ್ಟು ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಸ್ಪಷ್ಟ, ಕೇಂದ್ರೀಕೃತ ಫೋಟೋವನ್ನು ತೆಗೆಯಿರಿ ಅಥವಾ ಹತ್ತಿರದ ಕೆವಿಕೆ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ."
                    : "The automated neural model cannot classify this image with sufficient statistical certainty. To protect your crop and prevent phytotoxicity, disease-specific chemical prescriptions are strictly withheld. Please upload a crisp, well-lit photo of a single leaf in daylight or consult a local agricultural extension officer."}
                </p>
              </div>
            </div>
          )}

          {/* Cross-Species Consistency Warning if applicable */}
          {result.crop_mismatch_warning && (
            <div
              style={{
                marginBottom: "1.25rem",
                padding: "0.85rem 1rem",
                background: "#fffbeb",
                border: "1px solid #fde68a",
                borderRadius: "10px",
                display: "flex",
                alignItems: "flex-start",
                gap: "0.6rem",
                fontSize: "0.85rem",
                color: "#92400e",
              }}
            >
              <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                <strong>Cross-Species Note: </strong>
                {result.crop_mismatch_warning}
              </div>
            </div>
          )}

          {/* Bayesian Local Validation Trigger Button */}
          {(result.posterior_probability === null || result.posterior_probability === undefined) && !result.is_inconclusive && (
            <div
              style={{
                marginBottom: "1.5rem",
                padding: "0.9rem 1.25rem",
                background: "#ffffff",
                border: "1px solid #e2e8f0",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "0.75rem",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                <ShieldCheck size={20} color="#0284c7" />
                <span style={{ fontSize: "0.875rem", color: "#334155" }}>
                  Cross-verify this visual detection against local weather humidity, ambient temperature, and historical disease outbreak priors.
                </span>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.45rem 1rem", borderColor: "#0284c7", color: "#0284c7" }}
                onClick={handleValidateBayesian}
                disabled={validating}
              >
                {validating ? (
                  <>
                    <RefreshCw size={14} className="spin" style={{ animation: "spin 1s linear infinite" }} />
                    {t.validating}
                  </>
                ) : (
                  <>
                    <ShieldCheck size={14} />
                    {t.validateBtn}
                  </>
                )}
              </button>
            </div>
          )}

          {/* Top Predictions Differential Alternatives */}
          {result.top_predictions && result.top_predictions.length > 0 && (
            <div
              style={{
                background: "#ffffff",
                padding: "1.25rem",
                borderRadius: "12px",
                border: "1px solid #e2e8f0",
                marginBottom: "1.5rem",
              }}
            >
              <h4 style={{ fontSize: "0.95rem", color: "#334155", margin: "0 0 0.85rem 0", fontWeight: 700 }}>
                {t.topCandidates}
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {result.top_predictions.map((item, idx) => (
                  <div key={idx}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.2rem" }}>
                      <span style={{ fontWeight: 600, color: "#1e293b" }}>
                        {lang === "kn" && item.condition_kn
                          ? `${item.crop_kn || item.crop} - ${item.condition_kn}`
                          : `${item.crop} - ${item.condition}`}
                      </span>
                      <span style={{ fontWeight: 700, color: "#64748b" }}>
                        {((item.confidence || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div style={{ height: "6px", background: "#f1f5f9", borderRadius: "999px", overflow: "hidden" }}>
                      <div
                        style={{
                          height: "100%",
                          width: `${Math.min(100, Math.max(2, (item.confidence || 0) * 100))}%`,
                          background:
                            idx === 0
                              ? result.is_healthy
                                ? "#10b981"
                                : "#ef4444"
                              : "#94a3b8",
                          borderRadius: "999px",
                          transition: "width 0.4s ease",
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Symptoms and Differential Diagnosis Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.25rem", marginBottom: "1.5rem" }}>
            {/* Symptoms */}
            {(result.symptoms || result.symptoms_kn) && (
              <div
                style={{
                  background: "#ffffff",
                  padding: "1.25rem",
                  borderRadius: "12px",
                  border: "1px solid #e2e8f0",
                }}
              >
                <h4 style={{ fontSize: "0.95rem", color: "#0f172a", margin: "0 0 0.6rem 0", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Info size={16} color="#0284c7" />
                  {t.symptomsTitle}
                </h4>
                <p style={{ fontSize: "0.875rem", color: "#475569", lineHeight: 1.6, margin: 0, whiteSpace: "pre-line" }}>
                  {lang === "kn" && result.symptoms_kn ? result.symptoms_kn : result.symptoms}
                </p>
              </div>
            )}

            {/* Differential Diagnosis (Visual Look-Alikes) */}
            {(result.differential_diagnosis || result.differential_diagnosis_kn) && (
              <div
                style={{
                  background: "#ffffff",
                  padding: "1.25rem",
                  borderRadius: "12px",
                  border: "1px solid #e2e8f0",
                }}
              >
                <h4 style={{ fontSize: "0.95rem", color: "#0f172a", margin: "0 0 0.6rem 0", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Microscope size={16} color="#7c3aed" />
                  {t.diffTitle}
                </h4>
                <p style={{ fontSize: "0.875rem", color: "#475569", lineHeight: 1.6, margin: 0 }}>
                  {lang === "kn" && result.differential_diagnosis_kn
                    ? result.differential_diagnosis_kn
                    : result.differential_diagnosis}
                </p>
              </div>
            )}
          </div>

          {/* Favorable Agro-Climatic Conditions */}
          {(result.favorable_conditions || result.favorable_conditions_kn) && result.favorable_conditions !== "N/A" && (
            <div
              style={{
                background: "#ffffff",
                padding: "1rem 1.25rem",
                borderRadius: "12px",
                border: "1px solid #e2e8f0",
                marginBottom: "1.5rem",
              }}
            >
              <h4 style={{ fontSize: "0.92rem", color: "#0f172a", margin: "0 0 0.4rem 0", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <span>🌦️</span> {t.favorableTitle}
              </h4>
              <p style={{ fontSize: "0.85rem", color: "#475569", margin: 0, lineHeight: 1.5 }}>
                {lang === "kn" && result.favorable_conditions_kn
                  ? result.favorable_conditions_kn
                  : result.favorable_conditions}
              </p>
            </div>
          )}

          {/* Integrated Pest & Disease Management (IPM) 3-Pillar Breakdown */}
          <div
            style={{
              background: "#ffffff",
              padding: "1.5rem",
              borderRadius: "14px",
              border: "1px solid #e2e8f0",
              marginBottom: "1.5rem",
            }}
          >
            <h3 style={{ fontSize: "1.1rem", color: "#0f172a", margin: "0 0 1rem 0", fontWeight: 800, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <ShieldCheck size={20} color="#166534" />
              {t.managementTitle}
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {/* Pillar 1: Prevention */}
              {(result.preventive_practices || result.preventive_practices_kn) && (
                <div style={{ borderLeft: "3px solid #0284c7", paddingLeft: "0.85rem" }}>
                  <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "#0369a1", marginBottom: "0.25rem" }}>
                    {t.preventionTitle}
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "#334155", margin: 0, lineHeight: 1.5 }}>
                    {lang === "kn" && result.preventive_practices_kn
                      ? result.preventive_practices_kn
                      : result.preventive_practices}
                  </p>
                </div>
              )}

              {/* Pillar 2: Cultural & Biological */}
              {(result.cultural_biological_management || result.cultural_biological_management_kn) && (
                <div style={{ borderLeft: "3px solid #16a34a", paddingLeft: "0.85rem" }}>
                  <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "#15803d", marginBottom: "0.25rem" }}>
                    {t.biologicalTitle}
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "#334155", margin: 0, lineHeight: 1.5 }}>
                    {lang === "kn" && result.cultural_biological_management_kn
                      ? result.cultural_biological_management_kn
                      : result.cultural_biological_management}
                  </p>
                </div>
              )}

              {/* Pillar 3: Chemical Management */}
              {(result.chemical_management || result.chemical_management_kn) && (
                <div style={{ borderLeft: "3px solid #d97706", paddingLeft: "0.85rem" }}>
                  <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "#b45309", marginBottom: "0.25rem" }}>
                    {t.chemicalTitle}
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "#334155", margin: 0, lineHeight: 1.5 }}>
                    {lang === "kn" && result.chemical_management_kn
                      ? result.chemical_management_kn
                      : result.chemical_management}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Expert Confirmation Notice */}
          <div
            style={{
              padding: "0.9rem 1.1rem",
              background: "#fef3c7",
              border: "1px solid #fde68a",
              borderRadius: "10px",
              marginBottom: "1.25rem",
              fontSize: "0.85rem",
              color: "#92400e",
              display: "flex",
              alignItems: "flex-start",
              gap: "0.6rem",
            }}
          >
            <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
            <div>
              <strong>{t.expertWarningTitle}: </strong>
              {lang === "kn" && result.expert_warning_kn
                ? result.expert_warning_kn
                : result.expert_warning || t.limitationsText}
            </div>
          </div>

          {/* Verified Sources & Citations */}
          {result.sources && result.sources.length > 0 && (
            <div
              style={{
                padding: "0.85rem 1.1rem",
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: "10px",
                marginBottom: "1rem",
              }}
            >
              <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#475569", textTransform: "uppercase", marginBottom: "0.4rem" }}>
                📚 {t.sourcesTitle}
              </div>
              <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.8rem", color: "#64748b" }}>
                {result.sources.map((s, idx) => (
                  <li key={idx} style={{ marginBottom: "0.25rem" }}>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#0284c7", textDecoration: "underline", display: "inline-flex", alignItems: "center", gap: "0.25rem" }}
                    >
                      {s.title} ({s.institution})
                      <ExternalLink size={12} />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Limitations and Disclaimer */}
          <div
            style={{
              padding: "0.75rem 1rem",
              background: "rgba(0,0,0,0.02)",
              border: "1px dashed #cbd5e1",
              borderRadius: "10px",
              fontSize: "0.78rem",
              color: "#64748b",
            }}
          >
            <strong style={{ color: "#475569" }}>{t.limitationsTitle}: </strong>
            {t.limitationsText}
          </div>
        </div>
      )}

      {/* Diagnosis History Section */}
      <div
        className="card"
        style={{
          marginTop: "1.75rem",
          padding: "1.5rem",
          background: "#ffffff",
          borderRadius: "16px",
          border: "1px solid #e2e8f0",
          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1rem",
            flexWrap: "wrap",
            gap: "0.5rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "#ecfdf5",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#166534",
              }}
            >
              <History size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: "1.1rem", color: "#0f172a", fontWeight: 700 }}>
                {t.historyTitle}
              </h3>
              {selectedCropBlock && (
                <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
                  {selectedCropBlock.name} ({selectedCropBlock.crop_type || "Crop"})
                </span>
              )}
            </div>
          </div>
          {selectedCropBlock && (
            <button
              type="button"
              className="btn btn-secondary"
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "0.35rem" }}
              onClick={() => fetchHistory(selectedCropBlock.id)}
              disabled={historyLoading}
            >
              <RefreshCw size={14} className={historyLoading ? "spin-animation" : ""} />
              {historyLoading ? t.historyLoading : "Refresh"}
            </button>
          )}
        </div>

        {!selectedCropBlock ? (
          <p style={{ fontSize: "0.875rem", color: "#64748b", margin: 0 }}>
            {t.selectBlockAlert}
          </p>
        ) : historyLoading && history.length === 0 ? (
          <div style={{ textAlign: "center", padding: "1.5rem", color: "#64748b", fontSize: "0.875rem" }}>
            <RefreshCw size={20} className="spin-animation" style={{ margin: "0 auto 0.5rem auto", display: "block", color: "#166534" }} />
            {t.historyLoading}
          </div>
        ) : history.length === 0 ? (
          <div style={{ textAlign: "center", padding: "1.75rem 1rem", background: "#f8fafc", borderRadius: "10px" }}>
            <Leaf size={24} color="#94a3b8" style={{ margin: "0 auto 0.4rem auto" }} />
            <p style={{ fontSize: "0.875rem", color: "#64748b", margin: 0 }}>{t.historyEmpty}</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {history.map((item) => {
              const itemDate = new Date(item.detected_at).toLocaleString();
              const isItemHealthy = item.is_healthy || (item.condition && item.condition.toLowerCase().includes("healthy"));
              const isInconclusive = item.is_inconclusive || item.predicted_disease === "Inconclusive";

              const badgeBg = isInconclusive
                ? "rgba(168, 85, 247, 0.12)"
                : isItemHealthy
                ? "rgba(16, 185, 129, 0.12)"
                : "rgba(239, 68, 68, 0.12)";
              const badgeColor = isInconclusive
                ? "#7e22ce"
                : isItemHealthy
                ? "#047857"
                : "#b91c1c";

              return (
                <div
                  key={item.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "0.85rem 1.1rem",
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    flexWrap: "wrap",
                    gap: "0.75rem",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
                    <div
                      style={{
                        padding: "0.35rem 0.75rem",
                        borderRadius: "8px",
                        background: badgeBg,
                        color: badgeColor,
                        fontWeight: 700,
                        fontSize: "0.85rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.35rem",
                      }}
                    >
                      {isItemHealthy ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
                      {lang === "kn" && item.crop_kn
                        ? `${item.crop_kn} — ${item.condition_kn || item.condition}`
                        : `${item.crop || ""} — ${item.condition || item.predicted_disease}`}
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.8rem", color: "#64748b" }}>
                      <Calendar size={13} />
                      {itemDate}
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                    <span style={{ fontSize: "0.825rem", color: "#334155" }}>
                      <strong>{t.historyConfidence}:</strong> {(item.cnn_confidence * 100).toFixed(1)}%
                    </span>

                    {item.validated ? (
                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.2rem 0.55rem",
                          borderRadius: "999px",
                          background: "#dcfce7",
                          color: "#166534",
                          fontWeight: 600,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                        }}
                      >
                        <ShieldCheck size={12} />
                        {t.validatedBadge} ({((item.posterior_probability || item.cnn_confidence) * 100).toFixed(0)}%)
                      </span>
                    ) : (
                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.2rem 0.55rem",
                          borderRadius: "999px",
                          background: "#f1f5f9",
                          color: "#64748b",
                          fontWeight: 500,
                        }}
                      >
                        {t.pendingBadge}
                      </span>
                    )}

                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ padding: "0.3rem 0.65rem", fontSize: "0.78rem" }}
                      onClick={() => {
                        setResult(item);
                        window.scrollTo({ top: 380, behavior: "smooth" });
                      }}
                    >
                      {t.historyViewBtn}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Verified Knowledge Base Explorer Modal */}
      {showKbModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.6)",
            backdropFilter: "blur(4px)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "1rem",
          }}
          onClick={() => setShowKbModal(false)}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: "18px",
              maxWidth: "920px",
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: "2rem",
              boxShadow: "0 20px 30px -5px rgba(0, 0, 0, 0.3)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.25rem" }}>
              <div>
                <h3 style={{ fontSize: "1.45rem", fontWeight: 800, color: "#0f172a", margin: 0 }}>
                  📚 Verified Agricultural Disease Knowledge Base — India
                </h3>
                <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0.25rem 0 0 0" }}>
                  Curated monographs from ICAR, CPRI, IIHR, CPCRI, UAS Bangalore, and TNAU
                </p>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.85rem" }}
                onClick={() => setShowKbModal(false)}
              >
                {t.closeModal}
              </button>
            </div>

            {/* Search and Crop Filters */}
            <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: "240px", position: "relative" }}>
                <Search size={16} color="#94a3b8" style={{ position: "absolute", left: "10px", top: "11px" }} />
                <input
                  type="text"
                  placeholder={t.searchKbPlaceholder}
                  value={kbQuery}
                  onChange={(e) => setKbQuery(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "0.55rem 0.75rem 0.55rem 2.2rem",
                    borderRadius: "8px",
                    border: "1px solid #cbd5e1",
                    fontSize: "0.875rem",
                  }}
                />
              </div>

              <select
                value={kbCropFilter}
                onChange={(e) => setKbCropFilter(e.target.value)}
                style={{
                  padding: "0.55rem 0.85rem",
                  borderRadius: "8px",
                  border: "1px solid #cbd5e1",
                  fontSize: "0.875rem",
                  background: "#ffffff",
                }}
              >
                <option value="">{t.allCrops}</option>
                {["Tomato", "Potato", "Chilli", "Corn", "Grape", "Apple", "Citrus", "Arecanut", "Rice", "Wheat", "Cotton", "Sugarcane", "Mango", "Banana"].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* List of Knowledge Monographs */}
            {kbLoading ? (
              <div style={{ textAlign: "center", padding: "2rem", color: "#64748b" }}>
                <RefreshCw size={24} className="spin-animation" style={{ margin: "0 auto 0.5rem auto", display: "block" }} />
                Loading verified knowledge base...
              </div>
            ) : kbResults.length === 0 ? (
              <div style={{ textAlign: "center", padding: "2rem", color: "#64748b" }}>
                No matching plant disease monograph found.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem", maxHeight: "60vh", overflowY: "auto" }}>
                {kbResults.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      border: "1px solid #e2e8f0",
                      borderRadius: "12px",
                      padding: "1rem",
                      background: item.is_healthy ? "#f0fdf4" : "#f8fafc",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.35rem" }}>
                      <div>
                        <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#166534", textTransform: "uppercase" }}>
                          🌱 {item.crop} {item.crop_kn ? `(${item.crop_kn})` : ""}
                        </span>
                        <h4 style={{ margin: "0.15rem 0", fontSize: "1.05rem", color: "#0f172a", fontWeight: 700 }}>
                          {item.condition} {item.condition_kn ? `— ${item.condition_kn}` : ""}
                        </h4>
                        {item.causal_agent && (
                          <span style={{ fontSize: "0.8rem", color: "#0284c7", fontStyle: "italic" }}>
                            {item.causal_agent}
                          </span>
                        )}
                      </div>
                      <span
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.2rem 0.5rem",
                          borderRadius: "999px",
                          background: item.is_healthy ? "#dcfce7" : "#fee2e2",
                          color: item.is_healthy ? "#15803d" : "#991b1b",
                          fontWeight: 700,
                        }}
                      >
                        {item.is_healthy ? "Healthy" : "Pathology"}
                      </span>
                    </div>

                    <p style={{ fontSize: "0.825rem", color: "#475569", margin: "0.4rem 0", lineHeight: 1.5 }}>
                      <strong>Symptoms:</strong> {item.symptoms}
                    </p>

                    {item.differential_diagnosis && (
                      <p style={{ fontSize: "0.825rem", color: "#6b21a8", margin: "0.4rem 0", lineHeight: 1.5 }}>
                        <strong>Differential Key:</strong> {item.differential_diagnosis}
                      </p>
                    )}

                    {item.chemical_management && (
                      <p style={{ fontSize: "0.825rem", color: "#b45309", margin: "0.4rem 0", lineHeight: 1.5 }}>
                        <strong>Chemical (CIBRC/ICAR):</strong> {item.chemical_management}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Supported Crops Catalog Modal */}
      {showCatalogModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.5)",
            backdropFilter: "blur(4px)",
            zIndex: 999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "1rem",
          }}
          onClick={() => setShowCatalogModal(false)}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: "16px",
              maxWidth: "750px",
              width: "100%",
              maxHeight: "85vh",
              overflowY: "auto",
              padding: "2rem",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
              <div>
                <h3 style={{ fontSize: "1.35rem", margin: 0, color: "#0f172a" }}>Supported Indian Crops & Pathologies</h3>
                <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0.2rem 0 0 0" }}>
                  MobileNetV2 neural vision backbone trained on verified PlantVillage benchmarks (38 categories)
                </p>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.85rem" }}
                onClick={() => setShowCatalogModal(false)}
              >
                {t.closeModal}
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.85rem" }}>
              {[
                { crop: "Tomato (ಟೊಮ್ಯಾಟೊ)", items: ["Early Blight", "Late Blight", "Leaf Mold", "Septoria Spot", "Spider Mites", "Target Spot", "Yellow Leaf Curl (TYLCV)", "Mosaic Virus", "Healthy"] },
                { crop: "Potato (ಆಲೂಗಡ್ಡೆ)", items: ["Early Blight", "Late Blight", "Healthy"] },
                { crop: "Chilli / Pepper (ಮೆಣಸಿನಕಾಯಿ)", items: ["Bacterial Spot", "Healthy"] },
                { crop: "Corn / Maize (ಮೆಕ್ಕೆ ಜೋಳ)", items: ["Common Rust", "Northern Blight", "Gray Leaf Spot", "Healthy"] },
                { crop: "Grape (ದ್ರಾಕ್ಷಿ)", items: ["Black Rot", "Esca (Black Measles)", "Leaf Blight", "Healthy"] },
                { crop: "Apple (ಸೇಬು)", items: ["Apple Scab", "Black Rot", "Cedar Rust", "Healthy"] },
                { crop: "Citrus / Orange (ಕಿತ್ತಳೆ)", items: ["Citrus Greening (HLB)"] },
                { crop: "Arecanut (ಅಡಿಕೆ) *Extension*", items: ["Koleroga (Mahali)", "Yellow Leaf Disease", "Anabe (Foot Rot)", "Bud Borer", "Stem Bleeding", "Healthy"] },
                { crop: "Rice / Paddy (ಭತ್ತ) *Extension*", items: ["Rice Blast", "Bacterial Leaf Blight", "Brown Spot", "Healthy"] },
                { crop: "Wheat (ಗೋಧಿ) *Extension*", items: ["Yellow Stripe Rust", "Karnal Bunt", "Healthy"] },
                { crop: "Cotton (ಹತ್ತಿ) *Extension*", items: ["Bacterial Blight / Black Arm", "Leaf Curl Virus", "Healthy"] },
                { crop: "Sugarcane (ಕಬ್ಬು) *Extension*", items: ["Red Rot", "Smut", "Healthy"] },
                { crop: "Mango (ಮಾವಿನ ಹಣ್ಣು) *Extension*", items: ["Anthracnose / Blossom Blight", "Healthy"] },
                { crop: "Banana (ಬಾಳೆ) *Extension*", items: ["Sigatoka Leaf Spot", "Panama Wilt", "Healthy"] },
              ].map((grp, i) => (
                <div key={i} style={{ border: "1px solid #e2e8f0", borderRadius: "10px", padding: "1rem", background: "#f8fafc" }}>
                  <h4 style={{ fontSize: "0.95rem", color: "#166534", margin: "0 0 0.5rem 0", fontWeight: 700 }}>
                    {grp.crop}
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.8rem", color: "#475569" }}>
                    {grp.items.map((it, j) => (
                      <li key={j} style={{ marginBottom: "0.2rem" }}>{it}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
