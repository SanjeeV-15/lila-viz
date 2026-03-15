# LILA BLACK — Player Journey Visualizer

A browser-based Level Design tool that turns raw telemetry data into interactive
player-path overlays, heatmaps, and match timelines on the game's minimaps.

**Live tool:** https://sanjeevnandakumar.streamlit.app

---

## Features

- 🗺️ **Player Journeys** — scatter every event on the correct minimap; draw path lines for a single match
- 🌡️ **Heatmaps** — kill zones, death zones, storm-death clusters, loot hotspots
- ⏱️ **Match Timeline** — time-slider to scrub through a single match and watch it unfold
- 🔍 **Filters** — by map, date, match, player type (human/bot), and event type
- 👤 **Human vs Bot** — visually distinct colours and symbols

---

## Local Setup

### 1. Requirements

```bash
pip install streamlit pandas pyarrow plotly pillow
```

### 2. Data

Place the extracted data folder inside the project root so the structure looks like:

```
lila-viz/
├── app.py
├── data_loader.py
├── coord_utils.py
├── minimaps/
│   ├── AmbroseValley_Minimap.png
│   ├── GrandRift_Minimap.png
│   └── Lockdown_Minimap.jpg
└── player_data/
    ├── February_10/
    ├── February_11/
    ├── February_12/
    ├── February_13/
    └── February_14/
```

### 3. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Deploying to Streamlit Cloud (free)

1. Push this repo to GitHub (include the `player_data/` and `minimaps/` folders)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Connect your GitHub repo, set main file to `app.py`
4. Click **Deploy** — you'll have a public URL in ~2 minutes

> ⚠️ The full dataset is ~9 MB which is well within Streamlit Cloud's limits.

---

## Project Structure

```
app.py            – Streamlit UI (tabs, filters, charts)
data_loader.py    – Parquet loading + pandas cleaning
coord_utils.py    – World-to-pixel coordinate conversion
ARCHITECTURE.md   – Tech stack, data flow, trade-offs
INSIGHTS.md       – Three data-backed findings from the telemetry
```

---

## Environment Variables

None required. The app reads data from the local `player_data/` folder.
