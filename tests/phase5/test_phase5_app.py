import unittest

from src.phase5.app import create_app


class Phase5AppTests(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app(data_path="data/processed/restaurants_cleaned.csv")
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_page_loads(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Phase 5: Recommendation Experience", response.data)

    def test_recommend_returns_cards(self) -> None:
        response = self.client.post(
            "/recommend",
            data={
                "location": "Indiranagar",
                "budget": "medium",
                "cuisine": "Desserts",
                "min_rating": "4.0",
                "optional_preferences": "quick service",
                "sort_by": "rank",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Generated", response.data)
        self.assertIn(b"Rank", response.data)


if __name__ == "__main__":
    unittest.main()
