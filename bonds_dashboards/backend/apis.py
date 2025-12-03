from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path
import pandas as pd

from finance.bonds import Bonds, bond_issuing_date, b1, b2
from finance.portfolio import Portfolio, p1
from finance.yield_curve import curve
from llm.llm_calls import (
    build_portfolio_recommendation,
    minute_analysis,
    fetch_market_news
)

app = Flask(__name__)
CORS(app)

# ---------- LOAD NN PREDICTIONS ONCE ----------

def _load_predictions_df():
    """
    Load NN yield predictions from data/nn_predictions_multi_output_2018_2024.csv
    and normalize the date column.
    """
    root = Path(__file__).resolve().parents[2]          # DS4420PROJECT
    pred_path = root / "data" / "nn_predictions_multi_output_2018_2024.csv"
    df = pd.read_csv(pred_path, parse_dates=["Unnamed: 0"])
    df = df.rename(columns={"Unnamed: 0": "date"})
    return df

PRED_DF = _load_predictions_df()


def compute_prediction_summary():
    """
    Use the latest NN prediction to build:
    - predicted yields for 1Y/2Y/5Y/10Y
    - current market yields from `curve`
    - approximate portfolio P&L using DV01 and avg level move
    """
    latest = PRED_DF.iloc[-1]

    maturities = [1, 2, 5, 10]
    predicted_rates = [
        float(latest["treasury_1y_pred"]),
        float(latest["treasury_2y_pred"]),
        float(latest["treasury_5y_pred"]),
        float(latest["treasury_10y_pred"]),
    ]

    current_rates = []
    for m in maturities:
        try:
            idx = curve.maturities.index(m)
            current_rates.append(float(curve.rates[idx]))
        except ValueError:
            current_rates.append(float(curve.rates[-1]))

    avg_current = sum(current_rates) / len(current_rates)
    avg_pred = sum(predicted_rates) / len(predicted_rates)

    base_summary = p1.get_portfolio_summary(curve)
    base_pv = float(base_summary["portfolio_present_value"])
    dv01 = float(base_summary["portfolio_dv01"])

    delta_bps = (avg_pred - avg_current) * 100.0

    predicted_pv = base_pv + dv01 * delta_bps
    pnl = predicted_pv - base_pv
    pnl_pct = (pnl / base_pv * 100.0) if base_pv != 0 else 0.0

    return {
        "date": latest["date"].strftime("%Y-%m-%d"),
        "maturities": maturities,
        "predicted_rates": predicted_rates,
        "current_rates": current_rates,
        "avg_current_yield": avg_current,
        "avg_predicted_yield": avg_pred,
        "base_present_value": base_pv,
        "predicted_present_value": predicted_pv,
        "pnl_dollar": pnl,
        "pnl_percent": pnl_pct,
    }


@app.route("/api/bond")
def get_bond_data():
    b1_local = Bonds(bond_issuing_date, 1000, 0.04, 10)

    return jsonify(
        {
            "present_value": b1_local.present_value(curve),
            "dv01": b1_local.dv01(curve),
            "face_value": b1_local.face_value,
            "coupon_rate": b1_local.bond_interest,
        }
    )


@app.route("/api/portfolio")
def get_portfolio_data():
    try:
        portfolio_summary = p1.get_portfolio_summary(curve)
        return jsonify(portfolio_summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/yield_curve")
def get_yield_curve():
    try:
        return jsonify(
            {
                "maturities": curve.maturities,
                "rates": curve.rates,
                "curve_type": "Treasury Zero Rates",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/yield_predictions")
def get_yield_predictions():
    """
    Latest NN yield forecast + implied portfolio impact.
    """
    try:
        pred_summary = compute_prediction_summary()
        return jsonify(pred_summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommendation")
def get_recommendation():
    """
    Generate a portfolio recommendation using:
    - Portfolio summary
    - NN model predictions
    - Real-time macro signals (LLM-extracted)
    - Cleaned market news headlines
    """

    try:
        portfolio_summary = p1.get_portfolio_summary(curve)
        pred_summary = compute_prediction_summary()

        macro = minute_analysis(
            "Generate a numeric policy-feature vector.", 
            debug=True
        )

        news = fetch_market_news()

        text = build_portfolio_recommendation(
            portfolio_summary=portfolio_summary,
            prediction_summary=pred_summary,
            macro_signals=macro,
            news_headlines=news,
            debug=True,
        )

        return jsonify({
            "recommendation": text,
            "macro_used": macro,
            "news_used": news
        })

    except Exception as e:
        import traceback
        print("\n\n🔥 ERROR IN /api/recommendation:")
        traceback.print_exc()
        print("Error message:", e, "\n\n")
        return jsonify({"error": str(e)}), 500


@app.route("/api/minute_analysis")
def api_minute_analysis():
    try:
        news_text = fetch_market_news()

        analysis = minute_analysis(news_text, debug=True)

        return jsonify({
            "analysis": analysis,
            "raw_news": news_text
        })

    except Exception as e:
        import traceback
        print("\n\n🔥 ERROR IN /api/minute_analysis:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)