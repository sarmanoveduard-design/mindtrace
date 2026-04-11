# MindTrace AI Pipeline Spec

## 1. Pipeline stages

1. `answer_extract`
2. `session_aggregate`
3. `final_profile_build`

---

## 2. Source of truth by layer

### Layer 1 — answer level
- Table: `answer_extractions`
- Stage: `answer_extract`
- Source of truth:
  - current answer text
  - current question
  - active `taxonomy_version`
  - active `prompt_version` for `answer_extract`

### Layer 2 — session level
- Table: `session_aggregates`
- Stage: `session_aggregate`
- Source of truth:
  - current answers in session
  - latest successful `answer_extract`
  - active `taxonomy_version`
  - active `prompt_version` for `session_aggregate`

### Layer 3 — final profile level
- Table: `final_profiles`
- Stage: `final_profile_build`
- Source of truth:
  - latest successful `session_aggregate`
  - traceability from latest successful `answer_extract`
  - active `taxonomy_version`
  - active `prompt_version` for `final_profile_build`

---

## 3. Stage 1 — answer_extract

### input
- `answer_id`
- `session_id`
- `question_id`
- `question_code`
- `taxonomy_version_id`
- raw answer text / payload
- question context
- prompt version for `answer_extract`

### output
- `answer_extractions.normalized_output`
- schema: `answer_extraction_v1`

### writes to DB
- `answer_extractions`
- updates `answers.ai_status`

### result meaning
Returns normalized signals from one answer:
- usability
- adequacy
- signals
- contradictions
- risk flags
- summary
- overall confidence

### next step trigger
If extraction completed successfully:
- enqueue `session_aggregate`

---

## 4. Stage 2 — session_aggregate

### input
- `session_id`
- `taxonomy_version_id`
- all current answers in session
- latest successful `answer_extract` for current answer revisions
- prompt version for `session_aggregate`

### output
- `session_aggregates.aggregate_json`
- schema: `session_aggregate_v1`

### writes to DB
- `session_aggregates`
- optionally updates session processing state

### result meaning
Returns session-level aggregate:
- coverage
- aggregated signals
- deficits
- contradictions
- risk flags
- aggregate summary
- overall confidence

### next step trigger
If session is sufficiently covered or marked complete:
- enqueue `final_profile_build`

---

## 5. Stage 3 — final_profile_build

### input
- `session_id`
- `taxonomy_version_id`
- latest successful `session_aggregate`
- traceability from latest successful `answer_extract`
- prompt version for `final_profile_build`

### output
- `final_profiles.profile_json`
- schema: `final_profile_v1`

### writes to DB
- `final_profiles`
- `final_profiles.summary_text`
- session final status

### result meaning
Returns final diagnostic profile:
- readiness
- thinking profile
- values profile
- key patterns
- tensions
- risk flags
- evidence basis
- user view
- expert view
- overall confidence

---

## 6. Data flow

Answer
  -> answer_extract
  -> answer_extractions.normalized_output
  -> session_aggregate
  -> session_aggregates.aggregate_json
  -> final_profile_build
  -> final_profiles.profile_json

## 7. Read rules
answer_extract reads
- current answer revision only
- one question only
- one active taxonomy version
- one active prompt version for stage

session_aggregate reads
- current answers only
- latest successful answer_extract only
- same taxonomy_version only

final_profile_build reads
- latest successful session_aggregate only
- latest successful answer_extract only for traceability
- same taxonomy_version only

## 8. Write rules
answer_extract

Writes only:

- one extraction result for one answer and stage

session_aggregate
Writes:

- one aggregate snapshot per run
- latest successful aggregate becomes effective source

final_profile_build
Writes:

- one effective final profile per session
- latest successful final profile becomes effective source

## 9. Contract references
answer_extract contract
- docs/answer-extract-contract.md

session_aggregate contract
- docs/session-aggregate-contract.md

final_profile_build contract
- docs/final-profile-contract.md

## 10. Operational rules
- AI pipeline is async
- HTTP requests do not wait for AI completion
- all stages are versioned by prompt_versions
- all stages are bounded by taxonomy_versions
- intermediate AI results must be stored
- final profile must be built from aggregate layer, not directly from raw answers

## 11. Baseline v1
MindTrace AI core is approved if:

- one answer produces answer_extraction_v1
- one session produces session_aggregate_v1
- one completed session produces final_profile_v1
- all three layers are stored in DB
- all three layers are traceable through taxonomy and prompt versions