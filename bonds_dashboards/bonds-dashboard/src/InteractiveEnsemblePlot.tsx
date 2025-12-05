import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import * as d3 from "d3";

const maturities = ["GS1", "GS2", "GS5", "GS10"];

interface SeriesBundle {
  actual: number[];
  bayes: number[];
  nn: number[];
  ensemble: number[];
  months: number[];
}

export default function InteractiveEnsemblePlot() {
  const [selected, setSelected] = useState("GS10");
  const [data, setData] = useState<Record<string, SeriesBundle> | null>(null);

  const BASE = import.meta.env.BASE_URL;

  useEffect(() => {
    Promise.all([
      d3.csv(`${BASE}actual_yields.csv`),
      d3.csv(`${BASE}bayesian_predictions.csv`),
      d3.csv(`${BASE}nn_predictions.csv`)
    ]).then(([actual, bayes, nn]) => {
      const months = actual.map((_, i) => i + 1);
      const combined: Record<string, SeriesBundle> = {};

      maturities.forEach((maturity) => {
        const actualSeries = actual.map((d) => +d[maturity]);
        const bayesSeries = bayes.map((d) => +d[maturity]);
        const nnSeries = nn.map((d) => +d[`${maturity}_pred`]);
        const ensembleSeries = nnSeries.map(
          (_, i) => (nnSeries[i] + bayesSeries[i]) / 2
        );

        combined[maturity] = {
          actual: actualSeries,
          bayes: bayesSeries,
          nn: nnSeries,
          ensemble: ensembleSeries,
          months
        };
      });

      setData(combined);
    });
  }, []);

  if (!data) return <p>Loading interactive ensemble plot...</p>;

  const series = data[selected];

  return (
    <div>
      <h2>Interactive Ensemble Yield Forecast</h2>

      <label>
        Select maturity:{" "}
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {maturities.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </label>

      <Plot
        data={[
          {
            x: series.months,
            y: series.actual,
            type: "scatter",
            mode: "lines+markers",
            name: "Actual",
            line: { color: "black", width: 2 }
          },
          {
            x: series.months,
            y: series.bayes,
            type: "scatter",
            mode: "lines+markers",
            name: "Bayesian",
            line: { color: "blue", dash: "dot" }
          },
          {
            x: series.months,
            y: series.nn,
            type: "scatter",
            mode: "lines+markers",
            name: "Neural Network",
            line: { color: "red", dash: "dash" }
          },
          {
            x: series.months,
            y: series.ensemble,
            type: "scatter",
            mode: "lines+markers",
            name: "Ensemble",
            line: { color: "green", width: 3 }
          }
        ]}
        layout={{
          width: 900,
          height: 600,
          title: `${selected} Ensemble Prediction`,
          xaxis: { title: "Test Month" },
          yaxis: { title: "Yield (%)" },
          hovermode: "closest"
        }}
      />
    </div>
  );
}