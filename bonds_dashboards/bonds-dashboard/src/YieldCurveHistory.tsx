import React, { useEffect, useState } from "react";
import * as d3 from "d3";

interface CurveRow {
  date: string;
  treasury_1y: number;
  treasury_2y: number;
  treasury_5y: number;
  treasury_10y: number;
}

export default function YieldCurveHistory() {
  const [data, setData] = useState<CurveRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    d3.csv("/yield_history.csv").then((rows: any[]) => {
      const parsed = rows.map((r) => ({
        date: r.date,
        treasury_1y: +r.treasury_1y,
        treasury_2y: +r.treasury_2y,
        treasury_5y: +r.treasury_5y,
        treasury_10y: +r.treasury_10y,
      }));
      setData(parsed);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading yield history…</div>;

  const moves = data.slice(1).map((d, i) => d.treasury_10y - data[i].treasury_10y);

  return (
    <div style={{ padding: "20px", color: "white" }}>
      <h1>Yield Curve History</h1>

      <p style={{ maxWidth: "600px", color: "white" }}>
        The yield curve summarizes interest rates across different maturities.
        A normal curve slopes upward. When short-term yields rise above long-term
        yields (an inversion), it is historically associated with recession risk.
      </p>

      <h2 style={{ color: "white" }}>10-Year Monthly Yield Moves (Histogram)</h2>
      <YieldHistogram moves={moves} />

      <h2 style={{ color: "white" }}>Yield Curve Snapshot (Latest Month)</h2>
      <YieldCurvePlot row={data[data.length - 1]} />

      <p style={{ fontSize: "14px", marginTop: "20px", color: "#ddd" }}>
        Data source: FRED / cleaned dataset. The visuals help detect inversions,
        steepening, and flattening.
      </p>
    </div>
  );
}


function YieldHistogram({ moves }: { moves: number[] }) {
  const ref = React.useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const width = 600;
    const height = 260;

    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    const raw = d3.extent(moves) as [number, number];
    const padded = [raw[0] - 0.2, raw[1] + 0.2];

    const x = d3.scaleLinear().domain(padded).range([50, width - 20]);

    const bins = d3.bin().domain(padded).thresholds(15)(moves);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(bins, (b) => b.length) || 1])
      .range([height - 40, 20]);

    svg
      .append("g")
      .selectAll("rect")
      .data(bins)
      .enter()
      .append("rect")
      .attr("x", (d) => x(d.x0 || 0))
      .attr("y", (d) => y(d.length))
      .attr("width", (d) => Math.max(0, x(d.x1 || 0) - x(d.x0 || 0) - 1))
      .attr("height", (d) => (height - 40) - y(d.length))
      .attr("fill", "#a3c8ff");

    // X axis
    svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", `translate(0,${height - 40})`)
      .call(d3.axisBottom(x));

    // X label
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height - 5)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .text("Monthly Change in 10-Year Yield (%)");

    // Y axis
    svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", `translate(50,0)`)
      .call(d3.axisLeft(y));

    // Y label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", 15)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .text("Number of Months");
  }, [moves]);

  return <svg ref={ref} width={600} height={260} style={{ overflow: "visible" }}></svg>;
}


function YieldCurvePlot({ row }: { row: CurveRow }) {
  const ref = React.useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const maturities = [1, 2, 5, 10];
    const rates = [
      row.treasury_1y,
      row.treasury_2y,
      row.treasury_5y,
      row.treasury_10y,
    ];

    const width = 600;
    const height = 300;

    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    const x = d3.scalePoint<number>().domain(maturities).range([60, width - 40]);
    const y = d3
      .scaleLinear()
      .domain([0, (d3.max(rates) || 5) + 1])
      .range([height - 40, 20]);

    svg
      .append("path")
      .datum(rates)
      .attr("d", d3.line<number>()
        .x((_, i) => x(maturities[i])!)
        .y((v) => y(v)) as any)
      .attr("fill", "none")
      .attr("stroke", "#00ff99")
      .attr("stroke-width", 3);

    svg
      .selectAll("circle")
      .data(rates)
      .enter()
      .append("circle")
      .attr("cx", (_, i) => x(maturities[i])!)
      .attr("cy", (d) => y(d))
      .attr("r", 7)
      .attr("fill", "white")
      .attr("stroke", "#00cc66")
      .attr("stroke-width", 3);

    // X axis
    svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", `translate(0,${height - 40})`)
      .call(d3.axisBottom(x));

    // X label
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height - 5)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .text("Maturity (Years)");

    // Y axis
    svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", `translate(60,0)`)
      .call(d3.axisLeft(y));

    // Y label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", 15)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .text("Yield (%)");
  }, [row]);

  return <svg ref={ref} width={600} height={300} style={{ overflow: "visible" }}></svg>;
}