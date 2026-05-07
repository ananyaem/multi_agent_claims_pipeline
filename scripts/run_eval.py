#!/usr/bin/env python3
"""Run official assignment test cases and write docs/EVAL_REPORT.md.

By default this uses Gemini on fixture JPEGs under fixtures/<case_id>/ (strips embedded JSON
``content`` when an image exists) and requires GEMINI_API_KEY. Pass ``--fixture`` for the
deterministic harness that reads only embedded ``content`` in test_cases.json (no API calls).

Logs to stderr (INFO); also appends to ``<output_stem>_run.log`` next to ``-o`` unless
``--no-log-file``. Use ``-v`` for DEBUG.
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_ROOT = ROOT / "fixtures"

LOG = logging.getLogger("run_eval")


def _setup_logging(*, log_file: Path | None, verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    LOG.setLevel(level)
    LOG.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stderr_h = logging.StreamHandler(sys.stderr)
    stderr_h.setLevel(level)
    stderr_h.setFormatter(fmt)
    LOG.addHandler(stderr_h)
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        LOG.addHandler(fh)


def _resolve_fixture_image(case_id: str, doc: dict[str, Any]) -> Path | None:
    """Return path to an on-disk fixture image for this document, if any."""
    base = FIXTURES_ROOT / case_id
    if not base.is_dir():
        return None
    fn = doc.get("file_name")
    if isinstance(fn, str) and fn.strip():
        p = base / fn.strip()
        if p.is_file():
            return p
    fid = str(doc.get("file_id") or "")
    if fid:
        for suffix in (".jpeg", ".jpg", ".png"):
            p = base / f"{fid}{suffix}"
            if p.is_file():
                return p
    return None


def _hydrate_uploads(
    case_id: str,
    submission: dict[str, Any],
    claim_id: str,
    upload_root: Path,
    *,
    strip_content_when_imaged: bool,
    skip_unreadable_quality: bool,
) -> list[str]:
    """Copy fixture images into upload_root; optionally strip embedded JSON content for LLM path."""
    warnings: list[str] = []
    (upload_root / claim_id).mkdir(parents=True, exist_ok=True)
    for doc in submission.get("documents") or []:
        if skip_unreadable_quality and doc.get("quality") == "UNREADABLE":
            continue
        src = _resolve_fixture_image(case_id, doc)
        if src is None:
            if strip_content_when_imaged and doc.get("content") is not None:
                warnings.append(
                    f"{case_id}: no fixture image for file_id={doc.get('file_id')!r} "
                    f"(content kept; LLM will not replace extraction for this doc)."
                )
            continue
        fid = str(doc.get("file_id") or "doc")
        safe = doc.get("file_name") if isinstance(doc.get("file_name"), str) and doc["file_name"].strip() else src.name
        out_rel = f"{claim_id}/{fid}_{safe}"
        out_path = upload_root / out_rel
        shutil.copy2(src, out_path)
        doc["storage_relpath"] = out_rel
        doc.setdefault("mime_type", "image/jpeg")
        if strip_content_when_imaged and "content" in doc:
            del doc["content"]
    return warnings


def _prepare_submission(case: dict[str, Any], *, for_llm: bool) -> tuple[dict[str, Any], str | None]:
    sub = copy.deepcopy(case["input"])
    case_id = case["case_id"]
    claim_id: str | None = None
    if for_llm:
        if case_id == "TC009":
            sub.pop("claims_history", None)
            sub["claim_id"] = "CLM_EVAL_TC009_CURRENT"
            claim_id = sub["claim_id"]
        else:
            claim_id = str(sub.get("claim_id") or f"CLM_EVAL_{case_id}")
            sub["claim_id"] = claim_id
    else:
        claim_id = sub.get("claim_id")
        if isinstance(claim_id, str) and claim_id.strip():
            claim_id = claim_id.strip()
        else:
            claim_id = None
    return sub, claim_id


def _output_payload(ctx: Any) -> dict[str, Any]:
    return {
        "halted_reason": ctx.halted_reason,
        "decision": ctx.decision,
        "approved_amount": ctx.approved_amount,
        "confidence": ctx.confidence,
        "member_message": ctx.member_message,
        "rejection_reasons": list(ctx.rejection_reasons or []),
        "degraded_components": list(ctx.degraded_components or []),
        "halt_details": ctx.halt_details or {},
        "financial_breakdown": ctx.financial_breakdown or {},
        "fraud_signals": list(ctx.fraud_signals or []),
        "waiting_period_medical": ctx.waiting_period_medical,
        "policy_findings": list(ctx.policy_findings or []),
    }


def _trace_payload(ctx: Any) -> dict[str, Any]:
    return {
        "step_confidence_records": [{"step": s, "confidence": c} for s, c in (ctx.step_confidence_records or [])],
        "pipeline_details": ctx.pipeline_details or {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Deterministic harness: embedded JSON content only, no Gemini (for CI / offline).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=ROOT / "docs" / "EVAL_REPORT.md",
        help="Markdown output path (default: docs/EVAL_REPORT.md).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="DEBUG logging on stderr (and log file if enabled).",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="Append-style log file (default: <output_stem>_run.log next to -o; disabled with --no-log-file).",
    )
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Log only to stderr (no eval_run log file).",
    )
    args = parser.parse_args()
    use_llm = not args.fixture

    log_path: Path | None = None
    if not args.no_log_file:
        log_path = args.log_file if args.log_file is not None else args.output.parent / f"{args.output.stem}_run.log"
    _setup_logging(log_file=log_path, verbose=bool(args.verbose))

    upload_root = Path(tempfile.mkdtemp(prefix="eval_uploads_"))
    os.environ["UPLOAD_DIR"] = str(upload_root)
    sys.path.insert(0, str(ROOT / "src"))

    from claims_pipeline.config import TEST_CASES_PATH, get_settings
    from claims_pipeline.db import init_db
    from claims_pipeline.eval_db_seed import seed_eval_prior_claims_for_case
    from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
    from claims_pipeline.policy import PolicyService, get_active_policy_terms, seed_policy_and_members

    get_settings.cache_clear()
    if use_llm and not (get_settings().gemini_api_key or "").strip():
        LOG.error(
            "GEMINI_API_KEY is required for the default Gemini eval (set in environment or .env). "
            "Use --fixture for deterministic mode without API calls."
        )
        shutil.rmtree(upload_root, ignore_errors=True)
        return 1

    llm_provider = None
    if use_llm:
        from claims_pipeline.llm.gemini import GeminiProvider

        llm_provider = GeminiProvider()

    db_path = Path(tempfile.mkdtemp()) / "eval.db"
    init_db(f"sqlite:///{db_path}")
    from claims_pipeline.db import SessionLocal

    db = SessionLocal()
    warnings_all: list[str] = []
    t0 = time.monotonic()
    try:
        LOG.info(
            "starting eval mode=%s output=%s log_file=%s test_cases=%s",
            "gemini" if use_llm else "fixture",
            args.output,
            str(log_path) if log_path else "(stderr only)",
            TEST_CASES_PATH,
        )
        seed_policy_and_members(db)
        pv_id, terms = get_active_policy_terms(db)
        svc = PolicyService(terms)
        with open(TEST_CASES_PATH, encoding="utf-8") as f:
            bundle = json.load(f)

        mode_label = "Gemini vision + extraction" if use_llm else "fixture harness, no LLM"
        lines: list[str] = [
            f"# EVAL_REPORT ({mode_label})\n\n",
            f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n",
        ]

        n_cases = len(bundle["test_cases"])
        for i, case in enumerate(bundle["test_cases"], start=1):
            cid = case["case_id"]
            cname = case.get("case_name", "")
            LOG.info("case %d/%d %s — %s", i, n_cases, cid, cname)
            seed_eval_prior_claims_for_case(db, cid)
            sub, claim_id = _prepare_submission(case, for_llm=use_llm)
            if use_llm:
                assert claim_id is not None
                warnings_all.extend(
                    _hydrate_uploads(
                        cid,
                        sub,
                        claim_id,
                        upload_root,
                        strip_content_when_imaged=True,
                        skip_unreadable_quality=False,
                    )
                )
            ctx = run_pipeline_sync(
                sub,
                terms,
                pv_id,
                svc,
                llm_provider=llm_provider,
                claim_id=claim_id,
                db=db,
            )
            LOG.info(
                "case %s complete halted=%s decision=%s approved_amount=%s confidence=%s",
                cid,
                ctx.halted_reason,
                ctx.decision,
                ctx.approved_amount,
                ctx.confidence,
            )

            lines.append(f"## {cid} — {case.get('case_name', '')}\n\n")
            if use_llm:
                lines.append("### Expected (assignment)\n\n")
                lines.append(json.dumps(case.get("expected") or {}, indent=2, default=str))
                lines.append("\n\n")
            lines.append("### Output\n\n")
            lines.append(json.dumps(_output_payload(ctx), indent=2, default=str))
            lines.append("\n\n")
            if use_llm or ctx.step_confidence_records or ctx.pipeline_details:
                lines.append("### Trace (confidence + pipeline_details)\n\n")
                lines.append(json.dumps(_trace_payload(ctx), indent=2, default=str))
                lines.append("\n\n")
            lines.append("---\n\n")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        text = "".join(lines)
        args.output.write_text(text, encoding="utf-8")
        elapsed = time.monotonic() - t0
        LOG.info(
            "wrote report path=%s bytes=%d duration_s=%.2f cases=%d",
            args.output,
            len(text.encode("utf-8")),
            elapsed,
            n_cases,
        )
        for w in warnings_all:
            LOG.warning("%s", w)
    finally:
        db.close()

    shutil.rmtree(upload_root, ignore_errors=True)
    shutil.rmtree(db_path.parent, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
