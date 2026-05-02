from claims_pipeline.pipeline.confidence import aggregate_claim_confidence, harmonic_mean


def test_harmonic_all_ones():
    assert abs(harmonic_mean([1.0, 1.0, 1.0]) - 1.0) < 1e-9


def test_harmonic_one_low():
    h = harmonic_mean([0.95, 0.95, 0.5])
    arith = sum([0.95, 0.95, 0.5]) / 3
    assert h < arith
    assert h < 0.85


def test_harmonic_empty():
    assert harmonic_mean([]) == 0.0


def test_aggregate_with_degraded():
    c = aggregate_claim_confidence([0.95, 0.95, 0.94, 0.96, 0.91, 0.94, 0.94], ["FraudAgent"])
    assert c < 0.92
