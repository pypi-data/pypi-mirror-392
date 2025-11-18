import os
import pandas as pd

from validata.io.loader import load_file


def compare_columns(previous_file, new_file, previous_sheet=None, new_sheet=None):
    """
    Compare column names between a previous file and a new file.

    Parameters
    ----------
    previous_file : str
        Path to the previous (baseline) file – CSV, XLSX, or XLS.
    new_file : str
        Path to the new file.
    previous_sheet : str | int | None, optional
        Sheet name or index for the previous Excel file.
        Ignored for CSV. If None, first sheet is used.
    new_sheet : str | int | None, optional
        Sheet name or index for the new Excel file.
        Ignored for CSV. If None, first sheet is used.

    Returns
    -------
    pandas.DataFrame
        Single-column DataFrame listing columns that exist in the
        previous file but are missing in the new file. The column
        header is derived from the new file name, e.g.
        ``"{new file} Missing Columns"``.

        If there are no missing columns, the DataFrame contains a
        single row with the value ``NaN``.
    """
    prev_df = load_file(previous_file, sheet=previous_sheet)
    new_df = load_file(new_file, sheet=new_sheet)

    prev_cols = list(prev_df.columns)
    new_cols = list(new_df.columns)

    missing = [c for c in prev_cols if c not in new_cols]

    if not missing:
        # Represent "nothing missing" with a single NaN row
        missing = [pd.NA]

    new_file_name = os.path.splitext(os.path.basename(new_file))[0]
    header = f"{new_file_name} Missing Columns"

    return pd.DataFrame({header: missing})
