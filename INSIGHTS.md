# INSIGHTS.md
## Three Insights from the LILA BLACK Telemetry

---

### Insight 1 — Lockdown Has a Storm Problem: 3.4× Higher Storm-Death Rate Than AmbroseValley

**What caught my eye:**

On the heatmap overlay, switching to "Storm Deaths" on Lockdown showed deaths
clustered tightly against one edge of the map — not spread across multiple zones
the way deaths-by-combat are. On AmbroseValley, storm deaths were much sparser.

**The numbers:**

| Map | Human files | Storm deaths | Storm deaths / file |
|---|---|---|---|
| AmbroseValley | 555 | 32 | **0.058** |
| Lockdown | 170 | 34 | **0.200** |
| GrandRift | 57 | 8 | 0.140 |

Lockdown's storm-death rate is **3.4× higher** than AmbroseValley's per player-match,
even though it has fewer total files. Lockdown also has the highest share of deaths
that are storm-related: **14.7% of all deaths** on Lockdown are storm kills, vs
just **5.5%** on AmbroseValley.

**Why a Level Designer should care:**

A storm-death rate this elevated suggests one of three things:
1. The storm moves too fast relative to the map's traversal time on Lockdown
2. Extraction routes are too far from where players naturally end up after combat
3. There is a chokepoint near the storm boundary that players cannot clear in time

This is a **retention and fairness signal** — players who die to the storm rather
than to combat are likely to feel cheated rather than outplayed.

**Actionable items:**

- **Audit storm timing on Lockdown** — compare the storm's travel speed (ms per metre)
  to AmbroseValley's and check if the ratio matches the map-size ratio.
- **Mark extraction routes on the minimap** — overlay extraction-point locations on top
  of the storm-death cluster. If they don't align, the storm may be cutting off the
  natural exit path.
- **Metric to track:** `storm_death_rate` = `KilledByStorm events / total death events`
  per map. Target: bring Lockdown's rate below 8% (in line with AmbroseValley).

---

### Insight 2 — Nearly 1 in 5 Human Players Loots Nothing: Engagement Gap on All Maps

**What caught my eye:**

Switching to the Loot Hotspots heatmap showed clear high-density loot zones — but
when I cross-referenced that against per-player files, a significant share of human
players had **zero loot events** in their match.

**The numbers:**

| Map | Human files | Files with 0 loot | Rate |
|---|---|---|---|
| AmbroseValley | 555 | 109 | **19.6%** |
| Lockdown | 170 | 42 | **24.7%** |
| GrandRift | 57 | 11 | ~19.3% |

Across all maps, roughly **1 in 5 human players picks up nothing** in their match.
Among players who do loot, the average is **4.0 loot events per match**
with a maximum of 10 in a single run.

**Why a Level Designer should care:**

Looting is the primary economic loop in an extraction shooter. If 20% of players
skip it entirely, it means either:
1. They are dying before they reach any loot — the combat density is too high early
2. Loot spawns are not visible / readable enough to draw players in
3. Players are rushing toward the extraction point immediately (indicating they feel
   time pressure too early in the match)

On Lockdown specifically, the 24.7% no-loot rate is the highest of any map, and it
correlates with the elevated storm-death rate from Insight 1 — players may be sprinting
for extraction rather than stopping to loot.

**Actionable items:**

- **Correlate no-loot files with death cause** — do no-loot players die earlier in the
  match (position event count < median)? This distinguishes "died before reaching loot"
  from "chose not to loot."
- **Review loot spawn visibility on Lockdown** — are loot containers clearly marked on
  the minimap? Are they placed in natural-flow zones or off the main path?
- **Metrics to track:** `loot_engagement_rate` = % of human players with ≥1 Loot event
  per match per map. Target: raise from ~80% to ≥90%.

---

### Insight 3 — PvP Is Almost Absent: 99%+ of Kills Are Bot Kills

**What caught my eye:**

The Kill Zones heatmap vs the BotKill filter showed essentially the same pattern —
meaning human-vs-human kills are nearly absent. When I checked the raw numbers,
this was stark.

**The numbers:**

| Map | PvP kills (Kill event) | PvE kills (BotKill event) | PvP ratio |
|---|---|---|---|
| AmbroseValley | **0** | 2,698 | 0.0% |
| GrandRift | **2** | 246 | 0.8% |
| Lockdown | **0** | 706 | 0.0% |

Across 782 human-player match files and 796 unique matches,
there were only **2 human-vs-human kills** in the entire 5-day dataset.

**Context:** The average match composition is ~1.0 human + 0.6 bots, with the largest
observed match having only **2 humans**. This means most sessions are essentially
solo runs against bots. The data suggests the player base is small and matchmaking
rarely fills a lobby with multiple humans.

**Why a Level Designer should care:**

If maps are designed to facilitate PvP encounters — flanking routes, sight lines,
cover placement — those design elements are currently going completely untested by real
players. All combat feedback in this dataset is PvE feedback. This has two implications:

1. **The current data cannot validate PvP map design** — you can't see if the cover
   at a chokepoint works as intended when it's never being used in a human duel.
2. **Bot pathing determines where "combat" happens** — if bots always patrol the same
   corridors, kill-zone heatmaps reflect bot routes, not organic player behaviour.

**Actionable items:**

- **Bot audit:** overlay BotPosition heatmaps against Kill Zone heatmaps. High overlap
  means kills are happening wherever bots walk, not wherever the map naturally funnels
  players. If the bot paths are scripted, the kill zones are an artifact of the script.
- **Increase human matchmaking density** — even in playtests, seeding sessions with 4+
  humans would generate meaningful PvP signal for level designers.
- **Metrics to track:** `pvp_kill_ratio` = `Kill events / (Kill + BotKill events)` per
  map. Track this as player count grows. Any map changes to combat corridors should be
  evaluated once this ratio exceeds 10%.
