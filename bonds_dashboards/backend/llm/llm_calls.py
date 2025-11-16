import getpass
import os
from dotenv import load_dotenv

load_dotenv(override=True, dotenv_path='../.env')

TAVILY_KEY = os.getenv('TAVILY_KEY')
GEMINI_KEY = os.getenv('GOOGLE_API_KEY')

# from tavily import TavilyClient

# tavily_client = TavilyClient(api_key=TAVILY_KEY)
# response = tavily_client.search("Latest Fed rates news",
#                                 time_range= 'week',
#                                 max_results=10)

# print(response)


from langchain_google_genai import ChatGoogleGenerativeAI
from google.ai.generativelanguage_v1beta.types import Tool as GenAITool

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,

    # other params...
)

import json
import re
import logging

def minute_analysis(text, debug=True):
    """
    Extract numeric policy features from FOMC minutes for neural network input.
    Returns dict with 11 numeric features ready for MLP.
    """
    
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
  "p_cut": 0.0,                   // Probability of rate cut (0.0 to 1.0)
  "p_hold": 0.0,                  // Probability of rate hold (0.0 to 1.0)  
  "p_hike": 0.0,                  // Probability of rate hike (0.0 to 1.0)
  "inflation_tone": 0.0,          // 0.0 to 1.0 (higher = more inflation concern)
  "labor_tone": 0.0,              // 0.0 to 1.0 (higher = tighter labor market)
  "growth_tone": 0.0,             // 0.0 to 1.0 (higher = stronger growth outlook)
  "financial_conditions_tone": 0.0, // 0.0 to 1.0 (higher = tighter conditions)
  "balance_sheet_signal": 0.0     // -1.0 to +1.0 (QT>0, QE<0, neutral=0)
}}

Rules:
- p_cut + p_hold + p_hike must sum to 1.0
- Only return JSON, no text before or after
- Use decimal values like 0.75, not percentages

FOMC Minutes Text:
{text}
"""

    try:
        # Call LLM
        ai_msg = llm.invoke(prompt)
        raw_content = ai_msg.content.strip()
        
        if debug:
            print(f"Raw LLM response length: {len(raw_content)}")
            print(f"First 200 chars: {raw_content[:200]}")
        
        # Clean potential markdown formatting
        if raw_content.startswith("```"):
            raw_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content, flags=re.MULTILINE).strip()
        
        # Parse JSON
        try:
            obj = json.loads(raw_content)
        except json.JSONDecodeError as e:
            if debug:
                print(f"JSON parse error: {e}")
                print(f"Content: {raw_content}")
            # Return default values if parsing fails
            return get_default_features()
        
        # Validate and clean the response
        return validate_and_clean_features(obj, debug=debug)
        
    except Exception as e:
        if debug:
            print(f"LLM call failed: {e}")
        # Return default values on any error
        return get_default_features()

def validate_and_clean_features(obj, debug=False):
    """Validate and normalize LLM output features"""
    
    required_keys = {
        "policy_bias", "guidance_strength", "expected_move_bps",
        "p_cut", "p_hold", "p_hike", "inflation_tone", "labor_tone", 
        "growth_tone", "financial_conditions_tone", "balance_sheet_signal"
    }
    
    # Check for missing keys
    missing_keys = required_keys - set(obj.keys())
    if missing_keys:
        if debug:
            print(f"Missing keys: {missing_keys}")
        # Add missing keys with default values
        defaults = get_default_features()
        for key in missing_keys:
            obj[key] = defaults[key]
    
    # Type conversion and bounds checking
    try:
        # Bounded floats [-1, 1]
        obj["policy_bias"] = max(-1.0, min(1.0, float(obj["policy_bias"])))
        obj["balance_sheet_signal"] = max(-1.0, min(1.0, float(obj["balance_sheet_signal"])))
        
        # Bounded floats [0, 1] 
        for key in ["guidance_strength", "p_cut", "p_hold", "p_hike", 
                   "inflation_tone", "labor_tone", "growth_tone", "financial_conditions_tone"]:
            obj[key] = max(0.0, min(1.0, float(obj[key])))
        
        # Integer for basis points
        obj["expected_move_bps"] = int(round(float(obj["expected_move_bps"])))
        
        # Normalize probabilities to sum to 1
        prob_sum = obj["p_cut"] + obj["p_hold"] + obj["p_hike"]
        if prob_sum > 0:
            obj["p_cut"] /= prob_sum
            obj["p_hold"] /= prob_sum  
            obj["p_hike"] /= prob_sum
        else:
            # Default to hold if all probabilities are 0
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
