import pandas as pd

def convert_epoch_columns(df):
    """
    Convert any column in the DataFrame ending with 'Time' or containing 'epoch' from milliseconds since epoch
    to datetime. Handles NaN and non-integer values gracefully.
    """
    for col in df.columns:
        # Identify columns likely to be epoch milliseconds
        if (
            col.lower().endswith('time')
            or 'epoch' in col.lower()
        ):
            # Only convert if values look like epoch ms (large integers)
            if pd.api.types.is_numeric_dtype(df[col]):
                # Heuristic: typical ms epoch values are > 10^12
                if df[col].dropna().astype('float').gt(1e12).any():
                    df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce')
    return df

def safe_get_nested(dct, path, default=None):
    """
    Safely get a nested value from a dictionary.
    :param dct: The dictionary to extract from.
    :param path: List of keys representing the path.
    :param default: Value to return if any key is missing or None encountered.
    :return: The nested value or default.
    Example:
        safe_get_nested(vessel, ["ttbDetails", "taxClass", "id"])
    """
    current = dct
    for key in path:
        if current is None or not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default

def safe_get(val):
    """
    Returns val if it's not None AND contains at least one non-empty value.
    Returns None if val is None or is an empty dict.
    Accepts arrays/lists and other types as present unless empty.
    """
    if val is None:
        return None
    if isinstance(val, dict):
        # If any value in the dict is not None, not empty string, not empty dict, treat as present
        for v in val.values():
            # Also check for empty lists/tuples/sets
            if v is not None and v != "" and v != {} and v != [] and v != () and v != set():
                return val
        return None
    if isinstance(val, (list, tuple, set)):
        return val if len(val) > 0 else None
    if isinstance(val, str):
        return val if val.strip() != "" else None
    return val

def safe_get_path(dct, path, default=None):
    """
    Combines safe_get_nested and safe_get logic.
    Returns None if nested value is missing, None, empty string, empty list, or empty dict.
    """
    val = safe_get_nested(dct, path, default=default)
    return safe_get(val)

def trim_and_log(df, col_max_lengths):
    """
    Trims string columns to their max allowed length and logs if trimmed.
    :param df: Pandas DataFrame.
    :param col_max_lengths: Dict of {column: max_length}.
    :return: DataFrame with trimmed columns.
    """
    for col, max_len in col_max_lengths.items():
        if col in df.columns:
            def _trim(val):
                if isinstance(val, str) and len(val) > max_len:
                    print(f"TRIMMED: Column '{col}' value '{val}' to length {max_len}")
                    return val[:max_len]
                return val
            df[col] = df[col].apply(_trim)
    return df