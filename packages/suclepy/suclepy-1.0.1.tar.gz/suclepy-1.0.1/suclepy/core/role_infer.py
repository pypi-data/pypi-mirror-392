# suclepy/core/role_infer.py

import pandas as pd
from .validator import is_valid_email, is_valid_date, is_numeric

class RoleInfer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.roles = {}

    def infer(self):
        """
        Infer column roles/types for each column.
        Possible roles: numeric, string, email, date
        """
        for col in self.df.columns:
            sample = self.df[col].dropna().iloc[:10]  # check first 10 non-null
            if sample.empty:
                self.roles[col] = "unknown"
                continue

            if all(is_numeric(v) for v in sample):
                self.roles[col] = "numeric"
            elif col.lower() == "email" or all(is_valid_email(v) for v in sample):
                self.roles[col] = "email"
            elif all(is_valid_date(v) for v in sample):
                self.roles[col] = "date"
            else:
                self.roles[col] = "string"

        return self.roles
