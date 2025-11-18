# suclepy/core/cleaner.py

import pandas as pd
import numpy as np
from .utils import (
    fill_missing, drop_duplicates, standardize_dates,
    validate_emails, auto_fill_strings
)
from .reporter import CleaningReport

class Cleaner:
    def __init__(self, df: pd.DataFrame, config: dict = None):
        self.df = df.copy()
        self.config = config if config else {}

        # Initialize stats for report
        self.stats = {
            "total_rows_before": len(df),
            "rows_after_cleaning": 0,
            "duplicates_removed": 0,
            "missing_values_filled": 0,  # numeric missing
            "invalid_emails_fixed": 0,
            "missing_strings_filled": 0,  # string/object missing
            "dates_standardized": 0,
            "default_dates_used": 0
        }

    def clean(self):
        # 1️⃣ Remove duplicates
        self.df, dup_count = drop_duplicates(self.df)
        self.stats["duplicates_removed"] = dup_count

        # 2️⃣ Fill numeric missing values
        self.df, missing_count = fill_missing(self.df)
        self.stats["missing_values_filled"] = missing_count

        # 3️⃣ Validate & fix emails
        self.df, email_count = validate_emails(self.df)
        self.stats["invalid_emails_fixed"] = email_count

        # 4️⃣ Auto-fill missing string/object columns
        self.df, string_fill_count = auto_fill_strings(self.df)
        self.stats["missing_strings_filled"] = string_fill_count

        # 5️⃣ Standardize dates
        self.df, date_count, default_date_count = standardize_dates(self.df)
        self.stats["dates_standardized"] = date_count
        self.stats["default_dates_used"] = default_date_count

        # Update final row count
        self.stats["rows_after_cleaning"] = len(self.df)

        # Return cleaned df and stats
        return self.df, self.stats
