import pandas as pd
from validata import compare_columns


def test_compare_columns_missing():
    prev = pd.DataFrame({"Hotel Name": [1], "Hotel City": [2], "Hotel Address": [3]})
    new = pd.DataFrame({"Hotel Name": [1], "Hotel Address": [2]})

    # Write test to temp CSVs
    prev_path = "prev_test.csv"
    new_path = "new_test.csv"
    prev.to_csv(prev_path, index=False)
    new.to_csv(new_path, index=False)

    result = compare_columns(prev_path, new_path)

    col_name = "new_test Missing Columns"

    # Assertions
    assert col_name in result.columns
    assert "Hotel City" in result[col_name].tolist()
