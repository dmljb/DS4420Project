import React, { useState, useEffect } from "react";
import "./App.css";
import YieldCurveHistory from "./YieldCurveHistory";
import ModelResults from "./ModelResults";
import InteractiveEnsemblePlot from "./InteractiveEnsemblePlot";


const API_BASE =
  window.location.hostname === "localhost"
    ? "http://localhost:5050"
    : "https://ds4420-backend.onrender.com";

function truncate(text: string, max: number = 300): string {
  if (text.length <= max) return text;

  const cutoff = text.slice(0, max);
  const lastPeriod = cutoff.lastIndexOf(".");
  
  if (lastPeriod > 0) {
    return cutoff.slice(0, lastPeriod + 1);
  }

  return cutoff + "...";
}

interface MetricProps {
  label: string;
  value: number | string;
}

function Metric({ label, value }: MetricProps) {
  const num = Number(value);

  let color = "#e5e5e5";

if (label.includes("Policy Bias") && num <= -0.5) color = "#4cd964";
if (label.includes("Policy Bias") && num >= 0.5) color = "#ff3b30";

if (label.includes("Expected Move") && num <= -10) color = "#4cd964";
if (label.includes("Expected Move") && num >= 10) color = "#ff3b30";

if (label.includes("Inflation") && num >= 0.7) color = "#ff8c42";


  return (
    <div className="metric">
      <span>{label}</span>
      <span style={{ color }}>{num}</span>
    </div>
  );
}

// Define TypeScript interfaces
interface BondData {
  present_value: number;
  dv01: number;
  face_value: number;
  coupon_rate: number;
}

interface PortfolioData {
  portfolio_present_value: number;
  portfolio_dv01: number;
  portfolio_duration: number;
  number_of_bonds: number;
}

interface YieldCurveData {
  maturities: number[];
  rates: number[];
  curve_type: string;
}

interface PredictionSummary {
  date: string;
  maturities: number[];
  predicted_rates: number[];
  current_rates: number[];
  avg_current_yield: number;
  avg_predicted_yield: number;
  base_present_value: number;
  predicted_present_value: number;
  pnl_dollar: number;
  pnl_percent: number;
}

function App() {
  const [bondData, setBondData] = useState<BondData | null>(null);
  const [portData, setPortData] = useState<PortfolioData | null>(null);
  const [yieldCurve, setYieldCurve] = useState<YieldCurveData | null>(null);
  const [prediction, setPrediction] = useState<PredictionSummary | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<"dashboard" | "yield_history" | "model_results" | "interactive"
  >("dashboard");

  const [recoText, setRecoText] = useState<string | null>(null);
  const [recoLoading, setRecoLoading] = useState(false);
  const [recoError, setRecoError] = useState<string | null>(null);

  const [minuteText, setMinuteText] = useState<any>(null);
  const [rawNews, setRawNews] = useState<string | null>(null);
  const [minuteError, setMinuteError] = useState<string | null>(null);
  const [minuteLoading, setMinuteLoading] = useState<boolean>(false);

  // ----------------------------------
  // FETCH: Minute Analysis
  // ----------------------------------
  const fetchMinuteAnalysis = async () => {
    setMinuteLoading(true);
    setMinuteError(null);

    try {
      const response = await fetch(`${API_BASE}/api/minute_analysis`);
      if (!response.ok) {
        throw new Error(`Minute analysis API error! status: ${response.status}`);
      }
      const data = await response.json();
      setMinuteText(data.analysis);
      setRawNews(data.raw_news || null);
    } catch (err) {
      console.error("Error fetching minute analysis:", err);
      setMinuteError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setMinuteLoading(false);
    }
  };

  // ----------------------------------
  // INITIAL LOAD
  // ----------------------------------
  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchBondData(),
      fetchPortData(),
      fetchYieldData(),
      fetchPredictionData(),
      fetchMinuteAnalysis(),
    ])
      .then(() => setLoading(false))
      .catch(() => setLoading(false));
  }, []); // eslint-disable-line

  // ----------------------------------
  // FETCH HELPERS
  // ----------------------------------
  const fetchBondData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/bond`);
      if (!response.ok) throw new Error(`Bond API error! status: ${response.status}`);
      const data = await response.json();
      setBondData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown bond error");
      console.error(err);
    }
  };

  const fetchPortData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/portfolio`);
      if (!response.ok) throw new Error(`Portfolio API error! status: ${response.status}`);
      const data = await response.json();
      setPortData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown portfolio error");
      console.error(err);
    }
  };

  const fetchYieldData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/yield_curve`);
      if (!response.ok) throw new Error(`Yield Curve API error! status: ${response.status}`);
      const data = await response.json();
      setYieldCurve(data);
    } catch (err) {
      console.error("Error fetching yield curve:", err);
    }
  };

  const fetchPredictionData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/yield_predictions`);
      if (!response.ok) throw new Error(`Prediction API error! status: ${response.status}`);
      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      console.error("Prediction fetch failed:", err);
    }
  };

  // ----------------------------------
  // RETRY
  // ----------------------------------
  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setBondData(null);
    setPortData(null);
    setYieldCurve(null);
    setPrediction(null);
    setRecoText(null);
    setRecoError(null);

    Promise.all([fetchBondData(), fetchPortData(), fetchYieldData(), fetchPredictionData()])
      .then(() => setLoading(false))
      .catch(() => setLoading(false));
  };

  // ----------------------------------
  // AI RECOMMENDATION
  // ----------------------------------
  const handleAskAI = async () => {
    setRecoLoading(true);
    setRecoError(null);
    try {
      const response = await fetch(`${API_BASE}/api/recommendation`);
      if (!response.ok) throw new Error(`Recommendation error: ${response.status}`);
      const data = await response.json();
      setRecoText(data.recommendation);
    } catch (err) {
      console.error("Reco error:", err);
      setRecoError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setRecoLoading(false);
    }
  };

  // ----------------------------------
  // LOADING / ERROR UI
  // ----------------------------------
  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading portfolio data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error">
          Error: {error}
          <button onClick={handleRetry} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  // PAGE SWITCH: Yield Curve History
  if (page === "yield_history") {
    return (
      <div className="dashboard">
        <div className="navbar">
          <button onClick={() => setPage("dashboard")}>Dashboard</button>
          <button onClick={() => setPage("yield_history")}>Yield Curve History</button>
          <button onClick={() => setPage("model_results")}>Model Results</button>
          <button onClick={() => setPage("interactive")}>Interactive Plot</button>
        </div>
        <YieldCurveHistory />
        <div className="controls">
          <button onClick={handleRetry} className="refresh-btn">Refresh All Data</button>
        </div>
      </div>
    );
  }

  if (page === "model_results") {
  return (
    <div className="dashboard">
      <div className="navbar">
        <button onClick={() => setPage("dashboard")}>Dashboard</button>
        <button onClick={() => setPage("yield_history")}>Yield Curve History</button>
        <button onClick={() => setPage("model_results")}>Model Results</button>
        <button onClick={() => setPage("interactive")}>Interactive Plot</button>
      </div>
      <ModelResults />
    </div>
  );
}

