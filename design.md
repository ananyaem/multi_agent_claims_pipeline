# Design Doc

## Components

### UI

1. Input/Output to the end user. Allow the user to upload files, poll the server till decision is made. Add fields from input of test_cases.json
2. Analysis layer for operations team. Can potentially offload to a tool like BigQuery etc to automatically generate analysis as needed

### Scripts

1. Generate documents following guidelines, along with different quality levels like computer generated/hand written, blur/lighting, PDF/IMG etc.
2. LLM-as-a-judge test eval.

### Backend

1. Basic CRUD for claim status
2. Admin side policy management, claim monitoring etc. with validation of policy_terms
3. Instant validation for wrong documents, take types from test_cases.json
4. AI Agent for complete validation pipeline (extraction, decision)

## Constraints from Problem Statement

- Documents can be handwritten -> Need LLM for detection, simple OCR will not suffice
- Semi-structured data -> agent to iterate with OCR
- Domain specific keywords -> agent to validate them via google search
- Domain specific reg id-validation -> function call to validate the string
- Confidence metrics computed from each stage
- Categorisation of treatment for claim processing
- Need to let users make accounts so we can apply fraud logic also

## Ideas

- Store policy_terms in db and version it immutably
- OCR with hint: Tell Gemini to do OCR on this image, while giving hint of the structure and domain etc, the hint can be generated iteratively if we find the doc layout or category or errors from some later step. Or domain vocabulary we can provide
- Explore some easy to use UI library to minimise code
- Use redis or some other event stream for pipeline events. Keep db as source of truth of status and results, event is just a trigger to refetch from db instead of race conditions and event ordering/large messages
- In the UI we can give a form which automatically adds the fields for relevant document types for each disease/claim category where applicable, and we can keep a quick classifier to check if the attached doc is roughly related to the given category (Prescription, Bill etc.) with 50% threshold (reply in the same POST), while in the final pipeline we'll do exact checks later (a job to be polled for status). User will pick the category of the doc on their own, we'll validate it roughly. Also allow Others
- dont store test_cases in db, they can be loaded in the script
- LLM/AI Agents give us signals and metadata from extraction. Final claim logic to be deterministic based on policy_terms. 
- Look at policy_terms.json and test_cases.json to find which fields etc to put in the db
- Will need to buy credits of Gemini or OpenAI or any other decent LLM, MVP so cost not much problem (low scale)
- Look at free/cheap hosting which allows to deploy a docker
