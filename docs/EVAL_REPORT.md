# EVAL_REPORT (Gemini vision + extraction)

Generated: 2026-05-03T19:44:47.665093+00:00

## TC001 — Wrong Document Uploaded

### Expected (assignment)

{
  "decision": null,
  "system_must": [
    "Stop before making any claim decision",
    "Tell the member specifically what document type was uploaded and what is needed instead",
    "Not return a generic error \u2014 the message must name the uploaded document type and the required document type"
  ]
}

### Output

{
  "halted_reason": "WRONG_DOCUMENTS",
  "decision": null,
  "approved_amount": null,
  "confidence": 0.9797938144329897,
  "member_message": "Your claim is missing required documents. You uploaded: PRESCRIPTION (2 file(s)). This claim type requires: PRESCRIPTION, HOSPITAL_BILL. Please upload the missing document type(s) \u2014 for example, a Hospital Bill is required but we only received Prescription(s).",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {
    "uploaded_types": [
      "PRESCRIPTION"
    ],
    "required_types": [
      "PRESCRIPTION",
      "HOSPITAL_BILL"
    ],
    "missing": [
      "HOSPITAL_BILL"
    ]
  },
  "financial_breakdown": {},
  "fraud_signals": [],
  "waiting_period_medical": null,
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.96
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.979794,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.96
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": null,
    "documents": []
  }
}

---

## TC002 — Unreadable Document

### Expected (assignment)

{
  "decision": null,
  "system_must": [
    "Identify that the pharmacy bill cannot be read",
    "Ask the member to re-upload that specific document",
    "Not reject the claim outright"
  ]
}

### Output

