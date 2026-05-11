import unittest

from src.phase2.preferences import PreferenceValidationError, parse_preferences
from src.phase2.query_builder import build_query_filters


class Phase2Tests(unittest.TestCase):
    def test_parse_preferences_valid_payload(self) -> None:
        prefs = parse_preferences(
            {
                "location": "bangalore",
                "budget": "medium",
                "cuisine": "italian",
                "min_rating": "4.2",
                "optional_preferences": "family-friendly, quick service",
            }
        )
        self.assertEqual(prefs.location, "Bangalore")
        self.assertEqual(prefs.budget, "medium")
        self.assertEqual(prefs.cuisine, "Italian")
        self.assertEqual(prefs.min_rating, 4.2)
        self.assertEqual(prefs.optional_preferences, ["family-friendly", "quick service"])

    def test_parse_preferences_invalid_budget(self) -> None:
        with self.assertRaises(PreferenceValidationError):
            parse_preferences(
                {
                    "location": "Delhi",
                    "budget": "very high",
                    "cuisine": "North Indian",
                    "min_rating": 4,
                }
            )

    def test_query_builder_returns_phase3_ready_shape(self) -> None:
        prefs = parse_preferences(
            {
                "location": "Delhi",
                "budget": "low",
                "cuisine": "Chinese",
                "min_rating": 3.5,
                "optional_preferences": ["quick service"],
            }
        )
        query = build_query_filters(prefs)
        self.assertIn("hard_filters", query)
        self.assertIn("soft_preferences", query)
        self.assertTrue(query["query_metadata"]["ready_for_phase3"])


if __name__ == "__main__":
    unittest.main()
