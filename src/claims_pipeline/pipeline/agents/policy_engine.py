from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from claims_pipeline.pipeline.context import PipelineContext


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s[:10], "%Y-%m-%d")


def _diabetes_related(diagnosis: str) -> bool:
    d = diagnosis.lower()
    return "diabetes" in d or "t2dm" in d or "diabet" in d


def _obesity_related(diagnosis: str, line_desc: str) -> bool:
    comb = f"{diagnosis} {line_desc}".lower()
    return any(
        x in comb
        for x in (
            "obesity",
            "bariatric",
            "morbid obesity",
            "weight loss",
            "diet program",
            "diet plan",
        )
    )


def run_policy_engine(ctx: PipelineContext) -> None:
    terms = ctx.policy_terms
    cat = ctx.category_key
    opd = terms.get("opd_categories", {}).get(cat, {})
    coverage = terms.get("coverage", {})
    waiting = terms.get("waiting_periods", {})
    exclusions = terms.get("exclusions", {})
    pre_auth_cfg = terms.get("pre_authorization", {})

    findings: list[str] = []
    rejection_codes: list[str] = []

    member = ctx.member or {}
    join = member.get("join_date")
    treatment = ctx.submission.get("treatment_date", "")[:10]

    # Collect diagnosis and line items from extracted docs
    diagnosis = ""
    line_items: list[dict[str, Any]] = []
    hospital_name = ctx.submission.get("hospital_name")
    for ed in ctx.extracted_documents:
        data = ed.get("data") or {}
        if data.get("diagnosis"):
            diagnosis = data["diagnosis"]
        if data.get("line_items"):
            line_items.extend(data["line_items"])
        if data.get("hospital_name") and not hospital_name:
            hospital_name = data["hospital_name"]

    total_from_bill = 0.0
    for li in line_items:
        total_from_bill += float(li.get("amount", 0))
    if total_from_bill <= 0:
        total_from_bill = float(ctx.submission.get("claimed_amount", 0))

    # Network hospital
    network_list = [h.lower() for h in terms.get("network_hospitals", [])]
    if hospital_name:
        hl = hospital_name.lower()
        ctx.network_hospital = any(n in hl or hl in n for n in network_list)
        ctx.hospital_name_for_network = hospital_name

    # Waiting period — diabetes (TC005)
    if join and treatment and _diabetes_related(diagnosis):
        join_d = _parse_date(join)
        treat_d = _parse_date(treatment)
        days = (treat_d - join_d).days
        diab_wait = waiting.get("specific_conditions", {}).get("diabetes", 90)
        if days < diab_wait:
            eligible = join_d + timedelta(days=diab_wait)
            findings.append(
                f"Diabetes-related claim within {diab_wait}-day waiting period "
                f"(joined {join}, claim date {treatment})."
            )
            rejection_codes.append("WAITING_PERIOD")
            ctx.policy_findings = findings
            ctx.rejection_reasons = rejection_codes
            ctx.member_message = (
                f"Claims for diabetes-related treatment are not covered until {eligible.strftime('%Y-%m-%d')} "
                f"based on your policy waiting period (joined {join})."
            )
            ctx.add_step_confidence(0.96, step="PolicyEngine")
            return

    # Exclusions — obesity / bariatric (TC012)
    line_text = " ".join(li.get("description", "") for li in line_items)
    if _obesity_related(diagnosis, line_text):
        findings.append("Treatment relates to obesity / weight loss / bariatric — excluded.")
        rejection_codes.append("EXCLUDED_CONDITION")
        ctx.policy_findings = findings
        ctx.rejection_reasons = rejection_codes
        ctx.member_message = (
            "This claim falls under policy exclusions for obesity, weight-loss programs, or bariatric-related care."
        )
        ctx.add_step_confidence(0.94, step="PolicyEngine")
        return

    # Pre-authorization — MRI high value (TC007)
    if cat == "diagnostic":
        presc = next((e for e in ctx.extracted_documents if e.get("actual_type") == "PRESCRIPTION"), None)
        pdata = presc.get("data") if presc else {}
        tests_ordered = []
        if isinstance(pdata.get("tests_ordered"), list):
            tests_ordered = pdata["tests_ordered"]
        mri_like = any("mri" in str(t).lower() for t in tests_ordered)
        threshold = float(opd.get("pre_auth_threshold", 10000))
        high_tests = [x.lower() for x in opd.get("high_value_tests_requiring_pre_auth", [])]
        needs_pre = mri_like or any(any(k in str(li.get("description", "")).lower() for k in ("mri", "ct scan", "pet")) for li in line_items)
        amount = max(total_from_bill, float(ctx.submission.get("claimed_amount", 0)))
        pre_done = bool(ctx.submission.get("pre_authorization_obtained"))
        if needs_pre and amount >= threshold and not pre_done:
            findings.append(f"High-cost diagnostic ({amount:.0f} INR) requires pre-authorization — not on file.")
            rejection_codes.append("PRE_AUTH_MISSING")
            ctx.policy_findings = findings
            ctx.rejection_reasons = rejection_codes
            ctx.member_message = (
                "Pre-authorization was required for this diagnostic claim but was not obtained. "
                "Please obtain insurer pre-authorization and resubmit with the approval reference."
            )
            ctx.add_step_confidence(0.95, step="PolicyEngine")
            return

    # Per-claim limit (TC008) — apply to stated claimed amount for categories where the
    # whole submission must fit under the cap. Dental (TC006) uses line-item adjudication;
    # rejection happens only when appropriate after exclusions (handled in adjudication).
    per_claim = float(coverage.get("per_claim_limit", 1e12))
    claimed = float(ctx.submission.get("claimed_amount", 0))
    if cat != "dental" and claimed > per_claim:
        findings.append(f"Claimed amount ₹{claimed:.0f} exceeds per-claim limit ₹{per_claim:.0f}.")
        rejection_codes.append("PER_CLAIM_EXCEEDED")
        ctx.policy_findings = findings
        ctx.rejection_reasons = rejection_codes
        ctx.member_message = (
            f"Claim amount ₹{claimed:,.0f} exceeds this policy's per-claim limit of ₹{per_claim:,.0f}."
        )
        ctx.add_step_confidence(0.97, step="PolicyEngine")
        return

    ctx.policy_findings = findings
    ctx.rejection_reasons = rejection_codes
    ctx.add_step_confidence(0.94, step="PolicyEngine")
