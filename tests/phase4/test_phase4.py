import json
import unittest

from src.phase4.llm_service import LLMService
from src.phase4.prompt_builder import build_ranking_prompt
from src.phase4.response_parser import ResponseParserError, parse_and_validate_response


class Phase4Tests(unittest.TestCase):
    def test_prompt_builder_contains_output_schema(self) -> None:
        prompt = build_ranking_prompt(
            query_filters={"hard_filters": {"location": "Delhi"}},
            candidates=[{"restaurant_name": "A"}],
            top_k=1,
        )
        self.assertIn("output_schema", prompt)
        self.assertIn("candidate_restaurants", prompt)

    def test_response_parser_rejects_invalid_payload(self) -> None:
        with self.assertRaises(ResponseParserError):
            parse_and_validate_response('{"summary":"ok"}')

    def test_llm_service_returns_valid_schema(self) -> None:
        service = LLMService()
        raw = service.generate_ranked_output(
            prompt="test",
            query_filters={"hard_filters": {"location": "Indiranagar", "cuisine": "Desserts"}},
            candidates=[
                {
                    "restaurant_name": "A",
                    "location": "Indiranagar",
                    "cuisine": "Desserts",
                    "estimated_cost": 400.0,
                    "rating": 4.8,
                    "composite_score": 9.1,
                }
            ],
            top_k=1,
        )
        payload = parse_and_validate_response(raw)
        self.assertEqual(len(payload["recommendations"]), 1)
        self.assertEqual(payload["recommendations"][0]["rank"], 1)
        self.assertIsInstance(payload["summary"], str)


if __name__ == "__main__":
    unittest.main()
