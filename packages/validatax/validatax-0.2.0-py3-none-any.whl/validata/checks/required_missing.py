import pandas as pd

from validata.io.loader import load_file


def check_required_missing_values(required_columns, file, sheet=None):
    """
    Check missing values for required columns.

    Parameters
    ----------
    required_columns : list[str]
        List of required column names.
    file : str or path-like
        Path to the CSV or Excel file.
    sheet : str | int | None, optional
        Sheet name or index for Excel files. Ignored for CSV.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns:
        - "Column Name"
        - "Missing Count"
        If a column is not found, "Missing Count" is "Column Not Found".
    """
    df = load_file(file, sheet=sheet)
    df_cols = set(df.columns)

    rows = []
    for col in required_columns:
        if col not in df_cols:
            rows.append({"Column Name": col, "Missing Count": "Column Not Found"})
        else:
            missing_count = df[col].isna().sum()
            rows.append({"Column Name": col, "Missing Count": int(missing_count)})

    return pd.DataFrame(rows)
