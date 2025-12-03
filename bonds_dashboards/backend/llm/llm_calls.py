import os
from dotenv import load_dotenv

load_dotenv(override=True)

TAVILY_KEY = os.getenv("TAVILY_KEY")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")

from tavily import TavilyClient
tavily_client = TavilyClient(api_key=TAVILY_KEY)

import google.generativeai as genai
genai.configure(api_key=GEMINI_KEY)

llm = genai.GenerativeModel("models/gemini-2.5-flash")

import json
import re
import logging


def fetch_market_news():
    """
    Fetches macro / Fed / bond-market headlines and returns
    extremely clean, short summaries only (2 sentences max).
    """

    try:
        result = tavily_client.search(
            query="Federal Reserve interest rates bond yields inflation treasury market outlook",
            time_range="day",
            max_results=8,
            include_answer=False
        )

        clean_articles = []

        for r in result.get("results", []):
            title = r.get("title", "").strip()
            content = r.get("content", "").strip()

            if not content or len(content) < 40:
                continue

            blacklist_patterns = [
                r"Skip to.*", r"Cookie.*", r"User Menu.*", r"Menu.*",
                r"Search.*", r"Related news.*", r"General Public.*",
                r"Alerts.*", r"Export.*", r"Stats.*", r"Share.*",
                r"Forex.*", r"Crypto.*", r"\bEN\b.*\bEN\b.*",
                r"Canada.*English.*", r"Français.*", r"Português.*",
                r"Deutsch.*", r"Italiano.*", r"Polski.*", r"Русский.*"
            ]

            for pat in blacklist_patterns:
                content = re.sub(pat, "", content, flags=re.IGNORECASE)

            content = re.sub(r"http\S+", "", content)

            content = re.sub(r"[\*\[\]\(\)#]", "", content)

            content = re.sub(r"(\b\d{1,3}\.\d{1,3}\b\s*){3,}", "", content)

            content = " ".join(content.split())

            sentences = re.split(r"(?<=[.!?])\s+", content)
            content = " ".join(sentences[:2])

            if len(content) < 40:
                continue

            clean_articles.append(f"{title}: {content}")

        if not clean_articles:
            return "No clean market news available."

        return "\n\n".join(clean_articles)

    except Exception as e:
        print("Tavily error:", e)
        return "No news could be retrieved."


def minute_analysis(text, debug=True):
    """
    Extract numeric policy features from FOMC minutes for neural network input.
    Returns dict with 11 numeric features ready for MLP.
    """

    # If user passed placeholder text, auto-fetch real market news
    if text.strip().startswith("Generate a numeric policy-feature"):
        if debug:
            print("minute_analysis(): Detected placeholder, fetching real news.")
        text = fetch_market_news()

    # Truncate very long text to avoid token limits
    if len(text) > 15000:
        text = text[:15000] + "..."
        if debug:
            print(f"Truncated text to {len(text)} characters")

    prompt = f"""
You convert FOMC minutes into NUMERIC policy features for machine learning.
Answer with ONLY a JSON object, no markdown formatting.

Extract these 11 numeric features:

Schema (exact keys required):
{{
  "policy_bias": 0.0,              // -1.0 (dovish) to +1.0 (hawkish)
  "guidance_strength": 0.0,        // 0.0 to 1.0 (confidence in forward guidance)
  "expected_move_bps": 0,          // Expected basis points: -50, -25, 0, +25, +50
  "p_cut": 0.0,                    // Probability of rate cut (0.0 to 1.0)
  "p_hold": 0.0,                   // Probability of rate hold (0.0 to 1.0)
  "p_hike": 0.0,                   // Probability of rate hike (0.0 to 1.0)
  "inflation_tone": 0.0,           // 0.0 to 1.0 (higher = more inflation concern)
  "labor_tone": 0.0,               // 0.0 to 1.0 (higher = tighter labor market)
  "growth_tone": 0.0,              // 0.0 to 1.0 (higher = stronger growth outlook)
  "financial_conditions_tone": 0.0,// 0.0 to 1.0 (higher = tighter conditions)
  "balance_sheet_signal": 0.0      // -1.0 to +1.0 (QT>0, QE<0, neutral=0)
}}

Rules:
- p_cut + p_hold + p_hike must sum to 1.0
- Only return JSON, no text before or after
- Use decimal values like 0.75, not percentages

FOMC Minutes Text:
{text}
"""

    try:
        response = llm.generate_content(prompt)
        raw_content = response.text.strip()

        if debug:
            print(f"Raw LLM response length: {len(raw_content)}")
            print(f"First 200 chars: {raw_content[:200]}")

        if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content,
                                 flags=re.MULTILINE).strip()
        
        try:
            obj = json.loads(raw_content)
        except json.JSONDecodeError as e:
            if debug:
                print(f"JSON parse error: {e}")
                print(f"Content: {raw_content}")
            return get_default_features()
        
        return validate_and_clean_features(obj, debug=debug)
        
    except Exception as e:
        if debug:
            print(f"LLM call failed: {e}")
        return get_default_features()



