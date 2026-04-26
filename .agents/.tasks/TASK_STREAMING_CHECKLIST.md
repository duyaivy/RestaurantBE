# Task — Convert Chatbot HTTP Response to Streaming Response (RAG + NVIDIA API)

**Task Type:** Backend API Enhancement / Streaming Refactor  
**Priority:** High  
**Source of Truth:** Backend overview rules + existing chatbot code  
**Related App:** `chatbot`  
**Status:** Todo

---

## 1. Context

This backend already has a working chatbot flow that currently returns a normal JSON response over HTTP.

The current flow is roughly:

1. validate request data
2. get or create conversation
3. save the user message
4. build conversation history
5. run RAG retrieval
6. call the LLM
7. save the assistant message
8. return JSON with:
   - `conversation_id`
   - `answer`
   - `citations`
   - `items`

The current `ChatService` already acts as an orchestrator:
- it builds retrieval context first
- then calls the LLM
- then returns `answer`, `citations`, and `items` 

The backend architecture rules also require:
- keep logic inside the owning app
- avoid unnecessary rewrites
- run verification commands before task completion
- update deployment-related files if deployment behavior changes 

This task must follow those rules.

---

## 2. Goal

Convert the current chatbot endpoint from a standard one-shot HTTP JSON response into a **streaming response** so the client can display the assistant reply progressively.

The target behavior is:

- the client sends one request
- the backend starts responding immediately
- the assistant answer is streamed token-by-token or chunk-by-chunk
- citations/items/final metadata are still preserved
- conversation and message persistence still works correctly
- the existing architecture remains clean and app-owned

---

## 3. Important Constraints

### 3.1 Do not rewrite the chatbot feature from scratch
This is an incremental enhancement of the existing `chatbot` app.

### 3.2 Keep app ownership inside `chatbot`
Do not move chatbot logic into generic `utils` or unrelated shared modules.

### 3.3 Preserve the existing non-stream endpoint if possible
For backward compatibility, keep the current non-stream response path working unless explicitly told to replace it.

Recommended approach:

- keep existing endpoint:
  - `POST /api/chatbot/chat/`
- add new streaming endpoint:
  - `POST /api/chatbot/chat/stream/`

### 3.4 Streaming must work with the existing RAG flow
The current `ChatService` already does:
- retrieval first
- LLM generation second
- item extraction
- return final result object 

The streaming version must preserve that business meaning.

### 3.5 Do not write to the database on every token
Streaming should not create excessive database writes.

Recommended approach:
- save user message once
- create assistant placeholder message with `PENDING`
- accumulate streamed text in memory
- update the assistant message once on success
- update it once on failure if needed

---

## 4. Recommended Streaming Strategy

Use **HTTP streaming** from Django, not WebSocket, for this task.

Recommended implementation:

- `StreamingHttpResponse`
- content type: `text/event-stream`
- client consumption via `fetch()` + `ReadableStream`
- do **not** rely on browser `EventSource` because the request body needs `POST`

This means the endpoint can still receive:

```json
{
  "message": "Có món chay không?",
  "conversation_id": 42
}
```

and stream back incremental events.

---

## 5. Response Protocol

Use a structured event stream format.

Recommended event types:

### `meta`
Sent once after retrieval/context preparation succeeds.

Contains:
- `conversation_id`
- `citations`
- `items`

### `delta`
Sent many times during generation.

Contains:
- `token` or `text`

### `done`
Sent once after the final answer is fully generated and persisted.

Contains:
- `conversation_id`
- maybe final message metadata if needed

### `error`
Sent if generation fails after the request has started streaming.

Contains:
- user-safe error message

---

## 6. Recommended Event Payload Format

Use SSE-style frames like this:

```text
event: meta
data: {"conversation_id": 42, "citations": [...], "items": [...]}

event: delta
data: {"text": "Dạ "}

event: delta
data: {"text": "có "}

event: delta
data: {"text": "ạ..."}

event: done
data: {"conversation_id": 42}
```

