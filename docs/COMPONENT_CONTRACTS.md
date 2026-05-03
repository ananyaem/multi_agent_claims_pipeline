# Component contracts

## `IntakeAgent`

- **Input**: `PipelineContext.submission`, `PolicyService`
- **Output**: Sets `ctx.member`, `ctx.category_key`; or `halted_reason` / `member_message`
- **Errors**: none raised — halts via `halted_reason`

## `DocumentVerificationAgent`

- **Input**: submission documents, `document_requirements[category]`
- **Output**: pass or `halted_reason=WRONG_DOCUMENTS` + actionable `member_message`

## `ReadabilityAgent`

- **Input**: documents with optional `quality`
- **Output**: pass or `halted_reason=NEEDS_REUPLOAD`

## `ExtractionAgent`

- **Input**: documents; optional `LLMProvider`
- **Output**: `ctx.extracted_documents[]`; calls LLM when `content` missing
- **Errors**: degraded path lowers confidence

## `CrossValidationAgent`

- **Input**: extracted + submission metadata (`patient_name_on_doc`)
- **Output**: pass or `halted_reason=PATIENT_MISMATCH`

## `PolicyEngine`

- **Input**: `ctx.policy_terms`, extracted data, submission
- **Output**: `policy_findings`, `rejection_reasons` (WAITING_PERIOD, PRE_AUTH_MISSING, PER_CLAIM_EXCEEDED, EXCLUDED_CONDITION, …)

## `FraudAgent`

- **Input**: `claims_history`, `simulate_component_failure`
- **Output**: `fraud_signals`, `fraud_score`; may append `degraded_components`

## `AdjudicationAgent`

- **Input**: policy + fraud outcomes, line items, network flags
- **Output**: **only component that sets** `decision`, `approved_amount`, `financial_breakdown`, headline `confidence` (harmonic aggregate)

## `LLMProvider` (ABC)

- **Method**: `extract_document(claim_id, file_id, doc_type, image_bytes, mime_type, hint) -> (dict, confidence)`

## `GeminiProvider`

- Implements `LLMProvider` using `google-genai`, JSON response mode.

## `RedisLLMProvider`

- Enqueues JSON payload on `llm:queue`; blocks on `llm:result:{req_id}` until LLM worker responds or timeout.
