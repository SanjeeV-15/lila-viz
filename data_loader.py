# data_loader.py
# Loads all parquet files from player_data/ into a single pandas DataFrame.

import os
import pandas as pd
import pyarrow.parquet as pq

DATA_ROOT = "player_data"
DAYS = [
    "February_10",
    "February_11",
    "February_12",
    "February_13",
    "February_14",
]


def _is_bot(user_id: str) -> bool:
    """
    Bots have short numeric user IDs (e.g. '1440').
    Humans have UUID-style IDs (e.g. 'f4e072fa-b7af-...').
    """
    return "-" not in str(user_id)


def load_all_data() -> pd.DataFrame:
    """
    Walk every day folder, parse every parquet file, and return one
    combined DataFrame with extra helper columns:
        date          – folder name, e.g. 'February_10'
        is_bot        – True if the player is a bot
        match_id_clean – match_id with '.nakama-0' suffix removed (nicer for display)
    """
    frames = []

    for day in DAYS:
        folder = os.path.join(DATA_ROOT, day)
        if not os.path.isdir(folder):
            continue

        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            try:
                table = pq.read_table(filepath)
                df = table.to_pandas()

                # Decode event column from bytes → str
                df["event"] = df["event"].apply(
                    lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
                )

                # Derive helper columns
                user_id = filename.split("_")[0]
                df["date"] = day
                df["is_bot"] = _is_bot(user_id)

                frames.append(df)

            except Exception:
                # Skip unreadable files silently
                continue

    if not frames:
        return pd.DataFrame(columns=[
            "user_id", "match_id", "map_id", "x", "y", "z",
            "ts", "event", "date", "is_bot", "match_id_clean",
        ])

    combined = pd.concat(frames, ignore_index=True)

    # Clean up match_id for display
    combined["match_id_clean"] = combined["match_id"].str.replace(
        ".nakama-0", "", regex=False
    )

    return combined