All event payloads should be valid JSON strings.

---

## 7. Required Implementation Steps

### Step 1 — Keep the existing request validation flow
Reuse the existing `ChatMessageSerializer`.

Requirements:
- validate `message`
- validate optional `conversation_id`
- return `400` before streaming starts if input is invalid

Do not start streaming before validation succeeds.

---

### Step 2 — Reuse the current conversation flow
Before starting generation:

- get or create the conversation
- save the user message
- build the history

This should remain semantically equivalent to the current endpoint behavior.

---

### Step 3 — Create a pending assistant message before generation
Before token streaming begins:

- create an assistant `Message`
- set:
  - `role = ASSISTANT`
  - `status = PENDING`
  - `content = ""`
- keep the same conversation and sequence logic

This gives the database a stable placeholder for the in-progress reply.

---

### Step 4 — Perform retrieval once before LLM streaming
The current `ChatService` first retrieves context and citations, then calls the LLM. 

The streaming flow should keep that order:

1. build retrieval context
2. compute citations
3. compute dish/item metadata
4. emit one `meta` event
5. then start LLM streaming

Do not re-run retrieval on every token.

---

### Step 5 — Add LLM streaming support
Refactor the LLM integration so that the NVIDIA API can stream output progressively.

Recommended change:

- keep existing method:
  - `generate(...)`
- add new method:
  - `generate_stream(...)`

`generate_stream(...)` should yield partial text chunks or tokens progressively.

Do not remove the existing `generate(...)` method unless explicitly required.

---

### Step 6 — Add ChatService streaming support
Refactor the chatbot orchestration layer incrementally.

Recommended change:

- keep existing method:
  - `reply(...)`
- add new method:
  - `reply_stream(...)`

`reply_stream(...)` should:

1. validate non-empty message
2. build retrieval context
3. prepare `citations`
4. prepare `items`
5. yield one initial metadata object
6. stream LLM deltas progressively
7. return or expose the final accumulated answer

Recommended pattern:
- either yield structured event dictionaries
- or yield already-formatted SSE strings from the view layer

Prefer keeping `ChatService` focused on orchestration, not HTTP formatting.

---

### Step 7 — Implement the streaming view
Create a new endpoint such as:

- `POST /api/chatbot/chat/stream/`

Recommended behavior:

1. validate serializer
2. get/create conversation
3. save user message
4. create pending assistant message
5. build history
6. create a generator function
7. return `StreamingHttpResponse(generator(), content_type="text/event-stream")`

Inside the generator:

- call the streaming chat service
- emit `meta`
- emit `delta` events progressively
- accumulate final answer text
- on success:
  - update assistant message content
  - set status to `SUCCESS`
  - emit `done`
- on error:
  - update assistant message with safe fallback content
  - set status to `ERROR`
  - save `error_message`
  - emit `error`

---

### Step 8 — Handle persistence safely
Persistence rules:

#### User message
- save once before generation starts

#### Assistant placeholder
- create once with `PENDING`

#### During token stream
- do **not** save each token into the database

#### On successful completion
- update the existing assistant message:
  - `content = full_answer`
  - `status = SUCCESS`

#### On failure
- update the existing assistant message:
  - `content = fallback error text`
  - `status = ERROR`
  - `error_message = actual exception string`

This avoids DB write amplification and preserves the conversation timeline.

---

### Step 9 — Preserve final metadata
Even though text is streamed progressively, the final business response must still preserve:

- `conversation_id`
- `citations`
- `items`

These can be sent via:
- initial `meta` event
- or `meta` + `done` combination

Do not drop citations/items just because the answer is streamed.

---

### Step 10 — Keep frontend compatibility in mind
Document clearly that the frontend should consume the new endpoint with:

- `fetch()`
- stream reader
- incremental text decoding

Do not assume Axios standard JSON mode is sufficient for progressive rendering.

---

