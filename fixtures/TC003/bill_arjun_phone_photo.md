# TC003 / bill_arjun_phone_photo.jpeg (overlay: phone_photo)

| Key | Value |
| --- | --- |
| `actual_type` | HOSPITAL_BILL |
| `case_id` | TC003 |
| `case_name` | Documents Belong to Different Patients |
| `document_style` | hybrid |
| `file_id` | F006 |
| `file_name` | bill_arjun_phone_photo.jpeg |
| `output_fixture` | fixtures/TC003/bill_arjun_phone_photo.jpeg |
| `quality` | HANDWRITTEN |
| `style_overlay` | phone_photo |
| `variant` | phone_photo |
| `variant_of` | bill_arjun.jpeg |

---

## Prompt (paste below)

CRITICAL — Indian clinic pad (handwritten on printed template):
• Pre-printed: logo, doctor/clinic name block (if on pad), and static labels (Patient:, Date:, Rx:, etc.).
• Ballpoint INK: patient details, dates, diagnosis, every medicine line, amounts, signature — wobbly real pen, not the header font.
• Refuse: one clean font for the whole page. Require: clear print (header/labels) vs pen (filled fields).


Photorealistic smartphone-style photo of one physical Indian hospital/clinic bill on paper (India). 
Real desk/table, sheets resting flat or slight curl — not a screenshot or UI mockup.
Handwritten by the doctor on a printed layout template.

GROUND TRUTH — copy these strings onto the page as the doctor/staff would write them (pen for hybrid); spelling and numbers must match:
{
  "hospital_name": "City Medical Centre",
  "address": "12 MG Road, Bengaluru – 560001",
  "gstin": "29XXXXX1234X1ZX",
  "bill_no": "CMC/2024/08321",
  "date": "01-Nov-2024",
  "patient_name": "Arjun Mehta",
  "age_gender": "39 / Male",
  "referring_doctor": "Dr. Arun Sharma",
  "line_items": [
    {
      "description": "Consultation Fee (OPD)",
      "qty": 1,
      "rate": 1000.0,
      "amount": 1000.0
    },
    {
      "description": "CBC",
      "qty": 1,
      "rate": 200.0,
      "amount": 200.0
    },
    {
      "description": "Dengue NS1",
      "qty": 1,
      "rate": 300.0,
      "amount": 300.0
    }
  ],
  "subtotal": 1500.0,
  "gst": 0.0,
  "total": 1500.0,
  "payment_mode": "UPI"
}

Layout guide (section structure):
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
└─────────────────────────────────────────────────────┘

Style notes: Hybrid pad: printed letterhead + printed field labels only; all filled values in pen (see CRITICAL block at top of prompt).

Capture: Clear indoor photo of real paper: focus on ballpoint ink texture; natural hand or phone shadow OK. Not a flat digital mockup — looks like a physical Rx/bill with pen writing.
Additional overlay: Overlay: casual handheld phone shot — noticeable skew, edge of table or hand visible, uneven shadows from overhead light.

Context: Indian addresses, ₹ amounts, state medical registration (e.g. KA/45678/2015), GSTIN if on form, rubber stamp where appropriate.

Avoid: a single computer font for all text on the page; perfectly typeset body text in the same face as the header.
