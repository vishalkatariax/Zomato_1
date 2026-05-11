import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.phase3.retrieval_service import CandidateRetrievalService, RetrievalConfig


class Phase3RetrievalTests(unittest.TestCase):
    def test_retrieve_candidates_applies_filters_and_top_n(self) -> None:
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "restaurants_cleaned.csv"
            pd.DataFrame(
                [
                    {
                        "restaurant_name": "A",
                        "location": "Indiranagar",
                        "cuisine": "Desserts",
                        "estimated_cost": 400.0,
                        "rating": 4.8,
                    },
                    {
                        "restaurant_name": "B",
                        "location": "Indiranagar",
                        "cuisine": "Desserts",
                        "estimated_cost": 900.0,
                        "rating": 4.5,
                    },
                    {
                        "restaurant_name": "C",
                        "location": "Delhi",
                        "cuisine": "Desserts",
                        "estimated_cost": 300.0,
                        "rating": 4.9,
                    },
                ]
            ).to_csv(csv_path, index=False)

            service = CandidateRetrievalService(RetrievalConfig(data_path=csv_path, top_n_default=10))
            result = service.retrieve_candidates(
                {
                    "hard_filters": {
                        "location": "Indiranagar",
                        "cuisine": "Desserts",
                        "min_rating": 4.0,
                        "cost_range": {"min_cost": 0, "max_cost": 500},
                    },
                    "soft_preferences": [],
                },
                top_n=2,
            )

            self.assertEqual(result["retrieval_summary"]["input_rows"], 3)
            self.assertEqual(result["retrieval_summary"]["hard_filtered_rows"], 1)
            self.assertEqual(result["retrieval_summary"]["shortlisted_rows"], 1)
            self.assertEqual(result["candidates"][0]["restaurant_name"], "A")


if __name__ == "__main__":
    unittest.main()