{
  "halted_reason": "NEEDS_REUPLOAD",
  "decision": null,
  "approved_amount": null,
  "confidence": 0.9619255541061495,
  "member_message": "We could not read the file 'blurry_bill.jpeg' (PHARMACY_BILL). Please re-upload a clearer photo or scan of this document so we can process your claim.",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {
    "file_id": "F004",
    "issue": "UNREADABLE",
    "source": "fixture_marker"
  },
  "financial_breakdown": {},
  "fraud_signals": [],
  "waiting_period_medical": null,
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 1.0
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F003",
      "confidence": 0.99
    },
    {
      "step": "ExtractionAgent:F004",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.85
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.961926,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 1.0,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F003": 0.99,
        "ExtractionAgent:F004": 0.98,
        "ReadabilityAgent": 0.85
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": null,
    "documents": [
      {
        "file_id": "F003",
        "file_name": "prescription.jpeg",
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "age": "39 years",
          "gender": "Male",
          "date": "01-Nov-2024",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": "KA/45678/2015",
          "doctor_qualification": "MBBS, MD (Internal Medicine)",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Viral Fever",
          "medicines": [
            {
              "name": "Tab Paracetamol 650mg",
              "dosage": "1-1-1",
              "duration": "5 days"
            },
            {
              "name": "Tab Vitamin C 500mg",
              "dosage": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement"
        },
        "extraction_confidence": 0.99,
        "extraction_meta": {
          "confidence": 0.99,
          "readability": "GOOD",
          "notes": "Handwriting is very clear and legible; printed header contains full practice details."
        },
        "readability_metrics": {
          "laplacian_variance": 4007.333970714495,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F004",
        "file_name": "blurry_bill.jpeg",
        "document_type": "PHARMACY_BILL",
        "extracted_fields": {
          "patient_name": "Alexander Morgan",
          "doctor_name": "Dr. Sarah Jenkins",
          "doctor_registration": "REG-882109",
          "diagnosis": "Bacterial Bronchitis",
          "date": "2023-11-14",
          "medicines": [
            "Azithromycin 500mg",
            "Guaifenesin Syrup",
            "Salbutamol Inhaler"
          ],
          "line_items": [
            {
              "description": "Azithromycin 500mg (3 tablets)",
              "amount": 12.5
            },
            {
              "description": "Guaifenesin Syrup (100ml)",
              "amount": 8.75
            },
            {
              "description": "Salbutamol Inhaler (1 unit)",
              "amount": 15.0
            },
            {
              "description": "Consultation Fee / Pharmacy Handling",
              "amount": 2.0
            }
          ],
          "total": 38.25,
          "hospital_name": "Green Valley Medical Center Pharmacy",
          "tests_ordered": []
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is a clearly legible pharmacy bill with no blur or occlusions."
        },
        "readability_metrics": null
      }
    ]
  }
}

---

## TC003 — Documents Belong to Different Patients

### Expected (assignment)

{
  "decision": null,
  "system_must": [
    "Detect that the documents belong to different people",
    "Surface this to the member with the specific names found on each document",
    "Not proceed to a claim decision"
  ]
}

### Output

{
  "halted_reason": "PATIENT_MISMATCH",
  "decision": null,
  "approved_amount": null,
  "confidence": 0.9736229498770445,
  "member_message": "The documents appear to belong to different patients. We found these patient names: F005: Rajesh Kumar; F006: Arjun Mehta. Please upload documents that all relate to the same patient and match your membership.",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {
    "names": [
      [
        "F005",
        "Rajesh Kumar"
      ],
      [
        "F006",
        "Arjun Mehta"
      ]
    ]
  },
  "financial_breakdown": {},
  "fraud_signals": [],
  "waiting_period_medical": null,
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F005",
      "confidence": 1.0
    },
    {
      "step": "ExtractionAgent:F006",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.92
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.973623,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F005": 1.0,
        "ExtractionAgent:F006": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.92
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": null,
    "documents": [
      {
        "file_id": "F005",
        "file_name": "prescription_rajesh.jpeg",
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "age": "39 years",
          "gender": "Male",
          "date": "01-Nov-2024",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": "KA/45678/2015",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Viral Fever",
          "medicines": [
            {
              "name": "Tab Paracetamol 650mg",
              "dosage": "1-1-1",
              "duration": "5 days"
            },
            {
              "name": "Tab Vitamin C 500mg",
              "dosage": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement"
        },
        "extraction_confidence": 1.0,
        "extraction_meta": {
          "confidence": 1.0,
          "readability": "GOOD",
          "notes": "Clear, legible handwritten and printed text in a standard prescription format."
        },
        "readability_metrics": {
          "laplacian_variance": 3556.19052028505,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F006",
        "file_name": "bill_arjun.jpeg",
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "CITY MEDICAL CENTRE",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "gstin": "29XXXXX1234X1ZX",
          "phone": "080-XXXXXXXX",
          "bill_number": "CMC/2024/08321",
          "date": "01-Nov-2024",
          "patient_name": "Arjun Mehta",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": null,
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "medicines": [],
          "line_items": [
            {
              "description": "Consultation Fee (OPD)",
              "quantity": 1,
              "rate": 1000.0,
              "amount": 1000.0
            },
            {
              "description": "CBC",
              "quantity": 1,
              "rate": 200.0,
              "amount": 200.0
            },
            {
              "description": "Dengue NS1",
              "quantity": 1,
              "rate": 300.0,
              "amount": 300.0
            }
          ],
          "subtotal": 1500.0,
          "gst_amount": 0.0,
          "total": 1500.0,
          "payment_mode": "UPI",
          "received_by": "S. Priya"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The bill is clearly legible with no obstructions or blurriness."
        },
        "readability_metrics": {
          "laplacian_variance": 4120.613978836755,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC004 — Clean Consultation — Full Approval

### Expected (assignment)

{
  "decision": "APPROVED",
  "approved_amount": 1350,
  "notes": "10% co-pay applied on consultation category (\u20b9150 deducted)",
  "confidence_score": "above 0.85"
}

### Output

{
  "halted_reason": null,
  "decision": "APPROVED",
  "approved_amount": 1350.0,
  "confidence": 0.9397770815330636,
  "member_message": "Claim approved. Approved amount \u20b91,350.00. Eligible charges totaled \u20b91,500.00. Your plan's 10% co-pay is then applied to that amount; the figure above is the insurer's payable share.",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "eligible_line_total": 1500.0,
    "network_discount_percent": 0,
    "network_hospital": false,
    "after_network": 1500.0,
    "copay_percent": 10.0,
    "after_copay_before_cap": 1350.0,
    "sub_limit": 2000.0,
    "payable": 1350.0,
    "rejected_lines": [],
    "approved_line_items": [
      "Consultation Fee (\u20b91,000.00)",
      "CBC Test (\u20b9300.00)",
      "Dengue NS1 Test (\u20b9200.00)"
    ],
    "per_claim_limit": 5000
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "The bundle specifies a diagnosis of Viral Fever with no ophthalmic complaints or cataract procedures mentioned."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications (e.g., Metformin, Insulin) or glycemic markers are present in the prescription or bill."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "The case relates to acute fever and body ache; no surgical evaluation for hernia is noted."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "There is no record of antihypertensive medication or chronic blood pressure management."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Clinical picture is acute infection (Viral Fever/Dengue screen) rather than degenerative joint disease requiring arthroplasty."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No obstetric history, prenatal labs, or maternity-specific care documented."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric medications or mental health diagnoses identified."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Treatment is focused on acute viral symptoms; no obesity-specific drugs or bariatric pathway noted."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid hormone therapy or diagnostic thyroid tests (e.g., TSH) ordered."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The clinical bundle clearly describes an acute episode of Viral Fever with screening for Dengue. It shows no clinical relation to the chronic or elective conditions listed in the waiting-period buckets.",
    "source": "gemini_clinical"
  },
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F007",
      "confidence": 1.0
    },
    {
      "step": "ExtractionAgent:F008",
      "confidence": 0.99
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.94
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.94
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.939777,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F007": 1.0,
        "ExtractionAgent:F008": 0.99,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 0.75,
        "FraudAgent": 0.91,
        "PolicyEngine": 0.94,
        "AdjudicationAgent": 0.94
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "The bundle specifies a diagnosis of Viral Fever with no ophthalmic complaints or cataract procedures mentioned."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications (e.g., Metformin, Insulin) or glycemic markers are present in the prescription or bill."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "The case relates to acute fever and body ache; no surgical evaluation for hernia is noted."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "There is no record of antihypertensive medication or chronic blood pressure management."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Clinical picture is acute infection (Viral Fever/Dengue screen) rather than degenerative joint disease requiring arthroplasty."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No obstetric history, prenatal labs, or maternity-specific care documented."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric medications or mental health diagnoses identified."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Treatment is focused on acute viral symptoms; no obesity-specific drugs or bariatric pathway noted."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid hormone therapy or diagnostic thyroid tests (e.g., TSH) ordered."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The clinical bundle clearly describes an acute episode of Viral Fever with screening for Dengue. It shows no clinical relation to the chronic or elective conditions listed in the waiting-period buckets.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F007",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "patient_age": "39 years",
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": "KA/45678/2015",
          "doctor_specialization": "MBBS, MD (Internal Medicine)",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "date": "01-Nov-2024",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Viral Fever",
          "medicines": [
            {
              "description": "Tab Paracetamol 650mg",
              "frequency": "1-1-1",
              "duration": "5 days"
            },
            {
              "description": "Tab Vitamin C 500mg",
              "frequency": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement",
          "line_items": [],
          "total": null
        },
        "extraction_confidence": 1.0,
        "extraction_meta": {
          "confidence": 1.0,
          "readability": "GOOD",
          "notes": "The prescription is clearly written and all text is legible."
        },
        "readability_metrics": {
          "laplacian_variance": 82.39610164730387,
          "image_readable_hint": "low_sharpness"
        }
      },
      {
        "file_id": "F008",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "CITY CLINIC, BENGALURU",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "hospital_phone": "080-1234-5678",
          "hospital_gstin": "29XXXXX1234X1ZX",
          "bill_number": "CMC/2024/08321",
          "date": "2024-11-01",
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": null,
          "medicines": [],
          "tests_ordered": [
            "CBC Test",
            "Dengue NS1 Test"
          ],
          "line_items": [
            {
              "description": "Consultation Fee",
              "quantity": 1,
              "rate": 1000.0,
              "amount": 1000.0
            },
            {
              "description": "CBC Test",
              "quantity": 1,
              "rate": 300.0,
              "amount": 300.0
            },
            {
              "description": "Dengue NS1 Test",
              "quantity": 1,
              "rate": 200.0,
              "amount": 200.0
            }
          ],
          "subtotal": 1500.0,
          "tax_amount": 0.0,
          "total": 1500.0,
          "payment_mode": "UPI"
        },
        "extraction_confidence": 0.99,
        "extraction_meta": {
          "confidence": 0.99,
          "readability": "GOOD",
          "notes": "Clear and legible hospital bill with no major artifacts or missing information."
        },
        "readability_metrics": {
          "laplacian_variance": 5332.723878795866,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC005 — Waiting Period — Diabetes

### Expected (assignment)

{
  "decision": "REJECTED",
  "rejection_reasons": [
    "WAITING_PERIOD"
  ],
  "system_must": [
    "State the date from which the member will be eligible for diabetes-related claims"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.9656270701835518,
  "member_message": "Claims related to diabetes are not covered until 2024-11-30 based on your policy waiting periods (joined 2024-09-01).",
  "rejection_reasons": [
    "WAITING_PERIOD"
  ],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "reason": [
      "WAITING_PERIOD"
    ],
    "policy_notes": [
      "Waiting period (diabetes, 90 days): joined 2024-09-01, claim date 2024-10-15, clinical review cites: Explicit diagnosis of Type 2 Diabetes Mellitus and prescription of antidiabetic medications: Metformin and Glimepiride.."
    ]
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "diabetes",
        "related": true,
        "confidence": 1.0,
        "clinical_evidence": "Explicit diagnosis of Type 2 Diabetes Mellitus and prescription of antidiabetic medications: Metformin and Glimepiride."
      },
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of ophthalmic evaluation or cataract surgery."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of hernia diagnosis or surgical repair."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No documentation of high blood pressure or antihypertensive therapy."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of arthroplasty or orthopedic pre-operative workup."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of pregnancy or obstetric care."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric diagnoses or psychotropic medications noted."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No bariatric or medically supervised obesity treatment noted."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid-related diagnoses or medications (e.g., Levothyroxine)."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The clinical bundle confirms management of Type 2 Diabetes Mellitus. While the patient presented with acute fever and body ache (suspected Dengue), the document clearly records chronic diabetes management with specific oral hypoglycemic agents.",
    "source": "gemini_clinical"
  },
  "policy_findings": [
    "Waiting period (diabetes, 90 days): joined 2024-09-01, claim date 2024-10-15, clinical review cites: Explicit diagnosis of Type 2 Diabetes Mellitus and prescription of antidiabetic medications: Metformin and Glimepiride.."
  ]
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F009",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F010",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 1.0
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.96
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.93
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.965627,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F009": 0.98,
        "ExtractionAgent:F010": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 1.0,
        "PolicyEngine": 0.96,
        "FraudAgent": 0.91,
        "AdjudicationAgent": 0.93
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "diabetes",
          "related": true,
          "confidence": 1.0,
          "clinical_evidence": "Explicit diagnosis of Type 2 Diabetes Mellitus and prescription of antidiabetic medications: Metformin and Glimepiride."
        },
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of ophthalmic evaluation or cataract surgery."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of hernia diagnosis or surgical repair."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No documentation of high blood pressure or antihypertensive therapy."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of arthroplasty or orthopedic pre-operative workup."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of pregnancy or obstetric care."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric diagnoses or psychotropic medications noted."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No bariatric or medically supervised obesity treatment noted."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid-related diagnoses or medications (e.g., Levothyroxine)."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The clinical bundle confirms management of Type 2 Diabetes Mellitus. While the patient presented with acute fever and body ache (suspected Dengue), the document clearly records chronic diabetes management with specific oral hypoglycemic agents.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F009",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Vikram Joshi",
          "doctor_name": "Dr. Sunil Mehta",
          "doctor_registration": "GJ/56789/2014",
          "diagnosis": "Type 2 Diabetes Mellitus",
          "date": "01-Nov-2024",
          "medicines": [
            "Tab Metformin 500mg \u2014 1-1-1 x 30 days",
            "Tab Glimepiride 1mg \u2014 1-0-0 x 30 days"
          ],
          "line_items": null,
          "total": null,
          "hospital_name": "City Medical Centre",
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "age": "39 years",
          "gender": "Male",
          "chief_complaint": "Fever since 3 days, body ache",
          "follow_up": "After 5 days if no improvement"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is very clear with legible handwriting and printed text. Some patient information and diagnosis are provided in bilingual scripts."
        },
        "readability_metrics": {
          "laplacian_variance": 3804.5874965630865,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F010",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "CITY MEDICAL CENTRE",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "hospital_phone": "080-XXXXXXXX",
          "bill_number": "CMC/2024/08321",
          "date": "2024-10-15",
          "patient_name": "Vikram Joshi",
          "patient_age": "39",
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
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
          "tax_gst": 0.0,
          "total": 3000.0,
          "payment_mode": "UPI",
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ]
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "Text is clear and handwriting is legible. Note: there is a discrepancy in the original document where the sum of line items (1500) does not match the Total Amount (3000)."
        },
        "readability_metrics": {
          "laplacian_variance": 4996.595503464485,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC006 — Dental Partial Approval — Cosmetic Exclusion

### Expected (assignment)

{
  "decision": "PARTIAL",
  "approved_amount": 8000,
  "system_must": [
    "Itemize which line items were approved and which were rejected",
    "State the reason for each rejection at the line-item level"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "PARTIAL",
  "approved_amount": 8000.0,
  "confidence": 0.931285314479626,
  "member_message": "Claim partial. Approved amount \u20b98,000.00. Covered in this payment: Root Canal Treatment (\u20b98,000.00). Not covered: Teeth Whitening (\u20b94,000.00) \u2014 excluded as cosmetic/aesthetic under your policy.",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "eligible_line_total": 8000.0,
    "network_discount_percent": 0,
    "network_hospital": false,
    "after_network": 8000.0,
    "copay_percent": 0.0,
    "after_copay_before_cap": 8000.0,
    "sub_limit": 10000.0,
    "payable": 8000.0,
    "rejected_lines": [
      "Teeth Whitening (\u20b94,000.00) \u2014 excluded as cosmetic/aesthetic under your policy"
    ],
    "approved_line_items": [
      "Root Canal Treatment (\u20b98,000.00)"
    ],
    "per_claim_limit": 5000
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Treatment is exclusively dental (Root Canal, Teeth Whitening)."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No diabetic management or anti-diabetic medications present."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No abdominal or surgical evaluation for hernia noted."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No antihypertensive treatment or blood pressure monitoring provided."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No orthopedic workup for major joint surgery found."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No obstetric or prenatal care indicated."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric drugs or counseling mentioned."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of obesity management or bariatric pathway."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid hormone therapy or related lab tests ordered."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The documentation clearly describes dental procedures (Root Canal Treatment and Teeth Whitening) and contains no clinical indicators for the specified chronic condition buckets.",
    "source": "gemini_clinical"
  },
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F011",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.93
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.94
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.94
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.931285,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F011": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.93,
        "WaitingPeriodMedicalAgent": 0.75,
        "PolicyEngine": 0.94,
        "FraudAgent": 0.91,
        "AdjudicationAgent": 0.94
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Treatment is exclusively dental (Root Canal, Teeth Whitening)."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No diabetic management or anti-diabetic medications present."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No abdominal or surgical evaluation for hernia noted."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No antihypertensive treatment or blood pressure monitoring provided."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No orthopedic workup for major joint surgery found."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No obstetric or prenatal care indicated."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric drugs or counseling mentioned."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of obesity management or bariatric pathway."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid hormone therapy or related lab tests ordered."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The documentation clearly describes dental procedures (Root Canal Treatment and Teeth Whitening) and contains no clinical indicators for the specified chronic condition buckets.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F011",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "SMILE DENTAL CLINIC",
          "bill_no": "CMC/2024/08321",
          "date": "01-Nov-2024",
          "patient_name": "Priya Singh",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": null,
          "medicines": [],
          "line_items": [
            {
              "description": "Root Canal Treatment",
              "qty": 1,
              "rate": 8000.0,
              "amount": 8000.0
            },
            {
              "description": "Teeth Whitening",
              "qty": 1,
              "rate": 4000.0,
              "amount": 4000.0
            }
          ],
          "subtotal": 12000.0,
          "gst": 0.0,
          "total": 12000.0,
          "payment_mode": "UPI",
          "received_by": "S. Ramesh",
          "tests_ordered": []
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is a clear dental clinic bill with handwritten entries that are easily legible."
        },
        "readability_metrics": {
          "laplacian_variance": 4544.114711431725,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC007 — MRI Without Pre-Authorization

### Expected (assignment)

{
  "decision": "REJECTED",
  "rejection_reasons": [
    "PRE_AUTH_MISSING"
  ],
  "system_must": [
    "Explain that pre-authorization was required and not obtained",
    "Tell the member what they should do to resubmit with pre-auth"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.94046243826246,
  "member_message": "Pre-authorization was required for this diagnostic claim but was not obtained. Please obtain insurer pre-authorization and resubmit with the approval reference.",
  "rejection_reasons": [
    "PRE_AUTH_MISSING"
  ],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "reason": [
      "PRE_AUTH_MISSING"
    ],
    "policy_notes": [
      "High-cost diagnostic (15000 INR) requires pre-authorization \u2014 not on file."
    ]
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 0.95,
        "clinical_evidence": "The bundle mentions 'Suspected Lumbar Disc Herniation'. Clinically, this is a spinal condition (displacement of intervertebral disc material) and is distinct from the abdominal, inguinal, or umbilical hernias intended by the 'hernia' policy bucket."
      },
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No ophthalmological findings or visual impairment treatments identified."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications or glucose monitoring tests (HbA1c/Blood Sugar) present."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No antihypertensive medications or history of high blood pressure recorded."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "The MRI of the Lumbar Spine relates to spinal pathology, not elective major joint replacement (hip/knee)."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No obstetric history, pregnancy-related tests, or prenatal care indicated."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric diagnoses or psychotropic medications listed."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No bariatric or medically supervised obesity management protocols mentioned."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid function tests (T3/T4/TSH) or thyroid hormone medications provided."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The patient is being investigated for acute fever (suspected Dengue) and a spinal issue (Lumbar Disc Herniation). None of the conditions in the policy waiting-period buckets are present. Specifically, 'Lumbar Disc Herniation' is a neurological/orthopedic spine condition, not an abdominal hernia.",
    "source": "gemini_clinical"
  },
  "policy_findings": [
    "High-cost diagnostic (15000 INR) requires pre-authorization \u2014 not on file."
  ]
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.9866666666666667
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F012",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F013",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F014",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.95
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.93
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.940462,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.986667,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F012": 0.98,
        "ExtractionAgent:F013": 0.98,
        "ExtractionAgent:F014": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 0.75,
        "PolicyEngine": 0.95,
        "FraudAgent": 0.91,
        "AdjudicationAgent": 0.93
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 0.95,
          "clinical_evidence": "The bundle mentions 'Suspected Lumbar Disc Herniation'. Clinically, this is a spinal condition (displacement of intervertebral disc material) and is distinct from the abdominal, inguinal, or umbilical hernias intended by the 'hernia' policy bucket."
        },
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No ophthalmological findings or visual impairment treatments identified."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications or glucose monitoring tests (HbA1c/Blood Sugar) present."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No antihypertensive medications or history of high blood pressure recorded."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "The MRI of the Lumbar Spine relates to spinal pathology, not elective major joint replacement (hip/knee)."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No obstetric history, pregnancy-related tests, or prenatal care indicated."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric diagnoses or psychotropic medications listed."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No bariatric or medically supervised obesity management protocols mentioned."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid function tests (T3/T4/TSH) or thyroid hormone medications provided."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The patient is being investigated for acute fever (suspected Dengue) and a spinal issue (Lumbar Disc Herniation). None of the conditions in the policy waiting-period buckets are present. Specifically, 'Lumbar Disc Herniation' is a neurological/orthopedic spine condition, not an abdominal hernia.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F012",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "age": "39 years",
          "gender": "Male",
          "doctor_name": "Dr. Venkat Rao",
          "doctor_registration": "AP/67890/2017",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "phone": "+91-80-XXXX",
          "date": "01-Nov-2024",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Suspected Lumbar Disc Herniation",
          "medicines": [
            {
              "name": "Tab Paracetamol 650mg",
              "dosage": "1-1-1",
              "duration": "5 days"
            },
            {
              "name": "Tab Vitamin C 500mg",
              "dosage": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1",
            "MRI Lumbar Spine"
          ],
          "follow_up": "After 5 days if no improvement",
          "line_items": null,
          "total": null
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is clear and the handwriting is highly legible."
        },
        "readability_metrics": {
          "laplacian_variance": 3805.3672735916916,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F013",
        "file_name": null,
        "document_type": "LAB_REPORT",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": "KA/89012/2018",
          "pathologist_name": "Dr. Meena Pillai",
          "date": "01-Nov-2024",
          "sample_date": "01-Nov-2024",
          "sample_id": "PD-2024-18723",
          "hospital_name": "PRECISION DIAGNOSTICS PVT LTD",
          "lab_address": "45 Jayanagar, Bengaluru",
          "lab_id": "KA-NABL-1234",
          "diagnosis": null,
          "medicines": [],
          "tests_ordered": [
            "Hemoglobin",
            "WBC Count",
            "Dengue NS1 Antigen"
          ],
          "test_results": [
            {
              "test_name": "Hemoglobin",
              "result": "13.2",
              "unit": "g/dL",
              "normal_range": "13.0 - 17.0"
            },
            {
              "test_name": "WBC Count",
              "result": "9,800",
              "unit": "/\u00b5L",
              "normal_range": "4,500 - 11,000"
            },
            {
              "test_name": "Dengue NS1 Antigen",
              "result": "NEGATIVE",
              "unit": null,
              "normal_range": null
            }
          ],
          "line_items": [],
          "total": null
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "Clear, well-lit medical lab report with handwritten entries that are easily legible."
        },
        "readability_metrics": {
          "laplacian_variance": 1383.178248033392,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F014",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "CITY MEDICAL CENTRE",
          "bill_number": "CMC/2024/08321",
          "date": "01-Nov-2024",
          "patient_name": "Rajesh Kumar",
          "age": 39,
          "gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": null,
          "medicines": [],
          "line_items": [
            {
              "description": "MRI Lumbar Spine",
              "qty": 1,
              "rate": 15000.0,
              "amount": 15000.0
            }
          ],
          "subtotal": 15000.0,
          "gst": 0.0,
          "total": 15000.0,
          "payment_mode": "UPI",
          "tests_ordered": [
            "MRI Lumbar Spine"
          ]
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "Clear handwritten and printed text. All key fields extracted successfully."
        },
        "readability_metrics": {
          "laplacian_variance": 4023.994713705231,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC008 — Per-Claim Limit Exceeded

### Expected (assignment)

{
  "decision": "REJECTED",
  "rejection_reasons": [
    "PER_CLAIM_EXCEEDED"
  ],
  "system_must": [
    "State the per-claim limit and the claimed amount clearly in the rejection message"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.9398617748943144,
  "member_message": "Claim amount \u20b97,500 exceeds this policy's per-claim limit of \u20b95,000.",
  "rejection_reasons": [
    "PER_CLAIM_EXCEEDED"
  ],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "reason": [
      "PER_CLAIM_EXCEEDED"
    ],
    "policy_notes": [
      "Claimed amount \u20b97500 exceeds per-claim limit \u20b95000."
    ]
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Diagnosis is Gastroenteritis; no ophthalmic evaluation or surgery noted."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications or blood sugar monitoring present; diagnosis is acute gastroenteritis."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Bundle shows treatment for fever and gastroenteritis; no mention of abdominal wall defects or hernia repair."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No antihypertensive therapy or blood pressure management records identified."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No orthopedic evaluation or pre-operative workup for arthroplasty; bundle concerns acute infection."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No obstetric history or prenatal care; diagnosis is gastroenteritis."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric diagnoses or psychoactive medications listed."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No weight management interventions or bariatric pathway mentioned."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid hormone therapy or antithyroid drugs prescribed; tests limited to CBC and Dengue."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The clinical bundle clearly describes an acute episode of Gastroenteritis and a fever workup (Dengue NS1), which are unrelated to any of the specific chronic or elective waiting-period conditions listed.",
    "source": "gemini_clinical"
  },
  "policy_findings": [
    "Claimed amount \u20b97500 exceeds per-claim limit \u20b95000."
  ]
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F015",
      "confidence": 0.99
    },
    {
      "step": "ExtractionAgent:F016",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.97
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.93
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.939862,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F015": 0.99,
        "ExtractionAgent:F016": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 0.75,
        "FraudAgent": 0.91,
        "PolicyEngine": 0.97,
        "AdjudicationAgent": 0.93
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Diagnosis is Gastroenteritis; no ophthalmic evaluation or surgery noted."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications or blood sugar monitoring present; diagnosis is acute gastroenteritis."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Bundle shows treatment for fever and gastroenteritis; no mention of abdominal wall defects or hernia repair."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No antihypertensive therapy or blood pressure management records identified."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No orthopedic evaluation or pre-operative workup for arthroplasty; bundle concerns acute infection."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No obstetric history or prenatal care; diagnosis is gastroenteritis."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric diagnoses or psychoactive medications listed."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No weight management interventions or bariatric pathway mentioned."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid hormone therapy or antithyroid drugs prescribed; tests limited to CBC and Dengue."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The clinical bundle clearly describes an acute episode of Gastroenteritis and a fever workup (Dengue NS1), which are unrelated to any of the specific chronic or elective waiting-period conditions listed.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F015",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "patient_age": "39 years",
          "patient_gender": "Male",
          "doctor_name": "Dr. R. Gupta",
          "doctor_registration": "DL/34567/2016",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "date": "01-Nov-2024",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Gastroenteritis",
          "medicines": [
            "Antibiotics",
            "Probiotics",
            "ORS"
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement"
        },
        "extraction_confidence": 0.99,
        "extraction_meta": {
          "confidence": 0.99,
          "readability": "GOOD",
          "notes": "Handwritten text is very legible and clear."
        },
        "readability_metrics": {
          "laplacian_variance": 1294.278893410113,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F016",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "CITY MEDICAL CENTRE",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "hospital_gstin": "29XXXXX1234X1ZX",
          "hospital_phone": "080-XXXXXXXX",
          "bill_number": "CMC/2024/08321",
          "date": "01-Nov-2024",
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "line_items": [
            {
              "description": "Consultation Fee (OPD)",
              "quantity": 1,
              "rate": 1000.0,
              "amount": 1000.0
            },
            {
              "description": "CBC (Complete Blood Count)",
              "quantity": 1,
              "rate": 200.0,
              "amount": 200.0
            },
            {
              "description": "Dengue NS1 Antigen Test",
              "quantity": 1,
              "rate": 300.0,
              "amount": 300.0
            }
          ],
          "subtotal": 1500.0,
          "gst": 0.0,
          "total": 1500.0,
          "payment_mode": "UPI",
          "received_by": "Rohit Singh (Cashier)",
          "tests_ordered": [
            "CBC (Complete Blood Count)",
            "Dengue NS1 Antigen Test"
          ]
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "Clear document with some manual corrections (crossed-out values replaced with updated figures)."
        },
        "readability_metrics": {
          "laplacian_variance": 2272.413489267154,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC009 — Fraud Signal — Multiple Same-Day Claims

### Expected (assignment)

{
  "decision": "MANUAL_REVIEW",
  "system_must": [
    "Flag the unusual same-day claim pattern",
    "Route to manual review rather than auto-rejecting",
    "Include the specific signals that triggered the flag in the output"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "MANUAL_REVIEW",
  "approved_amount": null,
  "confidence": 0.9275908421834551,
  "member_message": "Your claim has been flagged for manual review due to unusual claiming patterns. Same-day claim burst: 3 prior claim(s) on 2024-10-30 before this submission.",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "fraud_signals": [
      "Same-day claim burst: 3 prior claim(s) on 2024-10-30 before this submission."
    ],
    "fraud_score": 0.85
  },
  "fraud_signals": [
    "Same-day claim burst: 3 prior claim(s) on 2024-10-30 before this submission."
  ],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Diagnosis of Migraine and acute fever; no ophthalmological evaluation or treatment identified."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications or glycemic monitoring (HbA1c/BSL) present."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of abdominal wall defects or hernia-specific surgical evaluation."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No antihypertensive medications or documentation of high blood pressure management."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Bundle relates to acute fever and headache, not degenerative joint disease or arthroplasty."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No pregnancy-related labs, obstetric consultations, or postnatal care documented."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Diagnosis is Migraine (neurological); no psychiatric drugs or mental health conditions mentioned."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No bariatric pathways or anti-obesity pharmacological interventions identified."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid function tests (TFTs) or thyroid hormone replacement therapy noted."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The bundle specifically details treatment for an acute febrile illness (tested for Dengue) and Migraine. None of the clinical evidence correlates with the defined waiting-period condition buckets.",
    "source": "gemini_clinical"
  },
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F017",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F018",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.94
    },
    {
      "step": "FraudAgent",
      "confidence": 0.88
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.87
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.927591,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F017": 0.98,
        "ExtractionAgent:F018": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 0.75,
        "PolicyEngine": 0.94,
        "FraudAgent": 0.88,
        "AdjudicationAgent": 0.87
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Diagnosis of Migraine and acute fever; no ophthalmological evaluation or treatment identified."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications or glycemic monitoring (HbA1c/BSL) present."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of abdominal wall defects or hernia-specific surgical evaluation."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No antihypertensive medications or documentation of high blood pressure management."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Bundle relates to acute fever and headache, not degenerative joint disease or arthroplasty."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No pregnancy-related labs, obstetric consultations, or postnatal care documented."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Diagnosis is Migraine (neurological); no psychiatric drugs or mental health conditions mentioned."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No bariatric pathways or anti-obesity pharmacological interventions identified."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid function tests (TFTs) or thyroid hormone replacement therapy noted."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The bundle specifically details treatment for an acute febrile illness (tested for Dengue) and Migraine. None of the clinical evidence correlates with the defined waiting-period condition buckets.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F017",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "doctor_name": "Dr. S. Khan",
          "doctor_registration": "KA/45678/2015",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "date": "01-Nov-2024",
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Migraine",
          "medicines": [
            {
              "name": "Tab Paracetamol 650mg",
              "dosage": "1-1-1",
              "duration": "5 days"
            },
            {
              "name": "Tab Vitamin C 500mg",
              "dosage": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement",
          "verification_status": "VERIFIED by National Medical Commission and Likha Labs"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The prescription is clear and highly legible with distinct patient and medication details."
        },
        "readability_metrics": {
          "laplacian_variance": 5638.6567373960215,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F018",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": null,
          "date": "01-Nov-2024",
          "hospital_name": "CITY MEDICAL CENTRE",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "bill_number": "CMC/2024/08321",
          "medicines": [],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "line_items": [
            {
              "description": "Consultation Fee (OPD)",
              "amount": 1000.0
            },
            {
              "description": "CBC",
              "amount": 200.0
            },
            {
              "description": "Dengue NS1",
              "amount": 300.0
            }
          ],
          "subtotal": 1500.0,
          "tax_amount": 0.0,
          "total": 1500.0,
          "payment_mode": "UPI",
          "status": "PAID"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is clear and all handwritten fields are legible. Math for total matches line items."
        },
        "readability_metrics": {
          "laplacian_variance": 4477.239979839613,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC010 — Network Hospital — Discount Applied

### Expected (assignment)

{
  "decision": "APPROVED",
  "approved_amount": 3240,
  "notes": "Network discount (20%) applied first on \u20b94,500 = \u20b93,600. Co-pay (10%) applied on \u20b93,600 = \u20b9360 deducted. Final: \u20b93,240.",
  "system_must": [
    "Apply network discount before co-pay, not after",
    "Show the breakdown of discount and co-pay in the decision output"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "APPROVED",
  "approved_amount": 3240.0,
  "confidence": 0.937317428487306,
  "member_message": "Claim approved. Approved amount \u20b93,240.00. Eligible charges totaled \u20b94,500.00. As a network hospital, 20% discount is applied first (\u20b93,600.00 after discount). Your plan's 10% co-pay is then applied to that amount; the figure above is the insurer's payable share.",
  "rejection_reasons": [],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "eligible_line_total": 4500.0,
    "network_discount_percent": 20.0,
    "network_hospital": true,
    "after_network": 3600.0,
    "copay_percent": 10.0,
    "after_copay_before_cap": 3240.0,
    "sub_limit": 2000.0,
    "payable": 3240.0,
    "rejected_lines": [],
    "approved_line_items": [
      "Consultation Fee (\u20b91,500.00)",
      "Medicines (\u20b93,000.00)"
    ],
    "per_claim_limit": 5000
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No mention of ocular symptoms or ophthalmologic intervention; diagnosis is Acute Bronchitis."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications (e.g., Metformin, Insulin) or glucose testing ordered."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of hernia repair or surgical evaluation for abdominal/inguinal defects."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No antihypertensive medications or BP management protocols found."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No orthopedic findings or pre-operative workup for arthroplasty."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "Bundle relates to respiratory infection; no obstetric or prenatal care indicated."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric diagnoses or psychotropic drugs listed."
      },
      {
        "condition_key": "obesity_treatment",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No bariatric or weight management drugs/procedures mentioned."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid hormone replacement (Levothyroxine) or related diagnostic tests."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The clinical bundle provides high-confidence evidence for an acute respiratory condition (Acute Bronchitis) treated with antibiotics (Amoxicillin) and bronchodilators (Salbutamol). It does not relate to any of the specific waiting-period conditions listed.",
    "source": "gemini_clinical"
  },
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F019",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F020",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.94
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.94
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.937317,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F019": 0.98,
        "ExtractionAgent:F020": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 0.75,
        "PolicyEngine": 0.94,
        "FraudAgent": 0.91,
        "AdjudicationAgent": 0.94
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No mention of ocular symptoms or ophthalmologic intervention; diagnosis is Acute Bronchitis."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications (e.g., Metformin, Insulin) or glucose testing ordered."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of hernia repair or surgical evaluation for abdominal/inguinal defects."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No antihypertensive medications or BP management protocols found."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No orthopedic findings or pre-operative workup for arthroplasty."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "Bundle relates to respiratory infection; no obstetric or prenatal care indicated."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric diagnoses or psychotropic drugs listed."
        },
        {
          "condition_key": "obesity_treatment",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No bariatric or weight management drugs/procedures mentioned."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid hormone replacement (Levothyroxine) or related diagnostic tests."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The clinical bundle provides high-confidence evidence for an acute respiratory condition (Acute Bronchitis) treated with antibiotics (Amoxicillin) and bronchodilators (Salbutamol). It does not relate to any of the specific waiting-period conditions listed.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F019",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Deepak Shah",
          "age": "39 years",
          "gender": "Male",
          "date": "01-Nov-2024",
          "doctor_name": "Dr. S. Iyer",
          "doctor_registration": "TN/56789/2013",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Acute Bronchitis",
          "medicines": [
            {
              "name": "Amoxicillin",
              "dosage": "500mg",
              "frequency": "1-0-1",
              "duration": "7 days"
            },
            {
              "name": "Salbutamol Inhaler",
              "dosage": null,
              "frequency": "prn for cough/wheezing",
              "duration": null
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement",
          "line_items": [],
          "total": null
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is clearly legible with sharp printed and handwritten text."
        },
        "readability_metrics": {
          "laplacian_variance": 3806.862760392987,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F020",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "Apollo Hospitals",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "hospital_gstin": "29XXXXX1234X1ZX",
          "hospital_phone": "080-XXXXXXXX",
          "bill_number": "CMC/2024/08321",
          "date": "2024-11-01",
          "patient_name": "Deepak Shah",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": null,
          "line_items": [
            {
              "description": "Consultation Fee",
              "qty": 1,
              "rate": 1500.0,
              "amount": 1500.0
            },
            {
              "description": "Medicines",
              "qty": 1,
              "rate": 3000.0,
              "amount": 3000.0
            }
          ],
          "medicines": [],
          "tests_ordered": [],
          "subtotal": 1500.0,
          "tax": {
            "description": "GST (0% on medical)",
            "amount": 0.0
          },
          "total": 4500.0,
          "payment_mode": "UPI",
          "received_by": "[Cashier Name]",
          "payment_status": "PAID"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "Handwritten fields are very clear. The 'Subtotal' label on the bill is written next to the consultation amount, but the 'Total Amount' correctly sums both line items."
        },
        "readability_metrics": {
          "laplacian_variance": 3365.6005596651694,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC011 — Component Failure — Graceful Degradation

### Expected (assignment)

{
  "decision": "APPROVED",
  "system_must": [
    "Not crash or return a 500 error",
    "Indicate in the output that a component failed and was skipped",
    "Return a confidence score lower than a normal full-pipeline approval",
    "Include a note that manual review is recommended due to incomplete processing"
  ]
}

### Output

{
  "halted_reason": null,
  "decision": "APPROVED",
  "approved_amount": 4000.0,
  "confidence": 0.819855945571441,
  "member_message": "Claim approved. Approved amount \u20b94,000.00. Eligible charges totaled \u20b94,000.00.",
  "rejection_reasons": [],
  "degraded_components": [
    "FraudAgent"
  ],
  "halt_details": {},
  "financial_breakdown": {
    "eligible_line_total": 4000.0,
    "network_discount_percent": 0,
    "network_hospital": false,
    "after_network": 4000.0,
    "copay_percent": 0.0,
    "after_copay_before_cap": 4000.0,
    "sub_limit": 8000.0,
    "payable": 4000.0,
    "rejected_lines": [],
    "approved_line_items": [
      "Panchakarma Therapy (5 sessions) (\u20b93,000.00)",
      "Consultation (\u20b91,000.00)"
    ],
    "per_claim_limit": 5000
  },
  "fraud_signals": [
    "FraudAgent skipped due to simulated component failure."
  ],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 0.95,
        "clinical_evidence": "Diagnosis of 'Chronic Joint Pain' and 'Panchakarma Therapy' sessions are present, but there is no evidence of elective surgical replacement (hip/knee) or pre-operative arthroplasty workup."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications (e.g., Metformin, Insulin) or glucose-related diagnostic tests were ordered."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No documented hypertension management or antihypertensive medications (e.g., Amlodipine, Telmisartan) found in the bundle."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No mention of thyroid hormone therapy or antithyroid medications."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The bundle indicates treatment for an acute febrile illness (suspected Dengue based on Dengue NS1 test) and conservative management of chronic joint pain through Panchakarma. No evidence of any specific waiting-period conditions identified in the policy buckets.",
    "source": "gemini_clinical"
  },
  "policy_findings": []
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.99
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F021",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F022",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 0.75
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.94
    },
    {
      "step": "FraudAgent",
      "confidence": 0.5
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.94
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.819856,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.99,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F021": 0.98,
        "ExtractionAgent:F022": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 0.75,
        "PolicyEngine": 0.94,
        "FraudAgent": 0.5,
        "AdjudicationAgent": 0.94
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": [
        "FraudAgent"
      ]
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 0.95,
          "clinical_evidence": "Diagnosis of 'Chronic Joint Pain' and 'Panchakarma Therapy' sessions are present, but there is no evidence of elective surgical replacement (hip/knee) or pre-operative arthroplasty workup."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications (e.g., Metformin, Insulin) or glucose-related diagnostic tests were ordered."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No documented hypertension management or antihypertensive medications (e.g., Amlodipine, Telmisartan) found in the bundle."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No mention of thyroid hormone therapy or antithyroid medications."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The bundle indicates treatment for an acute febrile illness (suspected Dengue based on Dengue NS1 test) and conservative management of chronic joint pain through Panchakarma. No evidence of any specific waiting-period conditions identified in the policy buckets.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F021",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "doctor_name": "Vaidya T. Krishnan",
          "doctor_qualification": "BAMS",
          "doctor_registration": "AYUR/KL/2345/2019",
          "hospital_name": "City Medical Centre",
          "hospital_address": "12 MG Road, Bengaluru",
          "hospital_phone": "+91-80-XXXX",
          "patient_name": "Rajesh Kumar",
          "patient_age": "39 years",
          "patient_gender": "Male",
          "date": "01-Nov-2024",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Chronic Joint Pain",
          "medicines": [
            {
              "medicine_name": "Tab Paracetamol 650mg",
              "dosage": "1-1-1",
              "duration": "5 days"
            },
            {
              "medicine_name": "Tab Vitamin C 500mg",
              "dosage": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "treatment_suggested": "Panchakarma Therapy",
          "follow_up": "After 5 days if no improvement"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is clear and legible with well-written handwriting."
        },
        "readability_metrics": {
          "laplacian_variance": 1469.0306096333334,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F022",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "Ayur Wellness Centre",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "hospital_phone": "080-XXXXXXXX",
          "hospital_gstin": "29XXXXX1234X1ZX",
          "bill_number": "CMC/2024/08321",
          "date": "01-Nov-2024",
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "referring_doctor": "Dr. Arun Sharma",
          "line_items": [
            {
              "description": "Panchakarma Therapy (5 sessions)",
              "qty": 1,
              "rate": 3000.0,
              "amount": 3000.0
            },
            {
              "description": "Consultation",
              "qty": 1,
              "rate": 1000.0,
              "amount": 1000.0
            }
          ],
          "subtotal": 4000.0,
          "gst": 0.0,
          "total": 4000.0,
          "payment_mode": "UPI",
          "received_by": "S. Patel"
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "The document is clear and all handwritten fields are easily legible."
        },
        "readability_metrics": {
          "laplacian_variance": 5134.922083465312,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

## TC012 — Excluded Treatment

### Expected (assignment)

{
  "decision": "REJECTED",
  "rejection_reasons": [
    "EXCLUDED_CONDITION"
  ],
  "confidence_score": "above 0.90"
}

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.9677921167272774,
  "member_message": "Claims related to obesity treatment are not covered until 2025-04-01 based on your policy waiting periods (joined 2024-04-01).",
  "rejection_reasons": [
    "WAITING_PERIOD"
  ],
  "degraded_components": [],
  "halt_details": {},
  "financial_breakdown": {
    "reason": [
      "WAITING_PERIOD"
    ],
    "policy_notes": [
      "Waiting period (obesity treatment, 365 days): joined 2024-04-01, claim date 2024-10-18, clinical review cites: Direct diagnosis of Morbid Obesity (BMI 37) and line items for Bariatric Consultation and Personalised Diet and Nutrition Program.."
    ]
  },
  "fraud_signals": [],
  "waiting_period_medical": {
    "matches": [
      {
        "condition_key": "obesity_treatment",
        "related": true,
        "confidence": 1.0,
        "clinical_evidence": "Direct diagnosis of Morbid Obesity (BMI 37) and line items for Bariatric Consultation and Personalised Diet and Nutrition Program."
      },
      {
        "condition_key": "cataract",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No ophthalmic diagnoses or procedures indicated."
      },
      {
        "condition_key": "diabetes",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No anti-diabetic medications or glycemic management recorded."
      },
      {
        "condition_key": "hernia",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No hernia-specific findings or surgical evaluation."
      },
      {
        "condition_key": "hypertension",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No record of blood pressure management or antihypertensive drugs."
      },
      {
        "condition_key": "joint_replacement",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No evidence of arthroplasty workup or major joint pathology."
      },
      {
        "condition_key": "maternity",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No prenatal or obstetric care documented."
      },
      {
        "condition_key": "mental_health",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No psychiatric diagnoses or related pharmacotherapy."
      },
      {
        "condition_key": "thyroid_disorders",
        "related": false,
        "confidence": 1.0,
        "clinical_evidence": "No thyroid hormone therapy or associated diagnostics."
      }
    ],
    "insufficient_clinical_information": false,
    "review_notes": "The primary clinical presentation involves an acute febrile illness (Fever, Dengue NS1 test) which is unrelated to waiting-period buckets. However, the documented diagnosis of Morbid Obesity and the specific billing for bariatric services clearly trigger the obesity_treatment bucket.",
    "source": "gemini_clinical"
  },
  "policy_findings": [
    "Waiting period (obesity treatment, 365 days): joined 2024-04-01, claim date 2024-10-18, clinical review cites: Direct diagnosis of Morbid Obesity (BMI 37) and line items for Bariatric Consultation and Personalised Diet and Nutrition Program.."
  ]
}

### Trace (confidence + pipeline_details)

{
  "step_confidence_records": [
    {
      "step": "VisualDocumentClassificationAgent",
      "confidence": 0.995
    },
    {
      "step": "IntakeAgent",
      "confidence": 0.99
    },
    {
      "step": "DocumentVerificationAgent",
      "confidence": 0.98
    },
    {
      "step": "ExtractionAgent:F023",
      "confidence": 1.0
    },
    {
      "step": "ExtractionAgent:F024",
      "confidence": 0.98
    },
    {
      "step": "ReadabilityAgent",
      "confidence": 0.96
    },
    {
      "step": "CrossValidationAgent",
      "confidence": 0.95
    },
    {
      "step": "WaitingPeriodMedicalAgent",
      "confidence": 1.0
    },
    {
      "step": "PolicyEngine",
      "confidence": 0.96
    },
    {
      "step": "FraudAgent",
      "confidence": 0.91
    },
    {
      "step": "AdjudicationAgent",
      "confidence": 0.93
    }
  ],
  "pipeline_details": {
    "confidence": {
      "overall": 0.967792,
      "formula": "harmonic_mean_with_degraded_penalty",
      "description": "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; lower scores dominate (weakest link). Each degraded component adds one penalty score (0.5) into the same mean \u2014 it is not an arithmetic average of headline numbers.",
      "steps": {
        "VisualDocumentClassificationAgent": 0.995,
        "IntakeAgent": 0.99,
        "DocumentVerificationAgent": 0.98,
        "ExtractionAgent:F023": 1.0,
        "ExtractionAgent:F024": 0.98,
        "ReadabilityAgent": 0.96,
        "CrossValidationAgent": 0.95,
        "WaitingPeriodMedicalAgent": 1.0,
        "PolicyEngine": 0.96,
        "FraudAgent": 0.91,
        "AdjudicationAgent": 0.93
      },
      "degraded_penalty_each": 0.5,
      "degraded_components": []
    },
    "waiting_period_medical": {
      "matches": [
        {
          "condition_key": "obesity_treatment",
          "related": true,
          "confidence": 1.0,
          "clinical_evidence": "Direct diagnosis of Morbid Obesity (BMI 37) and line items for Bariatric Consultation and Personalised Diet and Nutrition Program."
        },
        {
          "condition_key": "cataract",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No ophthalmic diagnoses or procedures indicated."
        },
        {
          "condition_key": "diabetes",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No anti-diabetic medications or glycemic management recorded."
        },
        {
          "condition_key": "hernia",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No hernia-specific findings or surgical evaluation."
        },
        {
          "condition_key": "hypertension",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No record of blood pressure management or antihypertensive drugs."
        },
        {
          "condition_key": "joint_replacement",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No evidence of arthroplasty workup or major joint pathology."
        },
        {
          "condition_key": "maternity",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No prenatal or obstetric care documented."
        },
        {
          "condition_key": "mental_health",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No psychiatric diagnoses or related pharmacotherapy."
        },
        {
          "condition_key": "thyroid_disorders",
          "related": false,
          "confidence": 1.0,
          "clinical_evidence": "No thyroid hormone therapy or associated diagnostics."
        }
      ],
      "insufficient_clinical_information": false,
      "review_notes": "The primary clinical presentation involves an acute febrile illness (Fever, Dengue NS1 test) which is unrelated to waiting-period buckets. However, the documented diagnosis of Morbid Obesity and the specific billing for bariatric services clearly trigger the obesity_treatment bucket.",
      "source": "gemini_clinical"
    },
    "documents": [
      {
        "file_id": "F023",
        "file_name": null,
        "document_type": "PRESCRIPTION",
        "extracted_fields": {
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. P. Banerjee",
          "doctor_registration": "WB/34567/2015",
          "hospital_name": "City Medical Centre",
          "date": "01-Nov-2024",
          "chief_complaint": "Fever since 3 days, body ache",
          "diagnosis": "Morbid Obesity \u2014 BMI 37",
          "medicines": [
            {
              "description": "Tab Paracetamol 650mg",
              "dosage": "1-1-1",
              "duration": "5 days"
            },
            {
              "description": "Tab Vitamin C 500mg",
              "dosage": "0-0-1",
              "duration": "7 days"
            }
          ],
          "tests_ordered": [
            "CBC",
            "Dengue NS1"
          ],
          "follow_up": "After 5 days if no improvement",
          "additional_treatment": "Bariatric Consultation and Customised Diet Plan",
          "line_items": [],
          "total": null
        },
        "extraction_confidence": 1.0,
        "extraction_meta": {
          "confidence": 1.0,
          "readability": "GOOD",
          "notes": "Clear, legible digital-style prescription document."
        },
        "readability_metrics": {
          "laplacian_variance": 4099.262675106444,
          "image_readable_hint": "adequate_sharpness"
        }
      },
      {
        "file_id": "F024",
        "file_name": null,
        "document_type": "HOSPITAL_BILL",
        "extracted_fields": {
          "hospital_name": "CITY MEDICAL CENTRE",
          "hospital_address": "12 MG Road, Bengaluru - 560001",
          "bill_number": "CMC/2024/08321",
          "date": "01-Nov-2024",
          "patient_name": "Rajesh Kumar",
          "patient_age": 39,
          "patient_gender": "Male",
          "doctor_name": "Dr. Arun Sharma",
          "doctor_registration": null,
          "diagnosis": "Bariatric Consultation / Diet Program",
          "medicines": [],
          "line_items": [
            {
              "description": "Bariatric Consultation",
              "quantity": 1,
              "rate": 3000.0,
              "amount": 3000.0
            },
            {
              "description": "Personalised Diet and Nutrition Program",
              "quantity": 1,
              "rate": 5000.0,
              "amount": 5000.0
            }
          ],
          "subtotal": 8000.0,
          "tax_amount": 0.0,
          "total": 8000.0,
          "payment_mode": "UPI",
          "received_by": "Rohit Singh",
          "tests_ordered": []
        },
        "extraction_confidence": 0.98,
        "extraction_meta": {
          "confidence": 0.98,
          "readability": "GOOD",
          "notes": "Clear, well-lit document with legible handwriting."
        },
        "readability_metrics": {
          "laplacian_variance": 2254.3111384343524,
          "image_readable_hint": "adequate_sharpness"
        }
      }
    ]
  }
}

---

