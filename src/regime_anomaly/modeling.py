"""Interfaces reserved for the future modelling notebooks.

No model is trained at this stage. Notebook 03 will define the experiment and this
module will later receive reusable production code extracted from that notebook.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class ModelBundle:
    """Stable serialization contract expected by the application."""

    preprocessor: Any
    model: Any
    metadata: dict[str, Any]

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Predict with the future final model."""
        raise NotImplementedError("O modelo final ainda não foi definido no notebook 03.")
