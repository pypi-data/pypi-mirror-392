import pandas as pd
from validata import compare_distinct_values
import tempfile
import os


def test_compare_distinct_values():
    prev = pd.DataFrame({
        "Country Code": ["FR", "DE", "US"]
    })

    new = pd.DataFrame({
        "Country Code": ["FR", "US", "IN"]   # IN is new
    })

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as prev_tmp, \
         tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as new_tmp:

        prev.to_csv(prev_tmp.name, index=False)
        new.to_csv(new_tmp.name, index=False)

        result = compare_distinct_values("Country Code", prev_tmp.name, new_tmp.name)

    os.unlink(prev_tmp.name)
    os.unlink(new_tmp.name)

    col = result.columns[0]

    assert "IN" in result[col].tolist()
