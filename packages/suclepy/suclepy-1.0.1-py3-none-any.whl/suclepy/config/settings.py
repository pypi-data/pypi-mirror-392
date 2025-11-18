# suclepy/config/settings.py

# Global configuration dictionary
_GLOBAL_CONFIG = {}

def set_rules(rules: dict):
    """
    Set global cleaning rules for SUCLEPY.
    Example:
        sp.config({
            "missing_value_strategy": "median",
            "remove_duplicates": True
        })
    """
    global _GLOBAL_CONFIG
    if not isinstance(rules, dict):
        raise ValueError("Rules must be provided as a dictionary")
    _GLOBAL_CONFIG.update(rules)
    print("SUCLEPY global rules updated:")
    for k, v in rules.items():
        print(f" - {k}: {v}")

def get_rules():
    """
    Retrieve current global configuration rules.
    """
    return _GLOBAL_CONFIG.copy()
