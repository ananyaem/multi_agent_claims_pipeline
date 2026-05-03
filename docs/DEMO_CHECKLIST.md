# Demo video checklist (8–12 min)

1. **Wrong documents (TC001)** — submit two prescriptions only; show specific error naming PRESCRIPTION vs required HOSPITAL_BILL.
2. **End-to-end approval (TC004)** — fixture JSON via Test runner `/eval/run` or paste TC004 documents; show trace + financial breakdown + confidence.
3. **Robustness / degradation** — explain harmonic confidence + TC011 simulated FraudAgent degradation (lower confidence, note in output).
4. **Proud technical choice** — deterministic adjudication + Redis-separated LLM worker + harmonic confidence.
5. **Would change with more time** — Postgres, BigQuery streaming, dedicated OCR pre-pass for extreme handwriting.
