# Tests Layout

Tests are organized phase-wise to match the project architecture:

- `tests/phase1/` - Phase 1 (data ingestion and preprocessing)
- `tests/phase2/` - Phase 2 (preference capture and query builder)
- `tests/phase3/` - Phase 3 (candidate retrieval layer)
- `tests/phase4/` - Phase 4 (prompting, inference, response parser)
- `tests/phase5/` - Phase 5 (results UI and refinement flow)

Run all tests from project root:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
