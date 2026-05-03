# TC007 / F013_partial_doc.jpeg (overlay: partial_doc)

| Key | Value |
| --- | --- |
| `actual_type` | LAB_REPORT |
| `case_id` | TC007 |
| `case_name` | MRI Without Pre-Authorization |
| `document_style` | hybrid |
| `file_id` | F013 |
| `file_name` | F013_partial_doc.jpeg |
| `output_fixture` | fixtures/TC007/F013_partial_doc.jpeg |
| `quality` | HANDWRITTEN |
| `style_overlay` | partial_doc |
| `variant` | partial_doc |
| `variant_of` | F013.jpeg |

---

## Prompt (paste below)

CRITICAL — Indian clinic pad (handwritten on printed template):
• Pre-printed: logo, doctor/clinic name block (if on pad), and static labels (Patient:, Date:, Rx:, etc.).
• Ballpoint INK: patient details, dates, diagnosis, every medicine line, amounts, signature — wobbly real pen, not the header font.
• Refuse: one clean font for the whole page. Require: clear print (header/labels) vs pen (filled fields).
 LAB REPORT: header/patient block and tabular results may look laser-printed; pathologist signature (and any handwritten remark line) must be pen ink.

Photorealistic smartphone-style photo of one physical Indian medical lab report on paper (India). 
Real desk/table, sheets resting flat or slight curl — not a screenshot or UI mockup.
Handwritten by the doctor on a printed layout template.

GROUND TRUTH — copy these strings onto the page as the doctor/staff would write them (pen for hybrid); spelling and numbers must match:
{
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
    {
      "name": "MRI Lumbar Spine",
      "result": "See detailed findings",
      "unit": "—",
      "range": "—"
    }
  ],
  "pathologist": "Dr. Meena Pillai, MD (Pathology)",
  "pathologist_reg": "KA/89012/2018",
  "test_name": "MRI Lumbar Spine"
}

Layout guide (section structure):
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
└─────────────────────────────────────────────────────┘

Style notes: Hybrid pad: printed letterhead + printed field labels only; all filled values in pen (see CRITICAL block at top of prompt).

Capture: Clear indoor photo of real paper: focus on ballpoint ink texture; natural hand or phone shadow OK. Not a flat digital mockup — looks like a physical Rx/bill with pen writing.
Additional overlay: Overlay: the document is partially cut off — one edge is folded under or the phone frame clips it. Fields near that edge are incomplete or missing from the image.

Context: Indian addresses, ₹ amounts, state medical registration (e.g. KA/45678/2015), GSTIN if on form, rubber stamp where appropriate.

Avoid: a single computer font for all text on the page; perfectly typeset body text in the same face as the header.
