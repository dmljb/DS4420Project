import React from "react";
import "./App.css";

export default function ModelResults() {
  return (
    <div className="dashboard">
      <h1>Model Results</h1>

      <div className="graph-grid">

        {/* Neural Network Graph */}
        <div className="graph-card">
          <h3>Neural Network: Actual vs Predicted Yields</h3>
          <img src="/DS4420Project/graphs/nn.png" alt="NN Results" />
        </div>

        {/* Bayesian Graph */}
        <div className="graph-card">
          <h3>Bayesian Model: Out-of-Sample Test Results</h3>
          <img src="/DS4420Project/graphs/BayesianResults.png" alt="Bayesian Results" />
        </div>

      </div>
    </div>
  );
}
