"""Contract tests for ekp_lint: the example bundle is clean; the dirty
fixture exhibits one case per finding class, and the linter sees each.

Run from the repo root: python3 -m unittest discover -s tests
"""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ekp_lint import lint  # noqa: E402

DIRTY = Path(__file__).resolve().parent / "fixtures" / "dirty"


class CleanBundle(unittest.TestCase):
    def test_example_bundle_has_no_findings(self):
        self.assertEqual(lint(ROOT / "examples" / "neighbourhood-library"), [])


class DirtyBundle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings = lint(DIRTY)

    def assertFinding(self, sev, level, fragment):
        hits = [f for f in self.findings
                if f[0] == sev and f[1] == level and fragment in f[3]]
        self.assertTrue(hits, f"no {sev}/{level} finding containing {fragment!r}")

    # L0
    def test_missing_type(self):
        self.assertFinding("ERROR", "L0", "missing `type`")

    def test_domain_type_rejected(self):
        self.assertFinding("ERROR", "L0", "`type: behavioral` not in epistemic vocabulary")

    # L1
    def test_missing_id(self):
        self.assertFinding("ERROR", "L1", "missing `id`")

    def test_malformed_id(self):
        self.assertFinding("ERROR", "L1", "malformed id `GAP-3`")

    def test_duplicate_id(self):
        self.assertFinding("ERROR", "L1", "duplicate id `GAP-001`")

    def test_prefix_type_mismatch(self):
        self.assertFinding("ERROR", "L1", "id prefix of `HYP-001` does not match type `assumption`")

    def test_folder_category_mismatch(self):
        self.assertFinding("ERROR", "L1", "expected under `concept/insights/`")

    def test_status_outside_lifecycle(self):
        self.assertFinding("ERROR", "L1", "`status: closed` not in gap lifecycle")

    def test_decision_in_subfolder(self):
        self.assertFinding("WARNING", "L1", "decisions/ should be flat")

    # L2
    def test_legacy_edge_field(self):
        self.assertFinding("WARNING", "L2", "legacy edge field `related_concept`")

    def test_bare_id_edge_target(self):
        self.assertFinding("WARNING", "L2", "`derives_from: GAP-001` is a bare ID")

    def test_dangling_edge(self):
        self.assertFinding("WARNING", "L2", "dangling edge `derives_from: concept/gaps/missing.md`")

    def test_resolves_from_non_decision(self):
        self.assertFinding("ERROR", "L2", "`resolves` stored on a opportunity")

    def test_resolves_target_not_a_gap(self):
        self.assertFinding("WARNING", "L2", "is a constraint; SPEC §5.2 defines resolves as settling gaps")

    def test_bidirectional_edge(self):
        self.assertFinding("ERROR", "L2", "bidirectional edge DEC-003<->GAP-005")

    # Views
    def test_id_missing_from_index(self):
        self.assertFinding("WARNING", "VIEWS", "DEC-003 (decisions/DEC-003_bidi.md) missing from index")

    def test_index_status_disagrees_with_file(self):
        self.assertFinding("WARNING", "VIEWS", "index lists DEC-002 as `validated` but file says `open`")

    def test_index_concept_status_checked_too(self):
        self.assertFinding("WARNING", "VIEWS", "index lists GAP-001 as `resolved` but file says `open`")

    # Log
    def test_log_create_without_file(self):
        self.assertFinding("WARNING", "LOG", "GAP-099 created in log but has no file")

    def test_log_transition_disagrees_with_file(self):
        self.assertFinding("WARNING", "LOG", "moves GAP-001 to `resolved` but file says `open`")

    def test_totals_are_pinned(self):
        errors = [f for f in self.findings if f[0] == "ERROR"]
        warnings = [f for f in self.findings if f[0] == "WARNING"]
        self.assertEqual((len(errors), len(warnings)), (10, 17))


if __name__ == "__main__":
    unittest.main()
