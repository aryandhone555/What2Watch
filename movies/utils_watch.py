# movies/utils_watch.py
import pandas as pd
from pathlib import Path
from django.conf import settings

STATUS_CSV = settings.BASE_DIR / "watch_status.csv"


def _load_df() -> pd.DataFrame:
    if STATUS_CSV.exists() and STATUS_CSV.stat().st_size > 0:
        return pd.read_csv(STATUS_CSV)
    return pd.DataFrame(columns=["username", "title", "watched"])



def read_status(username: str) -> dict[str, bool]:
    """Return {title: watched_bool} just for this user."""
    df = _load_df()
    df = df[df["username"] == username]
    return dict(zip(df["title"], df["watched"].astype(bool)))


def toggle_status(username: str, title: str) -> None:
    """Flip watched flag for a user/title (create row if missing)."""
    df = _load_df()

    mask = (df["username"] == username) & (df["title"] == title)
    if mask.any():
        df.loc[mask, "watched"] = ~df.loc[mask, "watched"]
    else:
        df.loc[len(df)] = [username, title, True]   # first click = watched

    STATUS_CSV.parent.mkdir(exist_ok=True, parents=True)
    df.to_csv(STATUS_CSV, index=False)
