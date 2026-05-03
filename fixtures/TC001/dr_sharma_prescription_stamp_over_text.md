# TC001 / dr_sharma_prescription_stamp_over_text.jpeg (overlay: stamp_over_text)

| Key | Value |
| --- | --- |
| `actual_type` | PRESCRIPTION |
| `case_id` | TC001 |
| `case_name` | Wrong Document Uploaded |
| `document_style` | hybrid |
| `file_id` | F001 |
| `file_name` | dr_sharma_prescription_stamp_over_text.jpeg |
| `output_fixture` | fixtures/TC001/dr_sharma_prescription_stamp_over_text.jpeg |
| `quality` | HANDWRITTEN |
| `style_overlay` | stamp_over_text |
| `variant` | stamp_over_text |
| `variant_of` | dr_sharma_prescription.jpeg |

---

## Prompt (paste below)

CRITICAL — Indian clinic pad (handwritten on printed template):
• Pre-printed: logo, doctor/clinic name block (if on pad), and static labels (Patient:, Date:, Rx:, etc.).
• Ballpoint INK: patient details, dates, diagnosis, every medicine line, amounts, signature — wobbly real pen, not the header font.
• Refuse: one clean font for the whole page. Require: clear print (header/labels) vs pen (filled fields).


Photorealistic smartphone-style photo of one physical Indian doctor's prescription (Rx) on paper (India). 
Real desk/table, sheets resting flat or slight curl — not a screenshot or UI mockup.
Handwritten by the doctor on a printed layout template.

GROUND TRUTH — copy these strings onto the page as the doctor/staff would write them (pen for hybrid); spelling and numbers must match:
{
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
    "Tab Vitamin C 500mg — 0-0-1 x 7 days"
  ],
  "investigations": "CBC, Dengue NS1",
  "follow_up": "After 5 days if no improvement"
}

Layout guide (section structure):
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
└─────────────────────────────────────────────────────┘

Style notes: Hybrid pad: printed letterhead + printed field labels only; all filled values in pen (see CRITICAL block at top of prompt).

Capture: Clear indoor photo of real paper: focus on ballpoint ink texture; natural hand or phone shadow OK. Not a flat digital mockup — looks like a physical Rx/bill with pen writing.
Additional overlay: Overlay: blue or red round rubber registration/clinic stamp partially overlapping text (some digits or amounts obscured).

Context: Indian addresses, ₹ amounts, state medical registration (e.g. KA/45678/2015), GSTIN if on form, rubber stamp where appropriate.

Avoid: a single computer font for all text on the page; perfectly typeset body text in the same face as the header.