## 8. Suggested Code Structure

Keep ownership inside the `chatbot` app.

Recommended structure:

```txt
chatbot/
├── views.py or views/
├── serializers.py or serializers/
├── models.py
├── urls.py
└── rag/
    ├── chat.py
    ├── llm.py
    ├── retrieval.py
    └── ...
```

Possible additions:

- streaming helper inside `chatbot/rag/`
- service helper inside `chatbot/`
- SSE formatter helper if useful

Do not move this logic into generic global helpers unless truly shared.

---

## 9. Non-Goals

This task does **not** require:

- WebSocket migration
- rewriting the whole chatbot module
- changing the database schema unless truly necessary
- changing unrelated DRF endpoints
- redesigning RAG retrieval logic
- rebuilding the existing conversation model

---

## 10. Error Handling Requirements

The streaming implementation must handle these cases:

### Validation failure
- return normal `400` JSON before stream starts

### Retrieval failure
- if failure happens before stream starts, return normal JSON error or start stream with error event only if already committed

### LLM/NVIDIA API failure during stream
- log exception
- update assistant message to `ERROR`
- emit safe `error` event
- finish stream cleanly

### Empty answer
- still complete the request gracefully
- do not leave assistant message in `PENDING`

### Client disconnect
- handle interruption gracefully if possible
- avoid leaving DB records inconsistent

---

## 11. Backward Compatibility Requirements

- Keep the current non-stream endpoint working.
- Do not break existing clients using the current JSON response path.
- The new streaming endpoint should be additive unless explicitly requested otherwise.

---

## 12. Verification Requirements

Before marking the task complete, run the required backend checks.

### Django system check

```bash
python manage.py check
```

### Migration consistency check

```bash
python manage.py makemigrations --check --dry-run
```

### Run migrations if model/schema changed

```bash
python manage.py migrate
```

### Local boot verification

```bash
python manage.py runserver
```

### ASGI startup verification

```bash
uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port 10000
```

### Manual stream verification
Also verify the new stream endpoint manually using:

- browser client with `fetch`
- or `curl`
- or a small local test script

Example manual expectation:
- response begins quickly
- text arrives progressively
- assistant message status becomes `SUCCESS` after completion
- citations/items are available
- errors produce `ERROR` status correctly

The backend rules require verification before considering a task complete. 

---

## 13. Deployment Rules

If this task changes any of the following:

- startup behavior
- required environment variables
- ASGI behavior
- deployment command assumptions
- static or translation flow

then update:

- `build.sh`
- `.env.example` if needed
- README / deployment documentation if needed

Do not leave deployment-related files outdated. 

---

## 14. Definition of Done

This task is done only when:

- a streaming chat endpoint exists and works
- the existing non-stream endpoint still works unless intentionally replaced
- the chatbot logic remains inside the `chatbot` app
- the RAG flow still works correctly
- the streamed answer is progressive
- citations and items are preserved
- user and assistant messages are persisted correctly
- assistant placeholder messages do not remain stuck in `PENDING`
- error cases update message status correctly
- verification commands pass
- deployment files are updated if required

---

## 15. Expected Output

The final implementation should provide:

1. a new streaming endpoint for chat
2. LLM streaming support for the NVIDIA API
3. streaming orchestration at the chatbot service layer
4. correct DB persistence for `Conversation` and `Message`
5. preserved `citations` and `items`
6. backward compatibility for existing non-stream clients
7. verified Django/ASGI runtime behavior

---

## 16. Notes for Implementation

- Do not rewrite the whole chatbot feature.
- Prefer additive changes over destructive refactors.
- Keep HTTP formatting in the view layer where reasonable.
- Keep orchestration in `ChatService`.
- Keep NVIDIA-specific streaming integration in the LLM layer.
- Do not store partial token chunks row-by-row in the database.
- Preserve conversation integrity at all times.
- If a helper is only useful for chatbot streaming, keep it inside the chatbot app.