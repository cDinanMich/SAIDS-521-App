# 2025 Fantasy Football Exploration Dashboard (SAIDS 521)

**Streamlit Link:**

https://saids-521-app-apdsay3gdmhyahqrrum2te.streamlit.app/

An interactive data visualization dashboard built with **Streamlit** to analyze historical weekly fantasy football trends from the 2025 NFL regular season (Weeks 1–17). Created for **SAIDS 521 (Assignment 3)**, this project explores positional scoring value, weekly top performers, and statistical drivers behind PPR fantasy points to inform future draft strategies.

## 📊 Dashboard Features

The application organizes four interactive visualizations into a responsive 2×2 grid:

1. **Weekly Top Performers (Lollipop Chart):** Compares the highest weekly scorers in raw PPR points against position-normalized PPR points ($z$-scores) to highlight which positions provide the greatest marginal advantage over their peers.
2. **Cumulative Positional Value (Treemap):** Visualizes total season normalized PPR points across position groups (`QB`, `RB`, `WR`, `TE`) and individual players, modeled after S&P 500 sector treemaps.
3. **Weekly Scoring Trends (Time Series):** Tracks average weekly raw PPR scoring trajectories across position groups throughout the regular season.
4. **Stat-to-Point Relationships (Scatterplot Matrix):** Examines how individual box-score metrics (yards, touchdowns, receptions, interceptions) correlate with both raw and normalized fantasy points by position.

### Interactive Sidebar Filters
* **Divisions:** Multi-select filter across all 8 NFL divisions (AFC/NFC North, South, East, West).
* **Teams:** Multi-select filter across all 32 NFL teams.
* **Weeks Included:** Range slider to slice the 2025 regular season (Weeks 1–17).
* **Player Season Percentile:** Range slider (0–100) filtering players based on their full-season raw PPR point percentile within their respective position group.

---

## 📁 Repository Structure

```text
saids-521-app/
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies for local and cloud deployment
├── README.md                   # Project documentation
└── data/
    └── clean_weekly_data.csv   # Cleaned 2025 NFL regular season player stats (Weeks 1–17)
```

---

## 🛠️ Data Pipeline & Methodology

* **Data Source:** Weekly 2025 NFL player statistics sourced via [`nflreadpy`](https://nflreadpy.nflverse.com/) (`nflverse` data).
* **Filtering:** Restricted to standard fantasy skill positions (`QB`, `RB`, `WR`, `TE`) and regular-season weeks (`Week <= 17`).
* **Feature Engineering:**
  * **Position-Normalized PPR (`normalized_ppr`):** Standardized $z$-scores computed within each position group to enable fair cross-position comparisons.
  * **NFL Divisions (`division`):** Mapped all 32 NFL franchises to their respective conferences and divisions.
  * **Positional Percentiles (`pos_percentile`):** Pre-calculated full-season raw PPR rankings within each position group to filter out low-volume backups.

---

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/cDinanMich/saids-521-app.git
   cd saids-521-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```
   The dashboard will open automatically in your default browser at `http://localhost:8501`.

---

## ☁️ Deployment

This repository is configured for deployment on **Streamlit Community Cloud**. Ensure `app.py`, `requirements.txt`, and `data/clean_weekly_data.csv` remain in the structure above when deploying from GitHub.
