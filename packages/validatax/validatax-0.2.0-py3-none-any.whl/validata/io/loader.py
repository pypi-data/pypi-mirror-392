import pandas as pd

def load_file(path, sheet=None):
    """
    Load a CSV or Excel file into a pandas DataFrame.

    - For CSV: ignores `sheet`
    - For Excel: if `sheet` is None, loads the first sheet
                 otherwise uses the provided sheet name or index.
    """
    lower = path.lower()

    if lower.endswith(".csv"):
        return pd.read_csv(path)

    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        if sheet is None:
            return pd.read_excel(path, sheet_name=0)
        return pd.read_excel(path, sheet_name=sheet)

    raise ValueError(f"Unsupported file type for: {path!r}")