if (page === "interactive") {
  return (
    <div className="dashboard">
      <div className="navbar">
        <button onClick={() => setPage("dashboard")}>Dashboard</button>
        <button onClick={() => setPage("yield_history")}>Yield Curve History</button>
        <button onClick={() => setPage("model_results")}>Model Results</button>
        <button onClick={() => setPage("interactive")}>Interactive Plot</button>
      </div>

      <InteractiveEnsemblePlot />
    </div>
  );
}


  const pnlIsPositive = prediction ? prediction.pnl_dollar >= 0 : false;

  // ----------------------------------
  // MAIN DASHBOARD
  // ----------------------------------
  return (
    <div className="dashboard">
      <div className="navbar">
        <button onClick={() => setPage("dashboard")}>Dashboard</button>
        <button onClick={() => setPage("yield_history")}>Yield Curve History</button>
        <button onClick={() => setPage("model_results")}>Model Results</button>
        <button onClick={() => setPage("interactive")}>Interactive Plot</button>
      </div>

      <h1>Portfolio Dashboard</h1>

      {/* Portfolio Cards */}
      {portData && (
        <div className="portfolio-section">
          <h2>Portfolio Overview</h2>
          <div className="metrics-container">
            <div className="metrics">
              <h3>Value</h3>
              <div className="value">
                ${portData.portfolio_present_value.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>

            <div className="metrics">
              <h3>DV01</h3>
              <div className="value">
                ${portData.portfolio_dv01.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>

            <div className="metrics">
              <h3>Macaulay Duration</h3>
              <div className="value">
                {portData.portfolio_duration?.toLocaleString("en-US") || "N/A"}
              </div>
            </div>

            <div className="metrics">
              <h3>Number of Bonds</h3>
              <div className="value">{portData.number_of_bonds || "N/A"}</div>
            </div>
          </div>
        </div>
      )}

      {/* Prediction Section */}
      {prediction && (
        <div className="prediction-section">
          <h2>Model Yield Forecast (Latest NN Prediction)</h2>

          <div className="metrics-container">
            <div className="metrics">
              <h3>Avg Current Yield (1Y–10Y)</h3>
              <div className="value">{prediction.avg_current_yield.toFixed(2)}%</div>
            </div>

            <div className="metrics">
              <h3>Avg Predicted Yield</h3>
              <div className="value">{prediction.avg_predicted_yield.toFixed(2)}%</div>
            </div>

            <div
              className="metrics pnl-card"
              style={{
                backgroundColor: pnlIsPositive
                  ? "rgba(0, 255, 0, 0.45)"
                  : "rgba(255, 0, 0, 0.45)",
                border: "1px solid rgba(255,255,255,0.2)",
                borderRadius: "20px",
                transition: "0.3s ease",
              }}
            >
              <h3>Expected Portfolio P&L</h3>
              <div className="value">
                {pnlIsPositive ? "+" : "-"}$
                {Math.abs(prediction.pnl_dollar).toLocaleString("en-US", {
                  maximumFractionDigits: 0,
                })}{" "}
                ({prediction.pnl_percent.toFixed(2)}%)
              </div>
            </div>
          </div>

          <div className="prediction-mini">
            <span className="mini-title">Predicted Yields by Maturity:</span>
            <span>1Y: {prediction.predicted_rates[0].toFixed(2)}%</span>
            <span>2Y: {prediction.predicted_rates[1].toFixed(2)}%</span>
            <span>5Y: {prediction.predicted_rates[2].toFixed(2)}%</span>
            <span>10Y: {prediction.predicted_rates[3].toFixed(2)}%</span>
          </div>
        </div>
      )}

      {/* Bond Cards */}
      {bondData && (
        <div className="bond-section">
          <h2>Individual Bonds</h2>
          <div className="bond-cards">
            <div className="card">
              <h3>Bond Present Value</h3>
              <div className="value">
                ${bondData.present_value.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>

            <div className="card">
              <h3>Bond DV01</h3>
              <div className="value">
                ${bondData.dv01.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </div>
            </div>

            <div className="card">
              <h3>Face Value</h3>
              <div className="value">${bondData.face_value.toLocaleString("en-US")}</div>
            </div>

            <div className="card">
              <h3>Coupon Rate</h3>
              <div className="value">{(bondData.coupon_rate * 100).toFixed(2)}%</div>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------- */}
      {/* CLEAN Minute-by-Minute Market Analysis (LLM) */}
      {/* ------------------------------------------- */}

      <div className="ai-section">
        <h2>Minute-Level Market Analysis (LLM)</h2>

        <button
          onClick={fetchMinuteAnalysis}
          className="refresh-btn"
          disabled={minuteLoading}
        >
          {minuteLoading ? "Fetching..." : "Refresh Minute Analysis"}
        </button>

        {minuteError && <p className="ai-error">{minuteError}</p>}

        {minuteText && (
  <div className="analysis-section">
    <div className="analysis-block policy">
      <h4>Policy Stance</h4>
      <Metric label="Policy Bias" value={minuteText.policy_bias} />
      <Metric label="Expected Move (bps)" value={minuteText.expected_move_bps} />
      <Metric label="Guidance Strength" value={minuteText.guidance_strength} />
      <Metric label="Balance Sheet Signal" value={minuteText.balance_sheet_signal} />
    </div>

    <div className="analysis-block macro">
      <h4>Macro Tones</h4>
      <Metric label="Inflation Tone" value={minuteText.inflation_tone} />
      <Metric label="Labor Tone" value={minuteText.labor_tone} />
      <Metric label="Growth Tone" value={minuteText.growth_tone} />
      <Metric label="Financial Conditions Tone" value={minuteText.financial_conditions_tone} />
    </div>

    <div className="analysis-block rate">
      <h4>Rate Probabilities</h4>
      <Metric label="P(Cut)" value={minuteText.p_cut} />
      <Metric label="P(Hold)" value={minuteText.p_hold} />
      <Metric label="P(Hike)" value={minuteText.p_hike} />
    </div>

  </div>
)}


{/*  ADD RAW NEWS DISPLAY HERE */}
{rawNews && (
  <div className="news-section">
    <h3>Latest Market Headlines</h3>

    {rawNews.split("\n\n").map((item, i) => (
      <div key={i} className="news-item">
        <p>{truncate(item)}</p>
      </div>
    ))}
  </div>
)}

      </div>

      {/* AI Recommendation */}
      <div className="ai-section">
        <h2>AI Recommendation (Gemini)</h2>

        <button
          onClick={handleAskAI}
          className="refresh-btn"
          disabled={recoLoading}
        >
          {recoLoading ? "Asking Gemini..." : "Get Recommendation"}
        </button>

        {recoError && <p className="ai-error">{recoError}</p>}
        {recoText && <p className="ai-text">{recoText}</p>}
      </div>

      <div className="controls">
        <button onClick={handleRetry} className="refresh-btn">
          Refresh All Data
        </button>
      </div>
    </div>
  );
}

export default App;
