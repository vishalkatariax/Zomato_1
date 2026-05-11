# 🍽️ Zomato AI – Restaurant Recommendation System

An AI-powered restaurant recommendation web app for Bangalore, built with Flask + Groq LLaMA 3.3 + the Zomato dataset.

![Zomato AI Screenshot](docs/screenshot.png)

---

## ✨ Features

- 🔍 **Smart Filtering** — Filter 12,000+ Bangalore restaurants by location, cuisine, budget, and rating
- 🤖 **LLM-Powered Ranking** — Groq's LLaMA 3.3 (70B) ranks and explains each recommendation
- 📍 **Dynamic Cuisine Dropdown** — Cuisine options update in real-time based on the selected location
- ⚡ **Quick Chips** — One-click presets for popular searches
- 📊 **Match Score** — AI-generated match percentage for each restaurant
- 🎨 **Zomato-inspired UI** — Clean, responsive design with animations

---

## 🏗️ Project Structure

```
.
├── restaurant_app.py          # Flask backend (main entry point)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── templates/
│   └── zomato_index.html      # Frontend UI (Zomato AI design)
├── data/
│   └── processed/
│       └── restaurants_cleaned.csv   # Zomato Bangalore dataset
├── phases/                    # Phase-wise implementation modules
│   ├── phase1-data-preparation/
│   ├── phase2-preference-capture/
│   ├── phase3-candidate-retrieval/
│   ├── phase4-llm-ranking/
│   ├── phase5-presentation/
│   └── phase6-evaluation-monitoring/
├── tests/                     # Unit tests per phase
│   ├── phase1/ … phase5/
│   └── README.md
├── problemstatement.md        # Original problem statement
├── phased-architecture.md     # Phase-wise architecture doc
└── edge-cases.md              # Edge cases & test guidance
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/zomato-ai.git
cd zomato-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

### 4. Add the dataset
Download from HuggingFace and place at `data/processed/restaurants_cleaned.csv`:
```
https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
```

### 5. Run the app
```bash
python restaurant_app.py
```
Open [http://localhost:5050](http://localhost:5050)

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (get one at [console.groq.com](https://console.groq.com)) |

---

## 🧠 How It Works

```
User Input (location, cuisine, budget, rating)
        ↓
Phase 3: Filter dataset (12,119 Bangalore restaurants)
        ↓
Phase 4: Top 15 candidates → Groq LLaMA 3.3 prompt
        ↓
LLM ranks & explains Top 3
        ↓
Phase 5: Display with match scores, AI explanations & animations
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 📦 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/recommend` | Get top N restaurant recommendations |
| `GET` | `/api/locations` | List all available locations |
| `GET` | `/api/cuisines` | List all cuisines |
| `GET` | `/api/cuisines-by-location?location=X` | Cuisines available at location X |

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Pandas
- **AI**: Groq API (LLaMA 3.3 70B)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Dataset**: [Zomato Bangalore on HuggingFace](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
