#!/usr/bin/env python3
"""
Build image-generation prompts for fixture documents and write them as Markdown for manual use.

  • Writes one Markdown file per document (and per overlay variant) under fixtures/<case_id>/
    next to the target image path — paste the prompt into Gemini (web) or another image tool yourself.
  • Writes fixtures/manifest.json mapping cases and expected output paths.

assignment/test_cases.json is READ-ONLY. Tunables live here: PRIMARY_DOC_STYLE, DEFAULT_QUALITY,
DEFAULT_CONTENT, AUTO_EXTRA_OVERLAYS.

Rendering follows assignment/sample_documents_guide.md (hybrid pad, quality noise, overlays).

CLI:
  --manifest-only     Only write fixtures/manifest.json (no prompt Markdown files).
  --case-id TC004     Limit to this case_id (repeatable).

Outputs:
  fixtures/<case_id>/<stem>.md   — prompts (same folder as the intended .jpeg)
  fixtures/manifest.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
TEST_CASES_FILE = ROOT / "assignment" / "test_cases.json"
MANIFEST_FILE = FIX / "manifest.json"

# Default: pre-printed clinic pad + ballpoint fill-in ("handwritten on template").
PRIMARY_DOC_STYLE = "hybrid"
# When assignment JSON has no `quality` field (camera / capture; not document_style).
DEFAULT_QUALITY = "HANDWRITTEN"
ALLOWED_DOCUMENT_STYLE_OVERRIDES = frozenset(
    {"printed", "handwritten", "hybrid", "small_clinic_handwritten"}
)

# Second-pass overlay variants (extra prompt .md files; keys in OVERLAY_STYLE).
# Keys are (case_id, file_id) as they appear in the read-only assignment file.
AUTO_EXTRA_OVERLAYS: dict[tuple[str, str], list[str]] = {
    ("TC001", "F001"): ["stamp_over_text"],
    ("TC003", "F006"): ["phone_photo"],
    ("TC005", "F009"): ["multilingual"],
    ("TC007", "F013"): ["partial_doc"],
    ("TC008", "F016"): ["corrections"],
    ("TC009", "F017"): ["duplicate_stamp"],
}

# Fills in layout when assignment omits or partially specifies document content.
DEFAULT_CONTENT: dict[str, dict[str, Any]] = {
    "PRESCRIPTION": {
        "doctor_name": "Dr. Arun Sharma, MBBS, MD (Internal Medicine)",
        "doctor_registration": "KA/45678/2015",
        "clinic": "City Medical Centre, 12 MG Road, Bengaluru",
        "phone": "+91-80-XXXX",
        "patient_name": "Rajesh Kumar",
        "date": "01-Nov-2024",
        "age_gender": "39 years, Male",
        "chief_complaint": "Fever since 3 days, body ache",
        "diagnosis": "Viral Fever",
        "medicines": [
            "Tab Paracetamol 650mg — 1-1-1 x 5 days",
            "Tab Vitamin C 500mg — 0-0-1 x 7 days",
        ],
        "investigations": "CBC, Dengue NS1",
        "follow_up": "After 5 days if no improvement",
    },
    "HOSPITAL_BILL": {
        "hospital_name": "City Medical Centre",
        "address": "12 MG Road, Bengaluru – 560001",
        "gstin": "29XXXXX1234X1ZX",
        "bill_no": "CMC/2024/08321",
        "date": "01-Nov-2024",
        "patient_name": "Rajesh Kumar",
        "age_gender": "39 / Male",
        "referring_doctor": "Dr. Arun Sharma",
        "line_items": [
            {"description": "Consultation Fee (OPD)", "qty": 1, "rate": 1000.0, "amount": 1000.0},
            {"description": "CBC", "qty": 1, "rate": 200.0, "amount": 200.0},
            {"description": "Dengue NS1", "qty": 1, "rate": 300.0, "amount": 300.0},
        ],
        "subtotal": 1500.0,
        "gst": 0.0,
        "total": 1500.0,
        "payment_mode": "UPI",
    },
    "LAB_REPORT": {
        "lab_name": "Precision Diagnostics Pvt Ltd",
        "nabl": "NABL Accredited",
        "lab_id": "KA-NABL-1234",
        "address": "45 Jayanagar, Bengaluru",
        "patient_name": "Rajesh Kumar",
        "age_sex": "39 / Male",
        "ref_doctor": "Dr. Arun Sharma",
        "sample_date": "01-Nov-2024",
        "report_date": "01-Nov-2024",
        "sample_id": "PD-2024-18723",
        "tests": [
            {"name": "Hemoglobin", "result": "13.2", "unit": "g/dL", "range": "13.0 – 17.0"},
            {"name": "Dengue NS1 Antigen", "result": "NEGATIVE", "unit": "—", "range": "—"},
        ],
        "pathologist": "Dr. Meena Pillai, MD (Pathology)",
        "pathologist_reg": "KA/89012/2018",
    },
    "PHARMACY_BILL": {
        "pharmacy": "Health First Pharmacy",
        "drug_license": "KA-BLR-XXXX",
        "address": "22 Brigade Road, Bengaluru",
        "bill_no": "HFP-24-09821",
        "date": "01-Nov-2024",
        "patient_name": "Rajesh Kumar",
        "doctor": "Dr. Arun Sharma",
        "items": [
            {"medicine": "Paracetamol 650", "batch": "A2341", "exp": "03/26", "qty": 15, "mrp": 2.5, "amt": 37.5},
            {"medicine": "Vitamin C 500", "batch": "B7821", "exp": "06/26", "qty": 10, "mrp": 4.0, "amt": 40.0},
        ],
        "subtotal": 77.5,
        "discount_pct": 5,
        "net": 73.62,
    },
}

# Noise / capture style, auto-applied based on quality field (all doc types).
QUALITY_NOISE: dict[str, str] = {
    "GOOD": (
        "Clear indoor smartphone photo. Paper fills the frame, sharp focus, slight natural shadow."
    ),
    "BLURRY": (
        "Handheld phone photo: out-of-focus blur (soft Gaussian), mild perspective skew, "
        "uneven ambient shadows. Fine print is soft but document type is still identifiable."
    ),
    "UNREADABLE": (
        "Very poor phone capture: heavy motion/defocus blur, strong overhead shadows or glare, "
        "steep perspective distortion. Most text is illegible — only large headings may be readable."
    ),
    "HANDWRITTEN": (
        "Clear indoor photo of real paper: focus on ballpoint ink texture; natural hand or phone shadow OK. "
        "Not a flat digital mockup — looks like a physical Rx/bill with pen writing."
    ),
}

# Document rendering style (what the paper itself looks like).
DOC_STYLE: dict[str, str] = {
    "printed": (
        "Fully printed: uniform font, aligned tables, crisp typography like a laser/inkjet printout."
    ),
    "handwritten": (
        "Fully handwritten in blue/black ballpoint ink. Uneven lines, realistic Indian doctor script. "
        "Medical shorthand OK (T2DM, HTN, OA, etc.)."
    ),
    "hybrid": (
        "Hybrid pad: printed letterhead + printed field labels only; all filled values in pen "
        "(see CRITICAL block at top of prompt)."
    ),
    "small_clinic_handwritten": (
        "Small Indian clinic: mostly handwritten on plain ruled paper, no printed template. "
        "Informal columns, cashier/counter handwriting, approximate alignment."
    ),
}

# Descriptions for AUTO_EXTRA_OVERLAYS second-pass prompts (not configured in JSON).
OVERLAY_STYLE: dict[str, str] = {
    "phone_photo": (
        "Overlay: casual handheld phone shot — noticeable skew, edge of table or hand visible, "
        "uneven shadows from overhead light."
    ),
    "stamp_over_text": (
        "Overlay: blue or red round rubber registration/clinic stamp partially overlapping text "
        "(some digits or amounts obscured)."
    ),
    "multilingual": (
        "Overlay: some fields include regional Indian language script alongside English — "
        "e.g. patient name or diagnosis also written in Hindi/Telugu/Tamil next to the English text."
    ),
    "partial_doc": (
        "Overlay: the document is partially cut off — one edge is folded under or the phone frame "
        "clips it. Fields near that edge are incomplete or missing from the image."
    ),
    "corrections": (
        "Overlay: one or more rupee amounts have been crossed out in pen and rewritten nearby — "
        "a cashier corrected the entry by hand; the original figure is still visible but struck through."
    ),
    "duplicate_stamp": (
        "Overlay: a large rubber stamp reading 'ORIGINAL' or 'DUPLICATE' appears twice on the "
        "document at slightly different angles, one impression partially obscuring text."
    ),
}

# Standard layout templates from sample_documents_guide.md.
LAYOUT_GUIDES: dict[str, str] = {
    "PRESCRIPTION": """\
