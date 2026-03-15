import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import os

from data_loader import load_all_data
from coord_utils import world_to_pixel, IMAGE_SIZE, MINIMAP_PATHS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LILA BLACK — Level Design Tool",
    page_icon="🎮",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .stMetric { background: #1e1e2e; border-radius: 8px; padding: 0.5rem 1rem; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("🎮 LILA BLACK — Player Journey Visualizer")
st.caption("Level Design tool · 5 days of production telemetry · Feb 10–14, 2026")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading match data (first run may take ~30s)...")
def get_data():
    return load_all_data()

df = get_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filters")

    selected_map = st.selectbox("Map", sorted(df["map_id"].dropna().unique()))

    dates = sorted(df["date"].unique())
    selected_dates = st.multiselect("Date(s)", dates, default=dates)

    df_f = df[(df["map_id"] == selected_map) & (df["date"].isin(selected_dates))]

    matches = sorted(df_f["match_id_clean"].dropna().unique())
    selected_match = st.selectbox("Match", ["All matches"] + list(matches))

    if selected_match != "All matches":
        df_f = df_f[df_f["match_id_clean"] == selected_match]

    player_filter = st.radio("Player type", ["Humans + Bots", "Humans only", "Bots only"])
    if player_filter == "Humans only":
        df_f = df_f[~df_f["is_bot"]]
    elif player_filter == "Bots only":
        df_f = df_f[df_f["is_bot"]]

    st.divider()
    all_events = sorted(df_f["event"].dropna().unique())
    selected_events = st.multiselect("Event types", all_events, default=all_events)
    df_f = df_f[df_f["event"].isin(selected_events)]

# ── Metrics row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Events shown", f"{len(df_f):,}")
c2.metric("Human players", int((~df_f["is_bot"]).sum() > 0 and df_f[~df_f["is_bot"]]["user_id"].nunique()))
c3.metric("Matches", df_f["match_id"].nunique())
c4.metric("Kill events", int(df_f["event"].isin(["Kill","BotKill","Killed","BotKilled"]).sum()))
c5.metric("Storm deaths", int((df_f["event"] == "KilledByStorm").sum()))

# ── Coordinate conversion ─────────────────────────────────────────────────────
@st.cache_data
def convert_coords(df_subset_json, map_id):
    import json
    df_sub = pd.read_json(df_subset_json, orient="split")
    result = df_sub.apply(lambda r: world_to_pixel(r["x"], r["z"], map_id), axis=1)
    df_sub["px"] = [v[0] for v in result]
    df_sub["py"] = [v[1] for v in result]
    return df_sub

# ── Event style map ────────────────────────────────────────────────────────────
EVENT_STYLES = {
    "Position":      dict(color="rgba(80,160,255,0.25)", symbol="circle",    size=4,  label="👤 Position"),
    "BotPosition":   dict(color="rgba(160,160,160,0.15)",symbol="circle",    size=3,  label="🤖 BotPosition"),
    "Kill":          dict(color="#ff4444",               symbol="x",         size=12, label="⚔️ Kill"),
    "Killed":        dict(color="#ff8844",               symbol="x",         size=12, label="💀 Killed"),
    "BotKill":       dict(color="#ff7777",               symbol="x-open",    size=10, label="⚔️ BotKill"),
    "BotKilled":     dict(color="#ffaa77",               symbol="x-open",    size=10, label="💀 BotKilled"),
    "KilledByStorm": dict(color="#cc44ff",               symbol="star",      size=14, label="🌩️ KilledByStorm"),
    "Loot":          dict(color="#ffd700",               symbol="diamond",   size=10, label="💰 Loot"),
}

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗺️  Player Journeys", "🌡️  Heatmaps", "⏱️  Match Timeline"])

def load_minimap(map_id):
    return Image.open(MINIMAP_PATHS[map_id])

def base_figure(map_id):
    img = load_minimap(map_id)
    fig = go.Figure()
    fig.add_layout_image(dict(
        source=img, x=0, y=0, xref="x", yref="y",
        sizex=IMAGE_SIZE, sizey=IMAGE_SIZE,
        sizing="stretch", layer="below",
    ))
    fig.update_xaxes(range=[0, IMAGE_SIZE], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(range=[IMAGE_SIZE, 0], showgrid=False, zeroline=False,
                     showticklabels=False, scaleanchor="x")
    fig.update_layout(
        height=680, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(20,20,30,0.85)", font=dict(color="white"), x=1.01),
    )
    return fig

# ═══════════════════════════════════════════════════════════════
# TAB 1 — Player Journeys
# ═══════════════════════════════════════════════════════════════
with tab1:
    if df_f.empty:
        st.warning("No data with current filters.")
    else:
        df_plot = convert_coords(df_f.to_json(orient="split", date_format="iso"), selected_map)

        fig = base_figure(selected_map)

        # Draw path lines when a single match is selected
        if selected_match != "All matches":
            path_df = df_plot[df_plot["event"].isin(["Position","BotPosition"])].sort_values("ts")
            for uid, udf in path_df.groupby("user_id"):
                is_bot = udf["is_bot"].iloc[0]
                color = "rgba(130,130,140,0.45)" if is_bot else "rgba(80,160,255,0.55)"
                fig.add_trace(go.Scatter(
                    x=udf["px"], y=udf["py"], mode="lines",
                    line=dict(color=color, width=1.5),
                    name=f"Path {str(uid)[:8]}", showlegend=False, hoverinfo="skip",
                ))

        # Plot event markers per type
        for evt in df_plot["event"].unique():
            sub = df_plot[df_plot["event"] == evt]
            style = EVENT_STYLES.get(evt, dict(color="white", symbol="circle", size=6, label=evt))
            fig.add_trace(go.Scatter(
                x=sub["px"], y=sub["py"], mode="markers",
                name=style["label"],
                marker=dict(color=style["color"], symbol=style["symbol"], size=style["size"],
                            line=dict(width=0)),
                text=sub["user_id"].str[:8] + " | " + sub["event"],
                hovertemplate="<b>%{text}</b><extra></extra>",
            ))

        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Showing {len(df_plot):,} events on {selected_map}. "
                   f"Select a single match to see player path lines.")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — Heatmaps
# ═══════════════════════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns([1, 3])
    with col_a:
        heatmap_choice = st.radio("Overlay type", [
            "All traffic",
            "Kill zones",
            "Death zones",
            "Storm deaths",
            "Loot hotspots",
        ])
        opacity = st.slider("Overlay opacity", 0.2, 1.0, 0.55, 0.05)
        nbins = st.slider("Resolution (bins)", 20, 100, 50, 5)

    hm_event_map = {
        "All traffic":   ["Position", "BotPosition"],
        "Kill zones":    ["Kill", "BotKill"],
        "Death zones":   ["Killed", "BotKilled", "KilledByStorm"],
        "Storm deaths":  ["KilledByStorm"],
        "Loot hotspots": ["Loot"],
    }
    df_hm = df_f[df_f["event"].isin(hm_event_map[heatmap_choice])]

    with col_b:
        if df_hm.empty:
            st.warning("No events match this filter combination.")
        else:
            df_hm_c = convert_coords(df_hm.to_json(orient="split", date_format="iso"), selected_map)
            fig_hm = base_figure(selected_map)
            fig_hm.add_trace(go.Histogram2dContour(
                x=df_hm_c["px"], y=df_hm_c["py"],
                colorscale="Hot", reversescale=True,
                opacity=opacity, showscale=True,
                contours=dict(coloring="heatmap"),
                nbinsx=nbins, nbinsy=nbins,
                name=heatmap_choice,
            ))
            st.plotly_chart(fig_hm, use_container_width=True)
            st.caption(f"{len(df_hm_c):,} events plotted · {heatmap_choice} · {selected_map}")

# ═══════════════════════════════════════════════════════════════
# TAB 3 — Match Timeline
# ═══════════════════════════════════════════════════════════════
with tab3:
    if selected_match == "All matches":
        st.info("👆 Select a **specific match** in the sidebar to use the timeline playback.")
    elif df_f.empty:
        st.warning("No data for this match with current filters.")
    else:
        df_tl = df_f.copy()
        df_tl["ts_ms"] = pd.to_datetime(df_tl["ts"]).astype("int64") // 1_000_000
        min_t = int(df_tl["ts_ms"].min())
        max_t = int(df_tl["ts_ms"].max())
        duration = max(max_t - min_t, 1)

        st.markdown(f"**Match duration:** ~{duration//1000}s &nbsp;|&nbsp; "
                    f"**Players:** {df_tl['user_id'].nunique()} &nbsp;|&nbsp; "
                    f"**Events:** {len(df_tl):,}")

        window = st.slider(
            "Playback window (seconds into match)",
            min_value=0, max_value=duration // 1000,
            value=(0, min(60, duration // 1000)), step=5,
        )

        t_lo = min_t + window[0] * 1000
        t_hi = min_t + window[1] * 1000
        df_win = df_tl[(df_tl["ts_ms"] >= t_lo) & (df_tl["ts_ms"] <= t_hi)]

        if df_win.empty:
            st.warning("No events in this time window.")
        else:
            df_win_c = convert_coords(df_win.to_json(orient="split", date_format="iso"), selected_map)
            df_win_c = df_win_c.sort_values("ts_ms")

            fig_tl = base_figure(selected_map)

            # Colour-code by time progression so earlier = darker
            fig_tl.add_trace(go.Scatter(
                x=df_win_c["px"], y=df_win_c["py"], mode="markers",
                marker=dict(
                    color=(df_win_c["ts_ms"] - t_lo) / max(t_hi - t_lo, 1),
                    colorscale="Plasma", size=7, showscale=True,
                    colorbar=dict(title="Match progress", tickformat=".0%"),
                ),
                text=df_win_c["event"] + " · " + df_win_c["user_id"].str[:8],
                hovertemplate="%{text}<extra></extra>",
            ))

            # Overlay combat icons on top
            for evt in ["Kill", "BotKill", "Killed", "BotKilled", "KilledByStorm", "Loot"]:
                sub = df_win_c[df_win_c["event"] == evt]
                if sub.empty:
                    continue
                style = EVENT_STYLES[evt]
                fig_tl.add_trace(go.Scatter(
                    x=sub["px"], y=sub["py"], mode="markers",
                    name=style["label"],
                    marker=dict(color=style["color"], symbol=style["symbol"],
                                size=style["size"] + 2, line=dict(width=1, color="white")),
                    text=sub["user_id"].str[:8],
                    hovertemplate=f"<b>{evt}</b> · %{{text}}<extra></extra>",
                ))

            st.plotly_chart(fig_tl, use_container_width=True)
            st.caption(f"{len(df_win_c):,} events in t={window[0]}s–{window[1]}s window")
