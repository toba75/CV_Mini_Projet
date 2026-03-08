"""Evaluation utilities for ShelfScan pipeline."""

import pathlib

import pandas as pd

REQUIRED_COLUMNS = ["image_filename", "spine_index", "title", "author"]


def load_ground_truth(csv_path: str) -> pd.DataFrame:
    """Load and validate ground truth CSV.

    Args:
        csv_path: Path to the ground truth CSV file.

    Returns:
        Validated DataFrame with columns image_filename, spine_index, title, author.

    Raises:
        ValueError: If file doesn't exist, columns are missing, or data is invalid.
    """
    path = pathlib.Path(csv_path)
    if not path.exists():
        raise ValueError(f"Ground truth file not found: {csv_path}")

    df = pd.read_csv(path)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    title_is_na = df["title"].isna()
    title_is_blank = df["title"].fillna("").str.strip() == ""
    empty_titles = title_is_na | title_is_blank
    if empty_titles.any():
        raise ValueError(f"Found {empty_titles.sum()} rows with empty titles")

    return df
