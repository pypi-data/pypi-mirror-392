# suclepy/core/reporter.py

import pandas as pd

class CleaningReport:
    def __init__(self, cleaned_df: pd.DataFrame, stats: dict):
        """
        Initializes CleaningReport with cleaned DataFrame and stats dictionary
        """
        self.cleaned_df = cleaned_df
        self.stats = stats

    # -----------------------------
    # Print summary of cleaning
    # -----------------------------
    def summary(self):
        lines = []
        lines.append("SUCLEPY CLEANING REPORT")
        lines.append("-" * 30)
        lines.append(f"Total Rows (before): {self.stats.get('total_rows_before', 0)}")
        lines.append(f"Rows After Cleaning: {self.stats.get('rows_after_cleaning', 0)}")
        lines.append(f"Duplicates Removed: {self.stats.get('duplicates_removed', 0)}")
        lines.append(f"Missing Values Filled: {self.stats.get('missing_values_filled', 0)}")
        lines.append(f"Invalid Emails Fixed: {self.stats.get('invalid_emails_fixed', 0)}")
        lines.append(f"Missing Strings Filled: {self.stats.get('missing_strings_filled', 0)}")  # <-- changed
        lines.append(f"Dates Standardized: {self.stats.get('dates_standardized', 0)}")
        lines.append(f"Default Date Used: {self.stats.get('default_dates_used', 0)}")
        lines.append(f"Status: SUCCESS ✅")
        return "\n".join(lines)


    # -----------------------------
    # Preview cleaned data
    # -----------------------------
    def head(self, n=5):
        return self.cleaned_df.head(n)

    # -----------------------------
    # Export cleaned DataFrame to CSV
    # -----------------------------
    def to_csv(self, filepath):
        self.cleaned_df.to_csv(filepath, index=False)
        print(f"File saved as {filepath}")
