#!/usr/bin/env python3
"""
Restaurant Recommendation Flask App
Backend: Zomato dataset + Groq LLM
Frontend: Zomato-AI inspired UI
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Load dataset once at startup
print("📂 Loading Zomato Bangalore dataset...")
# Make path absolute relative to this script so it works from any directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "processed", "restaurants_cleaned.csv")
df = pd.read_csv(csv_path)
df["cuisine_lower"]  = df["cuisine"].str.lower().str.strip()
df["location_lower"] = df["location"].str.lower().str.strip()
print(f"   ✅ {len(df)} records loaded.")


def get_recommendations(location: str, cuisine: str, budget: int, rating: float, top_n: int = 3):
    """Filter dataset and call Groq LLM to rank top N restaurants."""

    # Build filter mask
    mask = (df["estimated_cost"] <= budget) & (df["rating"] >= rating)

    if location.strip():
        mask &= df["location_lower"].str.contains(location.lower(), na=False)

    if cuisine.strip() and cuisine.lower() != "any":
        # Try exact cuisine keyword first
        keyword = cuisine.lower().split()[0]  # e.g. "south" from "south indian"
        cuisine_mask = df["cuisine_lower"].str.contains(keyword, na=False)
        # If too few results, broaden
        if (mask & cuisine_mask).sum() == 0:
            cuisine_mask = df["cuisine_lower"].str.contains(cuisine.lower().split()[-1], na=False)
        mask &= cuisine_mask

    filtered = df[mask].copy()
    filtered.sort_values(["rating", "estimated_cost"], ascending=[False, True], inplace=True)
    candidates = filtered.head(15)

    if candidates.empty:
        return {"success": False, "error": "No restaurants found matching your preferences.", "results": []}

    # Build candidate list for LLM
    restaurant_list = ""
    for i, row in enumerate(candidates.itertuples(), 1):
        restaurant_list += (
            f"{i}. {row.restaurant_name} | Area: {row.location} | "
            f"Cuisine: {row.cuisine} | Rating: {row.rating}/5 | "
            f"Cost for two: ₹{int(row.estimated_cost)}\n"
        )

    prompt = f"""You are an expert restaurant recommendation assistant for Bangalore, India.

A user wants TOP {top_n} restaurant recommendations:
- Location : {location or 'Bangalore (any area)'}
- Cuisine  : {cuisine or 'Any'}
- Budget   : ₹{budget} (cost for two people)
- Min Rating: {rating}/5

Filtered restaurant candidates from our Zomato database:
{restaurant_list}

Select and rank the BEST {top_n} restaurants. For EACH restaurant return a JSON array element with these exact keys:
- "rank": number
- "name": restaurant name
- "area": neighbourhood/area
- "cuisine": cuisine type
- "rating": rating out of 5 (number)
- "cost": cost for two in rupees (number)
- "match_score": a percentage 0-100 reflecting how well it matches the user's preferences (number)
- "explanation": 2-sentence explanation of why it's recommended
- "highlight": one short catchy phrase (e.g. "Best value pick", "Hidden gem", "Top rated")

Respond ONLY with a valid JSON array, no extra text. Example format:
[{{"rank":1,"name":"...","area":"...","cuisine":"...","rating":4.5,"cost":300,"match_score":95,"explanation":"...","highlight":"..."}}]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a restaurant recommendation assistant. Always respond with valid JSON only."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1200
    )

    raw = response.choices[0].message.content.strip()

    # Extract JSON array from response
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start == -1 or end == 0:
        return {"success": False, "error": "LLM response could not be parsed.", "results": []}

    results = json.loads(raw[start:end])

    return {
        "success": True,
        "results": results[:top_n],
        "total_candidates": len(filtered),
        "tokens_used": response.usage.total_tokens
    }


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Zomato AI Backend is running"}), 200


@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data     = request.get_json()
        location = data.get("location", "").strip()
        cuisine  = data.get("cuisine", "").strip()
        budget   = int(data.get("budget", 500))
        rating   = float(data.get("rating", 4.0))
        top_n    = int(data.get("top_n", 3))

        result = get_recommendations(location, cuisine, budget, rating, top_n)
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "results": []}), 500


@app.route("/api/locations")
def locations():
    """Return unique locations for autocomplete."""
    locs = sorted(df["location"].dropna().unique().tolist())
    return jsonify(locs)


@app.route("/api/cuisines")
def cuisines():
    """Return common cuisine types (all Bangalore)."""
    all_c = []
    for c in df["cuisine"].dropna():
        for part in c.split(","):
            all_c.append(part.strip())
    unique = sorted(set(all_c))
    return jsonify(unique[:80])


@app.route("/api/cuisines-by-location")
def cuisines_by_location():
    """Return cuisines available only at the given location."""
    location = request.args.get("location", "").strip()
    if not location:
        # No location selected — return all cuisines
        return cuisines()

    loc_df = df[df["location_lower"].str.contains(location.lower(), na=False)]
    all_c = []
    for c in loc_df["cuisine"].dropna():
        for part in c.split(","):
            p = part.strip()
            if p:
                all_c.append(p)
    unique = sorted(set(all_c))
    return jsonify(unique)


if __name__ == "__main__":
    print("🚀 Starting Zomato AI Restaurant Recommendation App...")
    print("   Open: http://localhost:5050")
    app.run(debug=True, port=5050, host="0.0.0.0")
