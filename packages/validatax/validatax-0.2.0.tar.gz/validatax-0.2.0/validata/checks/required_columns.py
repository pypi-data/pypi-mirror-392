import pandas as pd

from validata.io.loader import load_file


def check_required_columns(required_columns, file, sheet=None):
    """
    Check which required columns are missing from the file.

    Parameters
    ----------
    required_columns : list[str]
        List of required column names.
    file : str or path-like
        Path to the CSV or Excel file.
    sheet : str | int | None, optional
        Sheet name or index for Excel files. Ignored for CSV.
        If None, the first sheet is used for Excel files.

    Returns
    -------
    pandas.DataFrame
        Single-column DataFrame with header:
        "Missing Required Columns".
        If no columns are missing, returns one row with NaN.
    """
    df = load_file(file, sheet=sheet)
    df_cols = set(df.columns)

    missing = [col for col in required_columns if col not in df_cols]

    if not missing:
        missing = [pd.NA]

    return pd.DataFrame({"Missing Required Columns": missing})
