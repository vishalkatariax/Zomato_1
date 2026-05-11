import unittest
from pathlib import Path

import pandas as pd

from src.phase1.pipeline import Phase1Pipeline, PipelineConfig


class Phase1PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = Phase1Pipeline(
            PipelineConfig(
                dataset_name="dummy",
                split="train",
                output_dir=Path("data/processed"),
                min_row_completeness=0.8,
            )
        )

    def test_align_schema_maps_known_aliases(self) -> None:
        df = pd.DataFrame(
            {
                "name": ["A"],
                "location": ["Indiranagar"],
                "cuisines": ["Desserts"],
                "approx_cost(for two people)": ["400"],
                "rate": ["4.5/5"],
            }
        )
        mapped = self.pipeline._align_schema(df)
        self.assertEqual(
            list(mapped.columns),
            ["restaurant_name", "location", "cuisine", "estimated_cost", "rating"],
        )

    def test_normalize_cost_handles_ranges(self) -> None:
        self.assertEqual(Phase1Pipeline._normalize_cost("500-700"), 600.0)

    def test_normalize_rating_filters_invalid_values(self) -> None:
        self.assertIsNone(Phase1Pipeline._normalize_rating("NEW"))
        self.assertEqual(Phase1Pipeline._normalize_rating("4.8/5"), 4.8)


if __name__ == "__main__":
    unittest.main()
