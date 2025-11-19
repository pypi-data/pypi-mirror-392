import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fgmutils import evaluation

DATA_FILE = Path(__file__).resolve().parent / "data" / "avalia_ajuste_reference.json"


def test_avalia_ajuste_reference_values():
    esperado = json.loads(DATA_FILE.read_text())
    df = pd.DataFrame(esperado["dataFrame"])
    resultado = evaluation.avalia_estimativas(df["observado"], df["estimado"], df)
