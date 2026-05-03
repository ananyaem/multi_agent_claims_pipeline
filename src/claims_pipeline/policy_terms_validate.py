"""Validate policy JSON structure and consistency before persisting a version."""

from __future__ import annotations

from typing import Any

from claims_pipeline.meta import document_types_from_test_cases
from claims_pipeline.schemas import KNOWN_DOCUMENT_TYPE_STRINGS

# Structural expectations beyond document types
_OPD_KEYS = frozenset(
    {
        "consultation",
        "diagnostic",
        "pharmacy",
        "dental",
        "vision",
        "alternative_medicine",
        "others",
    }
)


def effective_document_type_allowlist(extra: frozenset[str] | None = None) -> frozenset[str]:
    """Fixture-derived types ∪ canonical schema types ∪ optional caller extras."""
    base = frozenset(document_types_from_test_cases()) | KNOWN_DOCUMENT_TYPE_STRINGS
    return base | extra if extra else base


def validate_policy_terms(terms: dict[str, Any], extra_document_types: frozenset[str] | None = None) -> list[str]:
    """
    Return a list of human-readable errors; empty means valid.
    Document types are checked against test_cases.json ∪ canonical types ∪ optional extras.
    """
    errs: list[str] = []

    if not isinstance(terms, dict):
        return ["Policy root must be a JSON object"]

    pid = terms.get("policy_id")
    if not pid or not isinstance(pid, str) or not pid.strip():
        errs.append('Missing or invalid string field "policy_id"')

    cov = terms.get("coverage")
    if not isinstance(cov, dict):
        errs.append('Missing or invalid object "coverage"')
    else:
        for k in ("sum_insured_per_employee", "annual_opd_limit", "per_claim_limit"):
            v = cov.get(k)
            if v is None or (isinstance(v, (int, float)) and v < 0):
                errs.append(f'coverage.{k} must be a non-negative number')

    opd = terms.get("opd_categories")
    if not isinstance(opd, dict):
        errs.append('Missing or invalid object "opd_categories"')
    else:
        missing_opd = _OPD_KEYS - set(opd.keys())
        if missing_opd:
            errs.append(f"opd_categories missing keys: {sorted(missing_opd)}")
        for ck, block in opd.items():
            if not isinstance(block, dict):
                errs.append(f"opd_categories.{ck} must be an object")
                continue
            if "covered" not in block:
                errs.append(f'opd_categories.{ck} missing "covered"')

    effective_doc_types = effective_document_type_allowlist(extra_document_types)

    dr = terms.get("document_requirements")
    if not isinstance(dr, dict) or not dr:
        errs.append('Missing or empty object "document_requirements"')
    else:
        for cat, block in dr.items():
            if not isinstance(cat, str) or not cat.strip():
                errs.append("document_requirements has invalid category key")
                continue
            if not isinstance(block, dict):
                errs.append(f'document_requirements["{cat}"] must be an object')
                continue
            req = block.get("required", [])
            opt = block.get("optional", [])
            if not isinstance(req, list) or not isinstance(opt, list):
                errs.append(f'document_requirements["{cat}"] required/optional must be arrays')
                continue
            for slot in ("required", "optional"):
                types_list = req if slot == "required" else opt
                for dt in types_list:
                    if not isinstance(dt, str) or not dt.strip():
                        errs.append(f'document_requirements["{cat}"].{slot} has invalid entry')
                    elif dt not in effective_doc_types:
                        errs.append(
                            f'Unknown document type "{dt}" in document_requirements["{cat}"].{slot} '
                            "(must appear in test_cases.json actual_type values or the canonical document-type set)"
                        )

    members = terms.get("members")
    if members is not None:
        if not isinstance(members, list):
            errs.append('"members" must be an array when present')
        else:
            seen: set[str] = set()
            for i, m in enumerate(members):
                if not isinstance(m, dict):
                    errs.append(f"members[{i}] must be an object")
                    continue
                mid = m.get("member_id")
                if not mid or not isinstance(mid, str):
                    errs.append(f"members[{i}] missing member_id")
                elif mid in seen:
                    errs.append(f'duplicate member_id "{mid}"')
                else:
                    seen.add(mid)

    ft = terms.get("fraud_thresholds")
    if ft is not None and not isinstance(ft, dict):
        errs.append('"fraud_thresholds" must be an object when present')

    return errs
