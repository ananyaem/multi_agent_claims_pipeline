# EVAL_REPORT (fixture, no LLM)

Generated: 2026-05-02T17:00:39.948488+00:00

## TC001 — Wrong Document Uploaded

### Output

{
  "halted_reason": "WRONG_DOCUMENTS",
  "decision": null,
  "approved_amount": null,
  "confidence": 0.9747692307692307,
  "member_message": "Your claim is missing required documents. You uploaded: PRESCRIPTION (2 file(s)). This claim type requires: PRESCRIPTION, HOSPITAL_BILL. Please upload the missing document type(s) \u2014 for example, a Hospital Bill is required but we only received Prescription(s).",
  "rejection_reasons": [],
  "degraded_components": []
}

---

## TC002 — Unreadable Document

### Output

{
  "halted_reason": "NEEDS_REUPLOAD",
  "decision": null,
  "approved_amount": null,
  "confidence": 0.9354595984421673,
  "member_message": "We could not read the file 'blurry_bill.jpg' (PHARMACY_BILL). Please re-upload a clearer photo or scan of this document so we can process your claim.",
  "rejection_reasons": [],
  "degraded_components": []
}

---

## TC003 — Documents Belong to Different Patients

### Output

{
  "halted_reason": "PATIENT_MISMATCH",
  "decision": null,
  "approved_amount": null,
  "confidence": 0.6079428172058189,
  "member_message": "The documents appear to belong to different patients. We found these patient names: F005: Rajesh Kumar; F006: Arjun Mehta. Please upload documents that all relate to the same patient and match your membership.",
  "rejection_reasons": [],
  "degraded_components": [
    "ExtractionAgent",
    "ExtractionAgent"
  ]
}

---

## TC004 — Clean Consultation — Full Approval

### Output

{
  "halted_reason": null,
  "decision": "APPROVED",
  "approved_amount": 1350.0,
  "confidence": 0.9494644721320405,
  "member_message": "Claim approved. Approved amount \u20b91,350.00. ",
  "rejection_reasons": [],
  "degraded_components": []
}

---

## TC005 — Waiting Period — Diabetes

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.950539864670516,
  "member_message": "Claims for diabetes-related treatment are not covered until 2024-11-30 based on your policy waiting period (joined 2024-09-01).",
  "rejection_reasons": [
    "WAITING_PERIOD"
  ],
  "degraded_components": []
}

---

## TC006 — Dental Partial Approval — Cosmetic Exclusion

### Output

{
  "halted_reason": null,
  "decision": "PARTIAL",
  "approved_amount": 8000.0,
  "confidence": 0.9481104914085398,
  "member_message": "Claim partial. Approved amount \u20b98,000.00. ",
  "rejection_reasons": [],
  "degraded_components": []
}

---

## TC007 — MRI Without Pre-Authorization

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.9464556430318573,
  "member_message": "Pre-authorization was required for this diagnostic claim but was not obtained. Please obtain insurer pre-authorization and resubmit with the approval reference.",
  "rejection_reasons": [
    "PRE_AUTH_MISSING"
  ],
  "degraded_components": []
}

---

## TC008 — Per-Claim Limit Exceeded

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.949346861624848,
  "member_message": "Claim amount \u20b97,500 exceeds this policy's per-claim limit of \u20b95,000.",
  "rejection_reasons": [
    "PER_CLAIM_EXCEEDED"
  ],
  "degraded_components": []
}

---

## TC009 — Fraud Signal — Multiple Same-Day Claims

### Output

{
  "halted_reason": null,
  "decision": "MANUAL_REVIEW",
  "approved_amount": null,
  "confidence": 0.9350918518505682,
  "member_message": "Your claim has been flagged for manual review due to unusual claiming patterns. Same-day claim burst: 3 prior claim(s) on 2024-10-30 before this submission.",
  "rejection_reasons": [],
  "degraded_components": []
}

---

## TC010 — Network Hospital — Discount Applied

### Output

{
  "halted_reason": null,
  "decision": "APPROVED",
  "approved_amount": 3240.0,
  "confidence": 0.9494644721320405,
  "member_message": "Claim approved. Approved amount \u20b93,240.00. ",
  "rejection_reasons": [],
  "degraded_components": []
}

---

## TC011 — Component Failure — Graceful Degradation

### Output

{
  "halted_reason": null,
  "decision": "APPROVED",
  "approved_amount": 4000.0,
  "confidence": 0.8062719048977227,
  "member_message": "Claim approved. Approved amount \u20b94,000.00. ",
  "rejection_reasons": [],
  "degraded_components": [
    "FraudAgent"
  ]
}

---

## TC012 — Excluded Treatment

### Output

{
  "halted_reason": null,
  "decision": "REJECTED",
  "approved_amount": 0.0,
  "confidence": 0.9460634574636976,
  "member_message": "This claim falls under policy exclusions for obesity, weight-loss programs, or bariatric-related care.",
  "rejection_reasons": [
    "EXCLUDED_CONDITION"
  ],
  "degraded_components": []
}

---

