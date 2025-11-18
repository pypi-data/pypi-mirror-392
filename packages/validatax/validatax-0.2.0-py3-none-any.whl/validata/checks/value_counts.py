import pandas as pd

from validata.io.loader import load_file


def get_value_counts(file, sheet=None, column=None):
    """
    Get value counts for a column as a DataFrame.

    Parameters
    ----------
    file : str or path-like
        Path to the CSV or Excel file.
    sheet : str | int | None, optional
        Sheet name or index for Excel. Ignored for CSV.
    column : str
        Column name for which to compute value counts.

    Returns
    -------
    pandas.DataFrame
        DataFrame with two columns:
        - "<column>": the distinct values
        - "Count": their counts
    """
    if column is None:
        raise ValueError("column must be provided")

    df = load_file(file, sheet=sheet)

    if column not in df.columns:
        raise ValueError(f"Column {column!r} not found in file.")

    vc = df[column].value_counts(dropna=False)

    result = vc.reset_index()
    result.columns = [column, "Count"]

    return result
