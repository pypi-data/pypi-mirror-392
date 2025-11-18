from pathlib import Path

import pandas as pd

import lfsir


ERROR = 1
CSV_DIR = Path(__file__).parent.joinpath("csv")


def _eq_tables(first: pd.DataFrame, second: pd.DataFrame, error: float = ERROR):
    return first.sub(second).abs().div(first).mul(100).ge(error).sum().sum() == 0


def test_1401_T001():
    original = pd.read_csv(
        CSV_DIR.joinpath("1401_T001.csv"), header=[0, 1], index_col=0
    )
    created = lfsir.load_knowledge("sci_results.T001", 1401)
    assert _eq_tables(original, created)
