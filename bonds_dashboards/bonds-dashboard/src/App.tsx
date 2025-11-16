import React, { useState, useEffect } from 'react';
import './App.css';

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

function App() {
  const [bondData, setBondData] = useState<BondData | null>(null);
  const [portData, setPortData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // const [currentScenario, setCurrentScenario] = useState('base');

  useEffect(() => {
    // Fetch both data sources
    Promise.all([fetchBondData(), fetchPortData()])
      .then(() => {
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const fetchBondData = async () => {
    try {
      const response = await fetch('http://localhost:5050/api/bond');
      
      if (!response.ok) {
        throw new Error(`Bond API error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setBondData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error fetching bond data:', err);
    }
  };

  const fetchPortData = async () => {
    try {
      const response = await fetch('http://localhost:5050/api/portfolio');
      
      if (!response.ok) {
        throw new Error(`Portfolio API error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setPortData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error fetching portfolio data:', err);
    }
  };

  const ScenarioControls = ({onScenarioChange, currentScenario}) => {
    const scenarios = [
      {id: 'base', label: 'Base Case'},
      {id: 'Fed raises 100bp', label: '100bps'},
      { id: 'recession', label: 'Recession' }
    ];

  return (
    <div className="control-panel">
      <h3>Rate Scenarios</h3>
      {scenarios.map(scenario => (
        <button 
          key={scenario.id}
          onClick={() => onScenarioChange(scenario.id)}
          className={`scenario-btn ${currentScenario === scenario.id ? 'active' : ''}`}
        >
          {scenario.label}
        </button>
      ))}
    </div>
  );
};


const handleScenarioChange = (scenario) => {
  setCurrentScenario(scenario);
  // Later you'll fetch new data based on this scenario
};


  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setBondData(null);
    setPortData(null);
    
    Promise.all([fetchBondData(), fetchPortData()])
      .then(() => {
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

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
          <button onClick={handleRetry} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>Portfolio Dashboard</h1>
      
      {/* Portfolio Cards - Only show if portData exists */}
      {portData && (
        <div className="portfolio-section">
          <h2>Portfolio Overview</h2>
          <div className="metrics-container">
            <div className="metrics">
              <h3>Value</h3>
              <div className="value">
                ${portData.portfolio_present_value.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </div>
            </div>

            <div className="metrics">
              <h3>DV01</h3>
              <div className="value">
                ${portData.portfolio_dv01.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </div>
            </div>

            <div className="metrics">
              <h3>Macaulay Duration</h3>
              <div className="value">
                {portData.portfolio_duration?.toLocaleString('en-US') || 'N/A'}
              </div>
            </div>

            <div className="metrics">
              <h3>Number of Bonds</h3>
              <div className="value">{portData.number_of_bonds || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Individual Bond Cards - Only show if bondData exists */}
      {bondData && (
        <div className="bond-section">
          <h2>Individual Bonds</h2>
          <div className="bond-cards">
            <div className="card">
              <h3>Bond Present Value</h3>
              <div className="value">
                ${bondData.present_value.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </div>
            </div>

            <div className="card">
              <h3>Bond DV01</h3>
              <div className="value">
                ${bondData.dv01.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </div>
            </div>

            <div className="card">
              <h3>Face Value</h3>
              <div className="value">
                ${bondData.face_value.toLocaleString('en-US')}
              </div>
            </div>

            <div className="card">
              <h3>Coupon Rate</h3>
              <div className="value">
                {(bondData.coupon_rate * 100).toFixed(2)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Show message if no data */}
      {!portData && !bondData && !loading && !error && (
        <div className="no-data">
          <p>No data available. Please check your API endpoints.</p>
        </div>
      )}

      <div className="controls">
        <button onClick={handleRetry} className="refresh-btn">
          Refresh All Data
        </button>
      </div>
    </div>
  );
}

export default App;