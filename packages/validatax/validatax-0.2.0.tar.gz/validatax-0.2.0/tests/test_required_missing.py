import pandas as pd
from validata import check_required_missing_values
import tempfile
import os


def test_required_missing():
    df = pd.DataFrame({
        "Hotel Name": ["Marriott", None, "Hilton"],
        "Hotel City": ["Paris", "Berlin", None],
        "Hotel Country": ["France", "Germany", "USA"]
    })

    required = ["Hotel Name", "Hotel City", "Hotel Zipcode"]

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        result = check_required_missing_values(required, tmp.name)

    os.unlink(tmp.name)

    d = result.set_index("Column Name")["Missing Count"]

    assert d["Hotel Name"] == 1
    assert d["Hotel City"] == 1
    assert d["Hotel Zipcode"] == "Column Not Found"
