from claims_pipeline.policy import canonical_json_hash, load_policy_file
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_policy_hash_stable():
    t = load_policy_file(ROOT / "policy_terms.json")
    h1 = canonical_json_hash(t)
    h2 = canonical_json_hash(t)
    assert h1 == h2
    assert len(h1) == 64
