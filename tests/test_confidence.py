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
    records = [
        ("IntakeAgent", 0.95),
        ("DocVerify", 0.95),
        ("Extract", 0.94),
        ("CrossVal", 0.96),
        ("Policy", 0.91),
        ("Fraud", 0.94),
        ("Adjudication", 0.94),
    ]
    c, _bd = aggregate_claim_confidence(records, ["FraudAgent"])
    assert c < 0.92