┌─────────────────────────────────────────────────────┐
│  Dr. Arun Sharma, MBBS, MD (Internal Medicine)      │
│  Reg. No: KA/45678/2015                             │
│  City Medical Centre, 12 MG Road, Bengaluru         │
│  Ph: +91-80-XXXXXXXX                                │
├─────────────────────────────────────────────────────┤
│  Patient: Rajesh Kumar          Date: 01-Nov-2024   │
│  Age: 39 years   Gender: M                          │
│  Chief Complaint: Fever since 3 days, body ache     │
├─────────────────────────────────────────────────────┤
│  Diagnosis: Viral Fever                             │
│                                                     │
│  Rx:                                                │
│  1. Tab Paracetamol 650mg — 1-1-1 x 5 days          │
│  2. Tab Vitamin C 500mg — 0-0-1 x 7 days            │
│                                                     │
│  Investigations: CBC, Dengue NS1                    │
│  Follow-up: After 5 days if no improvement          │
│                                                     │
│                            [Doctor's Signature]     │
│                            [Registration Stamp]     │
└─────────────────────────────────────────────────────┘""",
    "HOSPITAL_BILL": """\
┌─────────────────────────────────────────────────────┐
│  CITY MEDICAL CENTRE                                │
│  12 MG Road, Bengaluru – 560001                     │
│  GSTIN: 29XXXXX1234X1ZX                             │
│  Ph: 080-XXXXXXXX                                   │
├─────────────────────────────────────────────────────┤
│  BILL / RECEIPT                                     │
│  Bill No: CMC/2024/08321    Date: 01-Nov-2024       │
├─────────────────────────────────────────────────────┤
│  Patient Name: Rajesh Kumar                         │
│  Age/Gender: 39 / Male                              │
│  Referring Doctor: Dr. Arun Sharma                  │
├─────────────────────────────────────────────────────┤
│  DESCRIPTION                  QTY    RATE    AMOUNT │
│  Consultation Fee (OPD)        1    1000.00  1000.00│
│  CBC (Complete Blood Count)    1     200.00   200.00│
│  Dengue NS1 Antigen Test       1     300.00   300.00│
│                                                     │
│  Subtotal:                               1500.00    │
│  GST (0% on medical):                       0.00    │
│  Total Amount:                           1500.00    │
├─────────────────────────────────────────────────────┤
│  Payment Mode: Cash / UPI / Card                    │
│  Received by: [Cashier Name]    [Cashier Stamp]     │
└─────────────────────────────────────────────────────┘""",
    "LAB_REPORT": """\
┌─────────────────────────────────────────────────────┐
│  PRECISION DIAGNOSTICS PVT LTD                      │
│  NABL Accredited Lab   |   Lab ID: KA-NABL-1234     │
│  45 Jayanagar, Bengaluru   |  Ph: 080-XXXXXXXX      │
├─────────────────────────────────────────────────────┤
│  Patient: Rajesh Kumar                              │
│  Age/Sex: 39 / Male                                 │
│  Ref Doctor: Dr. Arun Sharma                        │
│  Sample Date: 01-Nov-2024   Report Date: 01-Nov-2024│
│  Sample ID: PD-2024-18723                           │
├─────────────────────────────────────────────────────┤
│  TEST NAME          RESULT    UNIT    NORMAL RANGE  │
│  Hemoglobin         13.2      g/dL    13.0 – 17.0   │
│  WBC Count          9,800     /μL     4,500 – 11,000│
│  Dengue NS1 Antigen  NEGATIVE           —           │
├─────────────────────────────────────────────────────┤
│  Dr. Meena Pillai, MD (Pathology)                   │
│  Reg. No: KA/89012/2018    [Signature & Stamp]      │
└─────────────────────────────────────────────────────┘""",
    "PHARMACY_BILL": """\
┌─────────────────────────────────────────────────────┐
│  HEALTH FIRST PHARMACY                              │
│  Drug Lic. No: KA-BLR-XXXX                          │
│  22 Brigade Road, Bengaluru                         │
├─────────────────────────────────────────────────────┤
│  Bill No: HFP-24-09821    Date: 01-Nov-2024         │
│  Patient: Rajesh Kumar    Dr: Dr. Arun Sharma       │
├─────────────────────────────────────────────────────┤
│  MEDICINE        BATCH   EXP    QTY  MRP    AMT     │
│  Paracetamol 650 A2341  03/26    15  2.50   37.50   │
│  Vitamin C 500   B7821  06/26    10  4.00   40.00   │
│                                                     │
│  Subtotal:                              77.50       │
│  Discount (5%):                         -3.88       │
│  Net Amount:                            73.62       │
├─────────────────────────────────────────────────────┤
│  Pharmacist: R. Sharma   [Stamp]                    │
└─────────────────────────────────────────────────────┘""",
}


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def effective_content(doc: dict[str, Any]) -> dict[str, Any]:
    """Merge doc content with patient_name_on_doc and type defaults."""
    actual_type = doc.get("actual_type", "PRESCRIPTION")
    raw = doc.get("content")
    base = DEFAULT_CONTENT.get(actual_type, {})
    merged = _deep_merge(base, raw) if isinstance(raw, dict) and raw else dict(base)

    if doc.get("patient_name_on_doc"):
        merged["patient_name"] = doc["patient_name_on_doc"]

    raw_dict = doc.get("content") if isinstance(doc.get("content"), dict) else {}
    if actual_type == "LAB_REPORT" and raw_dict.get("test_name") and "tests" not in raw_dict:
        merged["tests"] = [
            {"name": raw_dict["test_name"], "result": "See detailed findings", "unit": "—", "range": "—"}
        ]
    return merged


def resolve_document_style(doc: dict[str, Any]) -> str:
    """Return document_style from JSON or fall back to hybrid."""
    raw = doc.get("document_style")
    if isinstance(raw, str) and raw.strip() in ALLOWED_DOCUMENT_STYLE_OVERRIDES:
        return raw.strip()
    return PRIMARY_DOC_STYLE


def _critical_handwriting_block(actual_type: str, document_style: str) -> str:
    """
    Image models often render JSON fields as uniform printed text. Put pen-vs-print rules FIRST.

    Default (hybrid) = handwritten values on a printed clinic template.
    """
    sk = document_style if document_style in DOC_STYLE else PRIMARY_DOC_STYLE
    if sk == "printed":
        return ""
    if sk == "hybrid":
        lab = ""
        if actual_type == "LAB_REPORT":
            lab = (
                " LAB REPORT: header/patient block and tabular results may look laser-printed; "
                "pathologist signature (and any handwritten remark line) must be pen ink."
            )
        return (
            "CRITICAL — Indian clinic pad (handwritten on printed template):\n"
            "• Pre-printed: logo, doctor/clinic name block (if on pad), and static labels (Patient:, Date:, Rx:, etc.).\n"
            "• Ballpoint INK: patient details, dates, diagnosis, every medicine line, amounts, signature — wobbly real pen, "
            "not the header font.\n"
            "• Refuse: one clean font for the whole page. Require: clear print (header/labels) vs pen (filled fields).\n"
            f"{lab}\n\n"
        )
    if sk == "handwritten":
        return (
            "CRITICAL — Mostly handwritten Rx/bill: blue/black ballpoint throughout; "
            "messy real doctor script OK.\n\n"
        )
    if sk == "small_clinic_handwritten":
        return (
            "CRITICAL — Informal counter/clinic: handwritten on plain/ruled paper, rough columns.\n\n"
        )
    return ""


def build_prompt(
    actual_type: str,
    content: dict[str, Any],
    quality: str,
    document_style: str,
    overlay_style: str | None = None,
) -> str:
    """Build a concise image prompt for an Indian medical document."""
    type_labels = {
        "PRESCRIPTION": "Indian doctor's prescription (Rx)",
        "HOSPITAL_BILL": "Indian hospital/clinic bill",
        "LAB_REPORT": "Indian medical lab report",
        "PHARMACY_BILL": "Indian pharmacy bill",
    }
    type_desc = type_labels.get(actual_type, "Indian medical document")

    content_str = json.dumps(content, indent=2, ensure_ascii=False)
    layout = LAYOUT_GUIDES.get(actual_type, "")

    style_key = document_style if document_style in DOC_STYLE else PRIMARY_DOC_STYLE
    style_text = DOC_STYLE[style_key]

    noise_text = QUALITY_NOISE.get(quality, QUALITY_NOISE[DEFAULT_QUALITY])

    overlay_text = ""
    if overlay_style and overlay_style in OVERLAY_STYLE:
        overlay_text = f"\nAdditional overlay: {OVERLAY_STYLE[overlay_style]}"

    critical = _critical_handwriting_block(actual_type, style_key)

    return f"""\
{critical}Photorealistic smartphone-style photo of one physical {type_desc} on paper (India). 
Real desk/table, sheets resting flat or slight curl — not a screenshot or UI mockup.
Handwritten by the doctor on a printed layout template.

GROUND TRUTH — copy these strings onto the page as the doctor/staff would write them (pen for hybrid); spelling and numbers must match:
{content_str}

Layout guide (section structure):
{layout}

Style notes: {style_text}

Capture: {noise_text}{overlay_text}

Context: Indian addresses, ₹ amounts, state medical registration (e.g. KA/45678/2015), GSTIN if on form, rubber stamp where appropriate.

Avoid: a single computer font for all text on the page; perfectly typeset body text in the same face as the header.
"""


def _prompt_markdown_path(case_id: str, image_file_name: str) -> Path:
    """fixtures/TC001/dr_sharma_prescription.md (same folder as the .jpeg; stem matches)."""
    stem = Path(image_file_name).stem
    d = FIX / case_id
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{stem}.md"


def _write_prompt_markdown(
    md_path: Path,
    *,
    prompt_text: str,
    meta: dict[str, Any],
) -> None:
    """Write a single prompt as Markdown with a small metadata table."""
    title = str(meta.get("title", md_path.stem))
    rows = []
    for k, v in sorted(meta.items()):
        if k == "title":
            continue
        rows.append(f"| `{k}` | {v} |")
    table = "\n".join(
        [
            "| Key | Value |",
            "| --- | --- |",
            *rows,
        ]
    )
    body = "\n".join(
        [
            f"# {title}",
            "",
            table,
            "",
            "---",
            "",
            "## Prompt (paste below)",
            "",
            prompt_text.rstrip(),
            "",
        ]
    )
    md_path.write_text(body, encoding="utf-8")


def _write_manifest(manifest_documents: list[dict[str, Any]], note: str | None = None) -> None:
    manifest: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(TEST_CASES_FILE.relative_to(ROOT)),
        "fixtures_directory": str(FIX.relative_to(ROOT)),
        "documents": manifest_documents,
        "by_case_id": {
            cid: [e for e in manifest_documents if e["case_id"] == cid]
            for cid in sorted({e["case_id"] for e in manifest_documents if e.get("case_id")})
        },
    }
    if note:
        manifest["note"] = note
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)
    print(f"Wrote manifest: {MANIFEST_FILE.relative_to(ROOT)}")


def _variant_path(base: Path, style: str) -> Path:
    return base.with_name(f"{base.stem}_{style}{base.suffix}")


def _auto_variant_styles(case_id: str, file_id: str) -> list[str]:
    """Overlay styles for a second image pass (see AUTO_EXTRA_OVERLAYS)."""
    return [
        s for s in AUTO_EXTRA_OVERLAYS.get((case_id, file_id), [])
        if s in OVERLAY_STYLE
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Write prompts as Markdown (fixtures/<case_id>/) from assignment/test_cases.json."
        ),
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write fixtures/manifest.json only (no prompt Markdown).",
    )
    parser.add_argument(
        "--also-handwritten",
        action="store_true",
        help="Deprecated: no effect.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        metavar="TC00X",
        help="Only generate documents for this case_id (repeatable).",
    )
    args = parser.parse_args()

    FIX.mkdir(parents=True, exist_ok=True)

    with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    manifest_documents: list[dict[str, Any]] = []
    prompt_md_count = 0

    case_filter: set[str] | None = set(args.case_id) if args.case_id else None

    for tc in data.get("test_cases", []):
        case_id = tc.get("case_id", "")
        if case_filter is not None and case_id not in case_filter:
            continue

        case_name = tc.get("case_name", "")
        docs = tc.get("input", {}).get("documents", [])

        for doc in docs:
            file_id = doc.get("file_id", "")
            file_name = doc.get("file_name", f"{file_id}.jpeg")
            actual_type = doc.get("actual_type", "PRESCRIPTION")
            quality = doc.get("quality", DEFAULT_QUALITY)
            doc_style = resolve_document_style(doc)
            content = effective_content(doc)

            case_dir = FIX / case_id
            final_path = case_dir / file_name
            rel = str(final_path.relative_to(ROOT))

            row: dict[str, Any] = {
                "case_id": case_id,
                "case_name": case_name,
                "file_id": file_id,
                "file_name": file_name,
                "path": rel,
                "actual_type": actual_type,
                "quality": quality,
                "document_style": doc_style,
                "patient_name_on_doc": doc.get("patient_name_on_doc"),
                "variant_of": None,
            }

            prompt = build_prompt(actual_type, content, quality, doc_style)
            if not args.manifest_only:
                pm = _prompt_markdown_path(case_id, file_name)
                _write_prompt_markdown(
                    pm,
                    prompt_text=prompt,
                    meta={
                        "title": f"{case_id} / {file_name} (primary)",
                        "case_id": case_id,
                        "case_name": case_name,
                        "file_id": file_id,
                        "file_name": file_name,
                        "output_fixture": rel,
                        "actual_type": actual_type,
                        "quality": quality,
                        "document_style": doc_style,
                        "variant": "primary",
                    },
                )
                prompt_md_count += 1

            row["generated_ok"] = None
            manifest_documents.append(row)

            for extra_style in _auto_variant_styles(case_id, file_id):
                variant_path = _variant_path(final_path, extra_style)
                variant_row: dict[str, Any] = {
                    "case_id": case_id,
                    "case_name": case_name,
                    "file_id": file_id,
                    "file_name": variant_path.name,
                    "path": str(variant_path.relative_to(ROOT)),
                    "actual_type": actual_type,
                    "quality": quality,
                    "document_style": doc_style,
                    "style_overlay": extra_style,
                    "patient_name_on_doc": doc.get("patient_name_on_doc"),
                    "variant_of": file_name,
                }

                v_prompt = build_prompt(
                    actual_type, content, quality, doc_style, overlay_style=extra_style
                )
                if not args.manifest_only:
                    v_rel = str(variant_path.relative_to(ROOT))
                    vmd = _prompt_markdown_path(case_id, variant_path.name)
                    _write_prompt_markdown(
                        vmd,
                        prompt_text=v_prompt,
                        meta={
                            "title": f"{case_id} / {variant_path.name} (overlay: {extra_style})",
                            "case_id": case_id,
                            "case_name": case_name,
                            "file_id": file_id,
                            "file_name": variant_path.name,
                            "output_fixture": v_rel,
                            "actual_type": actual_type,
                            "quality": quality,
                            "document_style": doc_style,
                            "style_overlay": extra_style,
                            "variant_of": file_name,
                            "variant": extra_style,
                        },
                    )
                    prompt_md_count += 1

                variant_row["generated_ok"] = None
                manifest_documents.append(variant_row)

    if not args.manifest_only:
        print(
            f"Wrote {prompt_md_count} prompt Markdown file(s) under "
            f"{FIX.relative_to(ROOT)}/<case_id>/ — paste into Gemini (web) or another tool."
        )

    note_parts: list[str] = []
    if args.manifest_only:
        note_parts.append("manifest-only: manifest JSON only (no prompt Markdown).")
    else:
        note_parts.append(
            "Workflow: prompts in fixtures/<case_id>/*.md for manual Gemini image generation."
        )
    _write_manifest(manifest_documents, note=" ".join(note_parts))


if __name__ == "__main__":
    main()
