import os
import pandas as pd

from validata.io.loader import load_file


def compare_distinct_values(
    column,
    previous_file,
    new_file,
    previous_sheet=None,
    new_sheet=None,
):
    """
    Compare distinct values of a column between two files and
    return values that are new in the new file.

    Parameters
    ----------
    column : str
        Column name to compare.
    previous_file : str or path-like
        Path to the previous (baseline) file.
    new_file : str or path-like
        Path to the new file.
    previous_sheet : str | int | None, optional
        Sheet name or index for the previous Excel file.
    new_sheet : str | int | None, optional
        Sheet name or index for the new Excel file.

    Returns
    -------
    pandas.DataFrame
        Single-column DataFrame listing distinct values present
        in the new file but not in the previous file.
        Column header: "New Distinct Values in <new_file_name>".

        If there are no new values, returns one row with NaN.
    """
    prev_df = load_file(previous_file, sheet=previous_sheet)
    new_df = load_file(new_file, sheet=new_sheet)

    if column not in prev_df.columns:
        raise ValueError(f"Column {column!r} not found in previous file.")
    if column not in new_df.columns:
        raise ValueError(f"Column {column!r} not found in new file.")

    prev_vals = set(prev_df[column].dropna().unique())
    new_vals = set(new_df[column].dropna().unique())

    new_only = sorted(v for v in new_vals if v not in prev_vals)

    if not new_only:
        new_only = [pd.NA]

    new_file_name = os.path.splitext(os.path.basename(new_file))[0]
    header = f"New Distinct Values in {new_file_name}"

    return pd.DataFrame({header: new_only})
