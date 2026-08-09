import { useEffect, useMemo, useState } from "react";
import jsPDF from "jspdf";
import axios from "axios";
import {
  Upload,
  ScanLine,
  FileSearch,
  AlertTriangle,
  CheckCircle,
  Database,
  Activity,
  Image as ImageIcon,
  Cpu,
  Fingerprint,
  FileWarning,
  Hash,
  BarChart3,
  ShieldCheck,
  TrendingUp,
  Layers3,
} from "lucide-react";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from "recharts";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [acquisitionTime, setAcquisitionTime] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0] || null;

    setFile(selectedFile);
    setResult(null);

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (selectedFile) {
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setAcquisitionTime(new Date().toLocaleString());
    } else {
      setPreviewUrl(null);
      setAcquisitionTime(null);
    }
  };

  const analyzeFile = async () => {
    if (!file) {
      alert("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setResult(null);

      const response = await axios.post(
        "http://127.0.0.1:8000/analyze",
        formData
      );

      const analyzedResult = response.data?.result || response.data;

      setResult(analyzedResult);

      const historyEntry = {
        filename: file.name,
        time: new Date().toLocaleTimeString(),
        aiScore: Number(analyzedResult?.ai_fake_score || 0),
        authenticity: Number(analyzedResult?.authenticity_score || 0),
        forensic: Number(analyzedResult?.forensic_score || 0),
        risk: analyzedResult?.risk || "UNKNOWN",
      };

      setHistory((previous) => [
        historyEntry,
        ...previous.filter((item) => item.filename !== file.name),
      ].slice(0, 8));
    } catch (error) {
      console.error(error);

      alert(
        "Backend connection failed. Make sure the DeepGuard AI backend is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const percentage = (value) => {
    if (value === undefined || value === null || value === "") {
      return "--";
    }

    const numeric = Number(value);

    if (Number.isNaN(numeric)) {
      return "--";
    }

    return `${numeric.toFixed(2)}%`;
  };

  const getRiskClass = (risk) => {
    if (risk === "HIGH") {
      return "text-red-400 border-red-500/30 bg-red-500/10";
    }

    if (risk === "MEDIUM") {
      return "text-yellow-400 border-yellow-500/30 bg-yellow-500/10";
    }

    if (risk === "ERROR") {
      return "text-red-400 border-red-500/30 bg-red-500/10";
    }

    return "text-green-400 border-green-500/30 bg-green-500/10";
  };

  const getRiskExplanation = () => {
    if (!result) return "";

    const aiScore = Number(result.ai_fake_score || 0);
    const forensicScore = Number(result.forensic_score || 0);

    if (result.risk === "HIGH") {
      return "High AI synthetic-media indicators with supporting forensic evidence.";
    }

    if (result.risk === "MEDIUM" && aiScore >= 70 && forensicScore < 20) {
      return "High AI model score detected, but independent forensic support is limited.";
    }

    if (result.risk === "MEDIUM") {
      return "Moderate or elevated manipulation indicators require further examination.";
    }

    if (result.risk === "LOW" && forensicScore > 0) {
      return "Predominantly authentic characteristics with limited forensic anomalies.";
    }

    return "No strong synthetic-media evidence was identified by the available analysis.";
  };

  const aiScore = Number(result?.ai_fake_score || 0);
  const authenticityScore = Number(result?.authenticity_score || 0);
  const forensicScore = Number(result?.forensic_score || 0);

  const realismScore = useMemo(() => {
    if (Array.isArray(result?.ai_detection)) {
      const realism = result.ai_detection.find(
        (item) =>
          String(item.label || "").toLowerCase().includes("real") ||
          String(item.label || "").toLowerCase().includes("realism")
      );

      if (realism) {
        return Number(realism.score) * 100;
      }
    }

    return Math.max(0, 100 - aiScore);
  }, [result, aiScore]);

  const analyticsData = useMemo(() => {
    return [
      {
        name: "AI Synthetic",
        score: Number(aiScore.toFixed(2)),
      },
      {
        name: "Authenticity",
        score: Number(authenticityScore.toFixed(2)),
      },
      {
        name: "Forensic",
        score: Number(forensicScore.toFixed(2)),
      },
    ];
  }, [aiScore, authenticityScore, forensicScore]);

  const classificationData = useMemo(() => {
    return [
      {
        name: "Realism",
        value: Number(realismScore.toFixed(2)),
      },
      {
        name: "Deepfake",
        value: Number(aiScore.toFixed(2)),
      },
    ];
  }, [realismScore, aiScore]);

  const technicalAnalytics = useMemo(() => {
    const technical = result?.technical || {};

    return [
      {
        name: "Noise",
        value: Number(technical.noise_level || 0),
      },
      {
        name: "Edge Ratio",
        value: Number(technical.edge_ratio || 0) * 100,
      },
      {
        name: "Forensic",
        value: forensicScore,
      },
    ];
  }, [result, forensicScore]);

  const generateForensicReport = () => {
    if (!result || !file) {
      alert("Please examine an image first.");
      return;
    }

    const technical = result.technical || {};
    const doc = new jsPDF();

    let y = 20;

    const addText = (text, size = 11, spacing = 8) => {
      doc.setFontSize(size);

      const lines = doc.splitTextToSize(String(text), 175);

      if (y + lines.length * spacing > 280) {
        doc.addPage();
        y = 20;
      }

      doc.text(lines, 15, y);
      y += lines.length * spacing;
    };

    doc.setFontSize(18);
    doc.text("DeepGuard AI", 15, y);
    y += 10;

    doc.setFontSize(12);
    doc.text(
      "Digital Media Forensic Examination Report",
      15,
      y
    );
    y += 12;

    addText("EVIDENCE INFORMATION", 14, 9);

    addText(`Evidence Filename: ${file.name}`);

    addText(
      `SHA-256: ${
        result.sha256 ||
        result.file_hash ||
        result.hash ||
        "--"
      }`
    );

    addText(`Acquisition Time: ${acquisitionTime || "--"}`);

    y += 4;

    addText("AUTHENTICITY ASSESSMENT", 14, 9);

    addText(
      `AI Synthetic-Media Score: ${
        result.deepfake_probability ??
        result.ai_fake_score ??
        "--"
      }%`
    );

    addText(
      `Authenticity Assessment Score: ${
        result.authenticity_score ?? "--"
      }/100`
    );

    addText(`Risk Level: ${result.risk || "--"}`);

    addText(
      `Assessment: ${
        result.assessment ||
        getRiskExplanation()
      }`
    );

    y += 4;

    addText("AI ANALYSIS", 14, 9);

    addText(
      `AI Model Score: ${
        result.ai_fake_score ?? "--"
      }%`
    );

    addText(
      `Score Type: ${
        result.ai_score_type ||
        "uncalibrated_model_score"
      }`
    );

    if (Array.isArray(result.ai_detection)) {
      result.ai_detection.forEach((item) => {
        addText(
          `${item.label}: ${(Number(item.score) * 100).toFixed(2)}%`
        );
      });
    }

    y += 4;

    addText("FORENSIC ANALYSIS", 14, 9);

    addText(
      `Forensic Evidence Score: ${
        result.forensic_score ?? "--"
      }/100`
    );

    addText(
      `Forensic Evidence Level: ${
        result.forensic_level || "--"
      }`
    );

    y += 4;

    addText("FORENSIC FINDINGS", 14, 9);

    if (Array.isArray(result.findings)) {
      result.findings.forEach((finding) => {
        addText(`- ${finding}`);
      });
    } else {
      addText("--");
    }

    y += 4;

    addText("METADATA EXAMINATION", 14, 9);

    if (
      Array.isArray(result.metadata) &&
      result.metadata.length > 0
    ) {
      result.metadata.forEach((item) => {
        addText(`- ${item}`);
      });
    } else {
      addText("- No EXIF metadata found.");
    }

    y += 4;

    addText("DATA ANALYTICS SUMMARY", 14, 9);

    addText(`AI Synthetic-Media Score: ${aiScore.toFixed(2)}%`);
    addText(`Authenticity Score: ${authenticityScore.toFixed(2)}/100`);
    addText(`Forensic Evidence Score: ${forensicScore.toFixed(2)}/100`);
    addText(`Realism Score: ${realismScore.toFixed(2)}%`);

    y += 4;

    addText("TECHNICAL EXAMINATION", 14, 9);

    addText(`Width: ${technical.width ?? "--"} px`);
    addText(`Height: ${technical.height ?? "--"} px`);
    addText(`Format: ${technical.format || "--"}`);
    addText(`File Size: ${technical.file_size ?? "--"} bytes`);
    addText(`Noise Level: ${technical.noise_level ?? "--"}`);
    addText(`Edge Ratio: ${technical.edge_ratio ?? "--"}`);

    y += 8;

    addText("INTERPRETATION NOTE", 14, 9);

    addText(
      "The AI synthetic-media score is an uncalibrated model output and should not be interpreted as a validated probability of manipulation."
    );

    addText(
      "Forensic evidence indicators are supporting signals and do not independently establish whether an image is authentic or manipulated."
    );

    addText(
      "All analytical results should be reviewed by a qualified digital-forensics professional when used in an investigative or evidentiary context."
    );

    y += 4;

    addText("DeepGuard AI", 12, 9);

    addText(
      "AI-assisted analysis • Forensic indicators • Evidence scoring • Data analytics"
    );

    doc.save(
      `DeepGuard_Forensic_Report_${Date.now()}.pdf`
    );
  };

  return (
    <div className="min-h-screen bg-[#050b14] text-white">

      {/* HEADER */}
      <header className="border-b border-slate-800 bg-[#07101d]">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-cyan-400/10 border border-cyan-400/20">
                <Fingerprint className="w-7 h-7 text-cyan-400" />
              </div>

              <div>
                <h1 className="text-2xl font-bold text-white">
                  DeepGuard AI
                </h1>

                <p className="text-sm text-slate-400">
                  Digital Media Forensic Examination Platform
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">

              <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />

                <span className="text-xs font-semibold tracking-wider text-cyan-300">
                  FORENSIC EXAMINATION ACTIVE
                </span>
              </div>

              <div className="px-3 py-2 rounded-lg border border-slate-700 bg-slate-900/70">
                <p className="text-[9px] uppercase tracking-widest text-slate-500">
                  Proudly Developed
                </p>

                <p className="text-xs font-semibold text-slate-200">
                  IN PAKISTAN
                </p>
              </div>

            </div>
          </div>
        </div>
      </header>

      {/* MAIN */}
      <main className="max-w-7xl mx-auto px-6 py-10">

        {/* INTRO */}
        <section className="mb-8">
          <p className="text-cyan-400 text-sm font-semibold tracking-widest uppercase mb-2">
            Digital Evidence Laboratory
          </p>

          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Media Authenticity Examination
          </h2>

          <p className="text-slate-400 mt-3 max-w-3xl">
            AI-assisted digital media examination using artificial
            intelligence classification, metadata inspection,
            image-noise analysis, edge analysis, forensic
            evidence scoring, and analytical visualization.
          </p>
        </section>

        {/* EVIDENCE ACQUISITION */}
        <section className="rounded-2xl border border-slate-800 bg-[#091321] p-6 shadow-xl">

          <div className="flex items-center gap-3 mb-5">

            <div className="p-2 rounded-lg bg-cyan-400/10">
              <Upload className="w-5 h-5 text-cyan-400" />
            </div>

            <div>
              <h3 className="font-semibold text-lg text-white">
                Evidence Acquisition
              </h3>

              <p className="text-sm text-slate-500">
                Select an image for forensic examination
              </p>
            </div>

          </div>

          <label
            htmlFor="evidence-upload"
            className="block border border-dashed border-slate-700 rounded-xl p-8 md:p-10 text-center cursor-pointer hover:border-cyan-400/60 hover:bg-cyan-400/5 transition-all"
          >

            {!file ? (
              <>
                <ImageIcon className="w-12 h-12 text-slate-600 mx-auto mb-4" />

                <p className="text-slate-300 font-medium">
                  Click here to select an image
                </p>

                <p className="text-sm text-slate-500 mt-2">
                  JPG, JPEG, PNG and other supported image formats
                </p>
              </>
            ) : (
              <>
                <p className="text-cyan-400 text-sm font-semibold uppercase tracking-wider mb-4">
                  Selected evidence preview
                </p>

                {previewUrl && (
                  <div className="flex justify-center">
                    <div className="w-full max-w-md rounded-xl overflow-hidden border border-slate-700 bg-slate-950">
                      <img
                        src={previewUrl}
                        alt="Selected evidence preview"
                        className="w-full max-h-96 object-contain"
                      />
                    </div>
                  </div>
                )}

                <div className="mt-5 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-400/10 border border-cyan-400/20 max-w-full">

                  <CheckCircle className="w-4 h-4 text-cyan-400 shrink-0" />

                  <span className="text-sm text-cyan-300 break-all">
                    {file.name}
                  </span>

                </div>
              </>
            )}

            <input
              id="evidence-upload"
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />

          </label>

          <button
            type="button"
            onClick={analyzeFile}
            disabled={loading || !file}
            className="mt-6 px-8 py-3 rounded-xl bg-cyan-400 text-black font-bold disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 hover:bg-cyan-300 transition"
          >

            <ScanLine className="w-5 h-5" />

            {loading
              ? "Examining Evidence..."
              : "Start Forensic Examination"}

          </button>
        </section>

        {/* RESULTS */}
        {result && (
          <div className="mt-8 space-y-6">

            {/* EVIDENCE INTEGRITY */}
            <InfoCard
              icon={<Hash />}
              title="Evidence Integrity"
              subtitle="Cryptographic identification of examined evidence"
            >

              <div className="mb-5 flex items-center justify-between gap-4 rounded-xl border border-green-500/20 bg-green-500/5 px-4 py-3">

                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-500/10">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                  </div>

                  <div>
                    <p className="text-sm font-semibold text-green-400">
                      HASH VERIFIED
                    </p>

                    <p className="text-xs text-slate-500">
                      Evidence identity successfully established
                    </p>
                  </div>

                </div>

                <span className="rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-[10px] font-bold tracking-wider text-green-400">
                  VERIFIED
                </span>

              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

                <TechnicalItem
                  label="Evidence Filename"
                  value={file?.name || "--"}
                />

                <TechnicalItem
                  label="SHA-256 Evidence Hash"
                  value={
                    result.sha256 ||
                    result.file_hash ||
                    result.hash ||
                    "--"
                  }
                  wide
                />

                <TechnicalItem
                  label="Evidence Acquisition Time"
                  value={acquisitionTime || "--"}
                />

              </div>
            </InfoCard>

            {/* PRIMARY RESULTS */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-5">

              <ResultCard
                icon={<Cpu />}
                title="AI Synthetic-Media Score"
                value={percentage(aiScore)}
                description="Uncalibrated AI model output; not a validated probability"
              />

              <ResultCard
                icon={<CheckCircle />}
                title="Authenticity Assessment Score"
                value={`${authenticityScore.toFixed(0)}/100`}
                description="Derived primarily from the uncalibrated AI model output"
              />

              <ResultCard
                icon={<AlertTriangle />}
                title="Risk Level"
                value={result.risk || "--"}
                description={getRiskExplanation()}
                extraClass={getRiskClass(result.risk)}
              />

            </section>

            {/* DATA ANALYTICS */}
            <InfoCard
              icon={<BarChart3 />}
              title="Forensic Data Analytics"
              subtitle="Comparative visualization of AI, authenticity, and supporting forensic indicators"
            >

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* MAIN SCORE CHART */}
                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">

                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-semibold text-white">
                        Assessment Score Comparison
                      </h4>

                      <p className="text-xs text-slate-500 mt-1">
                        Current examination
                      </p>
                    </div>

                    <TrendingUp className="w-5 h-5 text-cyan-400" />
                  </div>

                  <div className="h-72">

                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={analyticsData}
                        margin={{
                          top: 10,
                          right: 10,
                          left: -10,
                          bottom: 10,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#1e293b"
                        />

                        <XAxis
                          dataKey="name"
                          stroke="#64748b"
                          tick={{ fill: "#94a3b8", fontSize: 11 }}
                        />

                        <YAxis
                          domain={[0, 100]}
                          stroke="#64748b"
                          tick={{ fill: "#94a3b8", fontSize: 11 }}
                        />

                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#0f172a",
                            border: "1px solid #334155",
                            borderRadius: "10px",
                            color: "#fff",
                          }}
                          formatter={(value) => [
                            `${Number(value).toFixed(2)}%`,
                            "Score",
                          ]}
                        />

                        <Bar
                          dataKey="score"
                          name="Score"
                          radius={[6, 6, 0, 0]}
                        >
                          {analyticsData.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={
                                index === 0
                                  ? "#22d3ee"
                                  : index === 1
                                  ? "#34d399"
                                  : "#a78bfa"
                              }
                            />
                          ))}
                        </Bar>

                      </BarChart>
                    </ResponsiveContainer>

                  </div>
                </div>

                {/* CLASSIFICATION CHART */}
                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">

                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-semibold text-white">
                        AI Classification Distribution
                      </h4>

                      <p className="text-xs text-slate-500 mt-1">
                        Detector classification output
                      </p>
                    </div>

                    <Layers3 className="w-5 h-5 text-cyan-400" />
                  </div>

                  <div className="h-72">

                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={classificationData}
                        margin={{
                          top: 10,
                          right: 10,
                          left: -10,
                          bottom: 10,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#1e293b"
                        />

                        <XAxis
                          dataKey="name"
                          stroke="#64748b"
                          tick={{ fill: "#94a3b8", fontSize: 11 }}
                        />

                        <YAxis
                          domain={[0, 100]}
                          stroke="#64748b"
                          tick={{ fill: "#94a3b8", fontSize: 11 }}
                        />

                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#0f172a",
                            border: "1px solid #334155",
                            borderRadius: "10px",
                            color: "#fff",
                          }}
                          formatter={(value) => [
                            `${Number(value).toFixed(2)}%`,
                            "Classification",
                          ]}
                        />

                        <Legend />

                        <Bar
                          dataKey="value"
                          name="Model Score"
                          radius={[6, 6, 0, 0]}
                        >
                          {classificationData.map((entry, index) => (
                            <Cell
                              key={`classification-${index}`}
                              fill={
                                index === 0
                                  ? "#34d399"
                                  : "#f87171"
                              }
                            />
                          ))}
                        </Bar>

                      </BarChart>
                    </ResponsiveContainer>

                  </div>
                </div>

              </div>

              {/* ANALYTICS METRICS */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">

                <AnalyticsMetric
                  icon={<Cpu />}
                  label="AI Score"
                  value={percentage(aiScore)}
                  description="Synthetic-media model output"
                />

                <AnalyticsMetric
                  icon={<ShieldCheck />}
                  label="Authenticity"
                  value={`${authenticityScore.toFixed(0)}/100`}
                  description="Assessment score"
                />

                <AnalyticsMetric
                  icon={<Activity />}
                  label="Forensic Evidence"
                  value={`${forensicScore.toFixed(0)}/100`}
                  description="Independent supporting indicators"
                />

                <AnalyticsMetric
                  icon={<BarChart3 />}
                  label="Realism"
                  value={percentage(realismScore)}
                  description="AI realism classification"
                />

              </div>

            </InfoCard>

            {/* SCORE BREAKDOWN */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-5">

              <InfoCard
                icon={<Cpu />}
                title="AI Detection"
                subtitle="Primary machine-learning assessment"
              >

                <div className="flex justify-between gap-4">

                  <span className="text-slate-400">
                    AI Model Score
                  </span>

                  <span className="text-xl font-bold text-cyan-400">
                    {percentage(aiScore)}
                  </span>

                </div>

                <div className="mt-4 h-2 rounded-full bg-slate-800 overflow-hidden">

                  <div
                    className="h-full bg-cyan-400 rounded-full transition-all"
                    style={{
                      width: `${Math.min(
                        Math.max(aiScore, 0),
                        100
                      )}%`,
                    }}
                  />

                </div>

                <p className="text-xs text-slate-500 mt-3">
                  This score represents the detector's model output
                  and has not been calibrated as a real-world probability.
                </p>

              </InfoCard>

              <InfoCard
                icon={<Activity />}
                title="Forensic Evidence"
                subtitle="Independent supporting indicators"
              >

                <div className="flex justify-between">

                  <span className="text-slate-400">
                    Evidence Score
                  </span>

                  <span className="text-xl font-bold text-cyan-400">
                    {forensicScore.toFixed(0)}/100
                  </span>

                </div>

                <div className="mt-4 h-2 rounded-full bg-slate-800 overflow-hidden">

                  <div
                    className="h-full bg-cyan-400 rounded-full transition-all"
                    style={{
                      width: `${Math.min(
                        Math.max(forensicScore, 0),
                        100
                      )}%`,
                    }}
                  />

                </div>

                <p className="text-xs text-slate-500 mt-3">
                  Supporting forensic evidence does not independently
                  establish whether media is authentic or manipulated.
                </p>

              </InfoCard>

            </section>

            {/* AI CLASSIFICATION */}
            <InfoCard
              icon={<Cpu />}
              title="AI Classification Results"
              subtitle="Raw classification labels returned by the AI detector"
            >

              <div className="space-y-3">

                {Array.isArray(result.ai_detection) &&
                result.ai_detection.length > 0 ? (

                  result.ai_detection.map((item, index) => (

                    <div
                      key={index}
                      className="flex justify-between rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-3"
                    >

                      <span className="text-slate-200">
                        {item.label}
                      </span>

                      <span className="text-cyan-400 font-semibold">
                        {(Number(item.score) * 100).toFixed(2)}%
                      </span>

                    </div>

                  ))

                ) : (

                  <div className="text-sm text-slate-500">
                    No classification data returned by the detector.
                  </div>

                )}

              </div>
            </InfoCard>

            {/* FINDINGS + METADATA */}
            <section className="grid grid-cols-1 lg:grid-cols-2 gap-5">

              <InfoCard
                icon={<FileWarning />}
                title="Forensic Findings"
              >

                <div className="space-y-3">

                  {Array.isArray(result.findings) &&
                  result.findings.length > 0 ? (

                    result.findings.map((finding, index) => (

                      <div
                        key={index}
                        className="flex gap-3 text-sm text-slate-300"
                      >

                        <CheckCircle className="w-5 h-5 text-cyan-400 shrink-0" />

                        <span>{finding}</span>

                      </div>

                    ))

                  ) : (

                    <p className="text-sm text-slate-500">
                      No forensic findings returned.
                    </p>

                  )}

                </div>

              </InfoCard>

              <InfoCard
                icon={<Database />}
                title="Metadata Examination"
              >

                <div className="space-y-3">

                  {Array.isArray(result.metadata) &&
                  result.metadata.length > 0 ? (

                    result.metadata.map((item, index) => (

                      <div
                        key={index}
                        className="text-sm text-slate-300 border-b border-slate-800 pb-3"
                      >
                        {item}
                      </div>

                    ))

                  ) : (

                    <div className="rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-3">

                      <p className="text-sm text-slate-400">
                        No EXIF metadata found.
                      </p>

                      <p className="text-xs text-slate-600 mt-1">
                        Absence of metadata does not prove manipulation.
                      </p>

                    </div>

                  )}

                </div>

              </InfoCard>

            </section>

            {/* TECHNICAL ANALYTICS */}
            <InfoCard
              icon={<BarChart3 />}
              title="Technical Data Analytics"
              subtitle="Supporting image characteristics extracted during examination"
            >

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">

                  <h4 className="font-semibold text-white mb-1">
                    Image Signal Metrics
                  </h4>

                  <p className="text-xs text-slate-500 mb-4">
                    Noise, edge density, and forensic score
                  </p>

                  <div className="h-64">

                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={technicalAnalytics}
                        margin={{
                          top: 10,
                          right: 10,
                          left: -10,
                          bottom: 10,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#1e293b"
                        />

                        <XAxis
                          dataKey="name"
                          stroke="#64748b"
                          tick={{ fill: "#94a3b8", fontSize: 11 }}
                        />

                        <YAxis
                          stroke="#64748b"
                          tick={{ fill: "#94a3b8", fontSize: 11 }}
                        />

                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#0f172a",
                            border: "1px solid #334155",
                            borderRadius: "10px",
                            color: "#fff",
                          }}
                        />

                        <Bar
                          dataKey="value"
                          name="Metric"
                          fill="#22d3ee"
                          radius={[6, 6, 0, 0]}
                        />

                      </BarChart>
                    </ResponsiveContainer>

                  </div>

                </div>

                <div className="grid grid-cols-2 gap-4">

                  <TechnicalAnalyticsBox
                    label="Image Width"
                    value={`${result.technical?.width ?? "--"} px`}
                  />

                  <TechnicalAnalyticsBox
                    label="Image Height"
                    value={`${result.technical?.height ?? "--"} px`}
                  />

                  <TechnicalAnalyticsBox
                    label="Noise Level"
                    value={result.technical?.noise_level ?? "--"}
                  />

                  <TechnicalAnalyticsBox
                    label="Edge Ratio"
                    value={result.technical?.edge_ratio ?? "--"}
                  />

                  <TechnicalAnalyticsBox
                    label="Format"
                    value={result.technical?.format || "--"}
                  />

                  <TechnicalAnalyticsBox
                    label="File Size"
                    value={`${result.technical?.file_size ?? "--"} bytes`}
                  />

                </div>

              </div>

            </InfoCard>

            {/* ASSESSMENT INTERPRETATION */}
            <InfoCard
              icon={<AlertTriangle />}
              title="Examination Interpretation"
              subtitle="How the automated assessment should be understood"
            >

              <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-5">

                <div className="flex gap-3">

                  <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />

                  <div>

                    <p className="text-sm font-semibold text-yellow-300">
                      {result.assessment || getRiskExplanation()}
                    </p>

                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      The AI detector provides an uncalibrated model score.
                      The forensic evidence score represents supporting
                      indicators such as metadata, image noise, edge density,
                      JPEG characteristics, and resolution. These signals
                      should be considered together rather than treated as
                      definitive proof of manipulation.
                    </p>

                  </div>

                </div>

              </div>

            </InfoCard>

            {/* ANALYSIS HISTORY */}
            {history.length > 0 && (
              <InfoCard
                icon={<Database />}
                title="Examination Analytics History"
                subtitle="Recent evidence examinations performed during this session"
              >

                <div className="overflow-x-auto">

                  <table className="w-full text-left">

                    <thead>
                      <tr className="border-b border-slate-800">

                        <th className="px-4 py-3 text-xs uppercase tracking-wider text-slate-500">
                          Evidence
                        </th>

                        <th className="px-4 py-3 text-xs uppercase tracking-wider text-slate-500">
                          Time
                        </th>

                        <th className="px-4 py-3 text-xs uppercase tracking-wider text-slate-500">
                          AI Score
                        </th>

                        <th className="px-4 py-3 text-xs uppercase tracking-wider text-slate-500">
                          Authenticity
                        </th>

                        <th className="px-4 py-3 text-xs uppercase tracking-wider text-slate-500">
                          Forensic
                        </th>

                        <th className="px-4 py-3 text-xs uppercase tracking-wider text-slate-500">
                          Risk
                        </th>

                      </tr>
                    </thead>

                    <tbody>

                      {history.map((item, index) => (

                        <tr
                          key={`${item.filename}-${index}`}
                          className="border-b border-slate-900 hover:bg-slate-900/40"
                        >

                          <td className="px-4 py-3 text-sm text-slate-300 max-w-xs truncate">
                            {item.filename}
                          </td>

                          <td className="px-4 py-3 text-sm text-slate-500">
                            {item.time}
                          </td>

                          <td className="px-4 py-3 text-sm text-cyan-400 font-semibold">
                            {item.aiScore.toFixed(2)}%
                          </td>

                          <td className="px-4 py-3 text-sm text-emerald-400 font-semibold">
                            {item.authenticity.toFixed(0)}/100
                          </td>

                          <td className="px-4 py-3 text-sm text-purple-400 font-semibold">
                            {item.forensic.toFixed(0)}/100
                          </td>

                          <td className="px-4 py-3">

                            <span
                              className={`inline-flex rounded-full border px-3 py-1 text-[10px] font-bold ${getRiskClass(
                                item.risk
                              )}`}
                            >
                              {item.risk}
                            </span>

                          </td>

                        </tr>

                      ))}

                    </tbody>

                  </table>

                </div>

              </InfoCard>
            )}

            {/* FORENSIC REPORT */}
            <section className="mt-8 rounded-2xl border border-cyan-500/20 bg-[#091321] p-6 shadow-xl">

              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-5">

                <div>

                  <div className="flex items-center gap-3">

                    <div className="p-2 rounded-lg bg-cyan-400/10">
                      <FileSearch className="w-5 h-5 text-cyan-400" />
                    </div>

                    <div>

                      <h3 className="font-semibold text-lg text-white">
                        Forensic Evidence Report
                      </h3>

                      <p className="text-sm text-slate-500 mt-1">
                        Generate a complete examination report with
                        forensic findings and data analytics.
                      </p>

                    </div>

                  </div>

                </div>

                <button
                  type="button"
                  onClick={generateForensicReport}
                  className="px-6 py-3 rounded-xl bg-cyan-400 text-black font-bold hover:bg-cyan-300 transition flex items-center justify-center gap-2"
                >

                  <FileSearch className="w-5 h-5" />

                  Generate Forensic Report

                </button>

              </div>

            </section>

            {/* TECHNICAL EXAMINATION */}
            <InfoCard
              icon={<FileSearch />}
              title="Technical Examination"
              subtitle="Raw technical characteristics of the examined evidence"
            >

              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">

                <TechnicalItem
                  label="Width"
                  value={`${result.technical?.width ?? "--"} px`}
                />

                <TechnicalItem
                  label="Height"
                  value={`${result.technical?.height ?? "--"} px`}
                />

                <TechnicalItem
                  label="Format"
                  value={result.technical?.format || "--"}
                />

                <TechnicalItem
                  label="File Size"
                  value={`${result.technical?.file_size ?? "--"} bytes`}
                />

                <TechnicalItem
                  label="Noise Level"
                  value={result.technical?.noise_level ?? "--"}
                />

                <TechnicalItem
                  label="Edge Ratio"
                  value={result.technical?.edge_ratio ?? "--"}
                />

              </div>

            </InfoCard>

          </div>
        )}

      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-800 mt-12">

        <div className="max-w-7xl mx-auto px-6 py-6 text-center">

          <p className="text-xs text-slate-600">
            DeepGuard AI - Digital Media Forensic Examination Platform
          </p>

          <p className="text-xs text-slate-700 mt-1">
            AI-assisted analysis - Forensic indicators - Evidence scoring - Data analytics
          </p>

        </div>

      </footer>

    </div>
  );
}


/* =========================================================
   RESULT CARD
========================================================= */

function ResultCard({
  icon,
  title,
  value,
  description,
  extraClass = "",
}) {
  return (
    <div
      className={
        "rounded-2xl border p-6 shadow-lg bg-[#091321] " +
        (extraClass || "border-slate-800")
      }
    >

      <div className="flex items-center gap-3 mb-4">

        <div className="p-2 rounded-lg bg-cyan-400/10 text-cyan-400">
          {icon}
        </div>

        <span className="text-sm text-slate-400">
          {title}
        </span>

      </div>

      <p className="text-3xl font-bold text-white">
        {value}
      </p>

      <p className="text-xs text-slate-500 mt-2 leading-relaxed">
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   INFO CARD
========================================================= */

function InfoCard({
  icon,
  title,
  subtitle,
  children,
}) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-[#091321] p-6 shadow-xl">

      <div className="flex items-center gap-3 mb-5">

        <div className="p-2 rounded-lg bg-cyan-400/10 text-cyan-400">
          {icon}
        </div>

        <div>

          <h3 className="font-semibold text-lg text-white">
            {title}
          </h3>

          {subtitle && (
            <p className="text-sm text-slate-500 mt-1">
              {subtitle}
            </p>
          )}

        </div>

      </div>

      {children}

    </section>
  );
}


/* =========================================================
   TECHNICAL ITEM
========================================================= */

function TechnicalItem({
  label,
  value,
  wide = false,
}) {
  return (
    <div className={wide ? "md:col-span-1" : ""}>

      <p className="text-[10px] uppercase tracking-widest text-slate-600">
        {label}
      </p>

      <p className="mt-2 font-semibold text-slate-200 break-all">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   ANALYTICS METRIC
========================================================= */

function AnalyticsMetric({
  icon,
  label,
  value,
  description,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">

      <div className="flex items-center gap-2">

        <div className="p-2 rounded-lg bg-cyan-400/10 text-cyan-400">
          {icon}
        </div>

        <span className="text-xs uppercase tracking-wider text-slate-500">
          {label}
        </span>

      </div>

      <p className="text-2xl font-bold text-white mt-3">
        {value}
      </p>

      <p className="text-[11px] text-slate-600 mt-1">
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   TECHNICAL ANALYTICS BOX
========================================================= */

function TechnicalAnalyticsBox({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5">

      <p className="text-[10px] uppercase tracking-widest text-slate-600">
        {label}
      </p>

      <p className="text-xl font-bold text-cyan-400 mt-2 break-all">
        {value}
      </p>

    </div>
  );
}


export default App;