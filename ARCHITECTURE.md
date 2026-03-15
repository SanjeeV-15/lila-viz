# ARCHITECTURE.md

## What I Built

A browser-based Level Design tool that loads 5 days of LILA BLACK production telemetry
(~89,000 events across 1,243 parquet files) and lets a designer interactively explore
player behaviour on all 3 maps.

---

## Tech Stack & Why

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11 | Fast iteration; all data tools available |
| Web framework | Streamlit | Zero front-end code needed; built-in state management, sliders, multi-select — exactly what a data tool needs |
| Data I/O | PyArrow + pandas | PyArrow reads the `.nakama-0` parquet files (no extension needed); pandas is the easiest way to filter/join 89k rows |
| Visualisation | Plotly (graph_objects) | Renders on a pixel coordinate system; supports `add_layout_image` to pin the minimap behind scatter plots; interactive zoom/pan for free |
| Hosting | Streamlit Community Cloud | Free, deploys straight from GitHub in ~2 min; no server config required |

**What I considered but rejected:**
- **Streamlit + Folium/Leaflet** – great for geo-maps, awkward for a custom game coordinate system
- **React + deck.gl** – much faster rendering but requires a full JS/TS build pipeline, too slow to ship in 5 days
- **Dash** – very similar to Streamlit for this use case but slightly more boilerplate

---

## Data Flow

```
player_data/
  February_10/ ... February_14/          (1,243 .nakama-0 parquet files)
        │
        ▼
  data_loader.py :: load_all_data()
    • pyarrow.parquet.read_table() for each file
    • Decode event column: bytes → str
    • Derive is_bot from user_id (UUID = human, numeric = bot)
    • Derive date from folder name
    • Concatenate into one 89k-row DataFrame (cached in Streamlit session)
        │
        ▼
  app.py :: sidebar filters
    • map_id, date(s), match_id, player type, event types
    • Pandas boolean indexing — sub-second on 89k rows
        │
        ▼
  coord_utils.py :: world_to_pixel(x, z, map_id)
    • Applied via df.apply() on the filtered subset
    • Returns (px, py) in [0, 1024] pixel space
        │
        ▼
  Plotly figure
    • Minimap PNG pinned as background via add_layout_image
    • Scatter traces per event type (colour + symbol encode event)
    • Path lines drawn when a single match is selected
    • Heatmap: Histogram2dContour overlay on same pixel canvas
    • Timeline: same canvas, events coloured by match-time progress
        │
        ▼
  Streamlit Cloud  →  public URL
```

---

## Coordinate Mapping — The Tricky Part

Game world coordinates are in 3-D; the minimap is a flat 2-D image (1024 × 1024 px).
The README provides map-specific `scale` and `origin` values.

**Step 1 – Normalise to UV (0–1 range):**
```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
```

**Step 2 – Convert UV to pixel coords:**
```
px = u * 1024
py = (1 - v) * 1024     ← Y must be flipped: image origin is top-left, game origin is bottom-left
```

**Key insight:** The `y` column in the data is *elevation* (height in 3D space), not a map axis. For 2D plotting only `x` and `z` are used. Getting this wrong produces a squashed or mirrored overlay — I validated by checking that known spawn areas (visible on the minimap) matched where position events clustered.

**Per-map config:**

| Map | Scale | Origin X | Origin Z |
|---|---|---|---|
| AmbroseValley | 900 | −370 | −473 |
| GrandRift | 581 | −290 | −290 |
| Lockdown | 1000 | −500 | −500 |

---

## Assumptions Made

| Ambiguity | Assumption |
|---|---|
| `ts` column is described as "milliseconds representing time elapsed within the match" but parses as a full timestamp (1970 epoch base) | Used the raw int64 value in ms for relative ordering within a match; displayed as offset-from-start in the timeline slider |
| Files with no valid parquet magic bytes | Silently skipped — none found in practice |
| `y` column use | Treated as elevation only; not plotted on 2-D minimap |
| Bot detection | UUID (with hyphens) = human; short numeric ID = bot — exactly as documented |
| February 14 being partial | Loaded as-is; labelled "partial day" in the UI |

---

## Major Trade-offs

| Decision | What I chose | What I gave up |
|---|---|---|
| Load all data upfront | Single `@st.cache_data` call at startup (~5–10s) | Lower initial load if only one map is needed |
| Plotly scatter for paths | Works at 10k–20k points smoothly | WebGL-based tools (deck.gl) handle millions of points; paths can get slow with very large matches |
| Streamlit UI | Rapid delivery, clean sidebar | Limited custom CSS; hard to add drag-to-select or brushing |
| Parquet read per file | Simple, no pre-processing needed | A pre-merged parquet would be 5× faster to load |

---

## What I'd Do With More Time

1. **Pre-process into a single merged parquet** – cut load time from ~10s to ~1s
2. **Animated playback** – true frame-by-frame animation using Plotly frames or a JS frontend
3. **Cluster analysis** – identify high-density areas automatically using DBSCAN and surface them as named "hotspots" to designers
4. **Player comparison view** – overlay two specific players' paths in the same match side by side
5. **Loot spawn correlation** – cross-reference loot pickup locations with kill density to surface "loot then fight" corridors
