"""Contract tests for ekp_usage: totals summed from transcript usage
records, EKP ops counted, dominant model picked, line format stable."""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ekp_usage import summarize, usage_line, fmt  # noqa: E402

TRANSCRIPT = Path(__file__).resolve().parent / "fixtures" / "transcript.jsonl"


class Summarize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tot, cls.models, cls.ops = summarize(TRANSCRIPT)

    def test_totals(self):
        self.assertEqual(self.tot, {"in": 3500, "out": 550,
                                    "cache_read": 12000, "cache_create": 300})

    def test_ops_counted(self):
        self.assertEqual(self.ops, {"/state": 1, "/wrap-up": 1})

    def test_dominant_model_by_output_tokens(self):
        self.assertEqual(max(self.models, key=self.models.get), "claude-test-1")

    def test_line_format(self):
        line = usage_line("2026-11-13", "abcd1234", self.tot, self.models, self.ops)
        self.assertEqual(line, "## [2026-11-13] usage | session abcd1234 | "
                               "ops: /state×1, /wrap-up×1 | "
                               "tokens: 3.5k in / 550 out / 12.0k cache-read | "
                               "model: claude-test-1")


class Fmt(unittest.TestCase):
    def test_humanize(self):
        self.assertEqual([fmt(950), fmt(1500), fmt(2_400_000)], ["950", "1.5k", "2.4M"])


if __name__ == "__main__":
    unittest.main()
