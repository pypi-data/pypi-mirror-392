# suclepy/core/utils.py

import pandas as pd
import numpy as np
from dateutil.parser import parse

# -----------------------------
# 1️⃣ Drop duplicates
# -----------------------------
def drop_duplicates(df: pd.DataFrame):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, removed

# -----------------------------
# 2️⃣ Fill missing values
# -----------------------------
def fill_missing(df: pd.DataFrame):
    missing_count = 0
    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64]:
            missing = df[col].isnull().sum()
            df[col].fillna(df[col].median(), inplace=True)
            missing_count += missing
        else:
            missing = df[col].isnull().sum()
            df[col].fillna("abcd", inplace=True)
            missing_count += missing
    return df, missing_count

# -----------------------------
# 3️⃣ Validate & fix emails
# -----------------------------
def validate_emails(df: pd.DataFrame):
    email_count = 0
    if "Email" in df.columns:
        for i, val in df["Email"].items():
            # Check if invalid: None, NaN, missing '@', or missing domain
            if not isinstance(val, str) or "@" not in val or "." not in val.split("@")[-1]:
                if isinstance(val, str) and "@" in val:
                    # Partially invalid email (like 'subodh@') → add gmail.com
                    local = val.split("@")[0]
                    df.at[i, "Email"] = f"{local}@gmail.com"
                else:
                    # Completely missing or invalid → use default
                    df.at[i, "Email"] = "abc@gmail.com"
                email_count += 1
    return df, email_count


# -----------------------------
# -----------------------------
# 4️⃣ Auto-fill missing strings
# -----------------------------
def auto_fill_strings(df: pd.DataFrame):
    """
    Fill missing string/object type columns with 'abcd' and return count.
    Handles: None, '', 'null', 'NaN', ' '
    """
    fill_count = 0
    for col in df.columns:
        if df[col].dtype == object:
            for i, val in df[col].items():
                if val in [None, "", "null", "NaN", " "]:
                    df.at[i, col] = "abcd"
                    fill_count += 1
    return df, fill_count




# -----------------------------
# 5️⃣ Standardize dates
# -----------------------------
def standardize_dates(df: pd.DataFrame):
    date_count = 0
    default_date_count = 0
    date_cols = [col for col in df.columns if "date" in col.lower()]

    for col in date_cols:
        for i, val in df[col].items():
            if pd.isnull(val):
                df.at[i, col] = "00-00-0000"
                default_date_count += 1
            else:
                try:
                    dt = parse(str(val), dayfirst=True)
                    df.at[i, col] = dt.strftime("%d-%m-%Y")
                    date_count += 1
                except Exception:
                    df.at[i, col] = "00-00-0000"
                    default_date_count += 1

    return df, date_count, default_date_count
