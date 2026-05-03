# TC002 / blurry_bill.jpeg (primary)

| Key | Value |
| --- | --- |
| `actual_type` | PHARMACY_BILL |
| `case_id` | TC002 |
| `case_name` | Unreadable Document |
| `document_style` | hybrid |
| `file_id` | F004 |
| `file_name` | blurry_bill.jpeg |
| `output_fixture` | fixtures/TC002/blurry_bill.jpeg |
| `quality` | UNREADABLE |
| `variant` | primary |

---

## Prompt (paste below)

CRITICAL — Indian clinic pad (handwritten on printed template):
• Pre-printed: logo, doctor/clinic name block (if on pad), and static labels (Patient:, Date:, Rx:, etc.).
• Ballpoint INK: patient details, dates, diagnosis, every medicine line, amounts, signature — wobbly real pen, not the header font.
• Refuse: one clean font for the whole page. Require: clear print (header/labels) vs pen (filled fields).


Photorealistic smartphone-style photo of one physical Indian pharmacy bill on paper (India). 
Real desk/table, sheets resting flat or slight curl — not a screenshot or UI mockup.
Handwritten by the doctor on a printed layout template.

GROUND TRUTH — copy these strings onto the page as the doctor/staff would write them (pen for hybrid); spelling and numbers must match:
{
  "pharmacy": "Health First Pharmacy",
  "drug_license": "KA-BLR-XXXX",
  "address": "22 Brigade Road, Bengaluru",
  "bill_no": "HFP-24-09821",
  "date": "01-Nov-2024",
  "patient_name": "Rajesh Kumar",
  "doctor": "Dr. Arun Sharma",
  "items": [
    {
      "medicine": "Paracetamol 650",
      "batch": "A2341",
      "exp": "03/26",
      "qty": 15,
      "mrp": 2.5,
      "amt": 37.5
    },
    {
      "medicine": "Vitamin C 500",
      "batch": "B7821",
      "exp": "06/26",
      "qty": 10,
      "mrp": 4.0,
      "amt": 40.0
    }
  ],
  "subtotal": 77.5,
  "discount_pct": 5,
  "net": 73.62
}

Layout guide (section structure):
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
└─────────────────────────────────────────────────────┘

Style notes: Hybrid pad: printed letterhead + printed field labels only; all filled values in pen (see CRITICAL block at top of prompt).

Capture: Very poor phone capture: heavy motion/defocus blur, strong overhead shadows or glare, steep perspective distortion. Most text is illegible — only large headings may be readable.

Context: Indian addresses, ₹ amounts, state medical registration (e.g. KA/45678/2015), GSTIN if on form, rubber stamp where appropriate.

Avoid: a single computer font for all text on the page; perfectly typeset body text in the same face as the header.
