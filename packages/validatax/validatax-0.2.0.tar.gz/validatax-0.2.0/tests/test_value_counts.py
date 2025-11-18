import pandas as pd
from validata import get_value_counts
import tempfile
import os


def test_value_counts():
    df = pd.DataFrame({
        "Year": [2021, 2022, 2021, 2023, 2021]
    })

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        result = get_value_counts(tmp.name, column="Year")

    os.unlink(tmp.name)

    vc = dict(zip(result["Year"], result["Count"]))

    assert vc[2021] == 3
    assert vc[2022] == 1
    assert vc[2023] == 1
