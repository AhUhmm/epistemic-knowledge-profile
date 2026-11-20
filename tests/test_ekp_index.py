"""Contract tests for ekp_index: the example's committed index is exactly
the script's output, and a frontmatter change makes the index stale."""
import shutil, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ekp_index import build_index, load_bundle  # noqa: E402

EXAMPLE = ROOT / "examples" / "neighbourhood-library"


class IndexGeneration(unittest.TestCase):
    def test_committed_example_index_is_reproducible(self):
        generated = build_index(EXAMPLE, load_bundle(EXAMPLE))
        on_disk = (EXAMPLE / "decisions" / "_index.md").read_text()
        self.assertEqual(generated, on_disk)

    def test_status_change_makes_index_stale(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "bundle"
            shutil.copytree(EXAMPLE, bundle)
            gap = bundle / "concept" / "gaps" / "GAP-002_unused-same-day-slots.md"
            gap.write_text(gap.read_text().replace("status: open", "status: resolved"))
            generated = build_index(bundle, load_bundle(bundle))
            on_disk = (bundle / "decisions" / "_index.md").read_text()
            self.assertNotEqual(generated, on_disk)
            self.assertIn("| GAP-002 | What happens to same-day slots nobody takes? | resolved |", generated)

    def test_index_does_not_depend_on_folder_name(self):
        with tempfile.TemporaryDirectory() as td:
            bundle = Path(td) / "a-differently-named-clone"
            shutil.copytree(EXAMPLE, bundle)
            generated = build_index(bundle, load_bundle(bundle))
            on_disk = (bundle / "decisions" / "_index.md").read_text()
            self.assertEqual(generated, on_disk)


if __name__ == "__main__":
    unittest.main()