def validate_and_clean_features(obj, debug=False):
    """Validate and normalize LLM output features"""
    
    required_keys = {
        "policy_bias", "guidance_strength", "expected_move_bps",
        "p_cut", "p_hold", "p_hike", "inflation_tone", "labor_tone", 
        "growth_tone", "financial_conditions_tone", "balance_sheet_signal"
    }
    
    missing_keys = required_keys - set(obj.keys())
    if missing_keys:
        if debug:
            print(f"Missing keys: {missing_keys}")
        defaults = get_default_features()
        for key in missing_keys:
            obj[key] = defaults[key]
    
    try:
        obj["policy_bias"] = max(-1.0, min(1.0, float(obj["policy_bias"])))
        obj["balance_sheet_signal"] = max(-1.0, min(1.0, float(obj["balance_sheet_signal"])))
        
        for key in ["guidance_strength", "p_cut", "p_hold", "p_hike",
                   "inflation_tone", "labor_tone", "growth_tone",
                   "financial_conditions_tone"]:
            obj[key] = max(0.0, min(1.0, float(obj[key])))
        
        obj["expected_move_bps"] = int(round(float(obj["expected_move_bps"])))
        
        prob_sum = obj["p_cut"] + obj["p_hold"] + obj["p_hike"]
        if prob_sum > 0:
            obj["p_cut"] /= prob_sum
            obj["p_hold"] /= prob_sum
            obj["p_hike"] /= prob_sum
        else:
            obj["p_cut"], obj["p_hold"], obj["p_hike"] = 0.0, 1.0, 0.0
            
    except (ValueError, TypeError) as e:
        if debug:
            print(f"Type conversion error: {e}")
        return get_default_features()
    
    return obj


def get_default_features():
    """Return default feature values when LLM fails"""
    return {
        "policy_bias": 0.0,
        "guidance_strength": 0.5,
        "expected_move_bps": 0,
        "p_cut": 0.33,
        "p_hold": 0.34, 
        "p_hike": 0.33,
        "inflation_tone": 0.5,
        "labor_tone": 0.5,
        "growth_tone": 0.5,
        "financial_conditions_tone": 0.5,
        "balance_sheet_signal": 0.0
    }

def build_portfolio_recommendation(
    portfolio_summary: dict,
    prediction_summary: dict,
    macro_signals: dict = None,
    news_headlines: str = None,
    debug: bool = False
) -> str:
    """
    Portfolio recommendation using:
    - Model predictions
    - Macro policy signals
    - Real-world news
    """

    try:
        macro_text = json.dumps(macro_signals, indent=2) if macro_signals else "None"
        news_text = news_headlines if news_headlines else "No news available."

        payload = {
            "portfolio": {
                "present_value": portfolio_summary.get("portfolio_present_value"),
                "dv01": portfolio_summary.get("portfolio_dv01"),
                "duration": portfolio_summary.get("portfolio_duration"),
                "avg_coupon": portfolio_summary.get("average_coupon"),
                "avg_maturity": portfolio_summary.get("average_maturity"),
            },
            "prediction": {
                "date": prediction_summary.get("date"),
                "maturities": prediction_summary.get("maturities"),
                "current_rates": prediction_summary.get("current_rates"),
                "predicted_rates": prediction_summary.get("predicted_rates"),
                "avg_current_yield": prediction_summary.get("avg_current_yield"),
                "avg_predicted_yield": prediction_summary.get("avg_predicted_yield"),
                "pnl_dollar": prediction_summary.get("pnl_dollar"),
                "pnl_percent": prediction_summary.get("pnl_percent"),
            },
            "macro_signals_used": macro_signals,
            "news_used": news_headlines,
        }

        prompt = f"""
You are a fixed-income portfolio strategist.

Blend the following inputs:
1) QUANT MODEL FORECAST
2) REAL-TIME MACRO SIGNALS (policy bias, tones, expected move)
3) TODAY'S MARKET HEADLINES

Your job is to interpret whether the NEWS reinforces or contradicts the MODEL.
Adjust your recommendation accordingly.

DATA:
{json.dumps(payload, indent=2)}

Macro signals (structured from LLM):
{macro_text}

Market Headlines (cleaned, short):
{news_text}

INSTRUCTIONS:
- Identify whether news is hawkish, dovish, or mixed.
- Compare macro tones versus model predictions.
- State whether cuts/hikes look more or less likely because of the news.
- State the likely direction of yields.
- Explain how this affects the portfolio's DV01 and duration exposure.
- End with ONE ACTION PHRASE:
  "Add duration", "Reduce duration", "Hold as is", "Hedge duration", or "Shift to belly".

Keep it under 130 words. Do NOT mention being an AI model.
Return plain text only.
"""

        response = llm.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        if debug:
            print("build_portfolio_recommendation failed:", e)
        return (
            "Could not fetch a recommendation now. "
            "Treat this as a low-confidence scenario and avoid large moves."
        )