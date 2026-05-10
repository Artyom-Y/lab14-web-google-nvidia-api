# Plan: Convert `dialog.py` into a Google-chat-capable app

**Goal**
 Authentication will use an API key loaded from a `.env` file via `python-dotenv`.
 Persistence will be a local JSON file storing chat IDs and minimal history.
 CLI is the first UI; responses will stream token-by-token.
**Assumptions**
- We'll keep the app lightweight and Python-based.
 Authentication: use an API key loaded from `.env` via `python-dotenv`. Document required env var: `GOOGLE_API_KEY`
 Chat session model: map a CLI session (or named session) to a `chat_id` returned by `client.chats.create`; persist mapping and recent messages to a local JSON file (e.g., `chats.json`).
- The workspace already contains utilities for Google GenAI in `google-genai.py` (review needed).

 Implement a Google client wrapper module that exposes `create_chat(session_key, first_message, stream=False)`, `send_message(chat_id, message, stream=False)`, and `stream_response(...)` helpers.
 Integrate `client.chats.create` (using model `gemini-3-flash-preview` by default) to start/continue conversations and ensure messages are attached to the correct `chat_id` so memory persists. Enable token streaming when `stream=True`.
**High-Level Steps**
1. Review [dialog.py](dialog.py) to map current flow and identify extension points.
 Add persistence for messages/chat IDs using a local JSON file. Implement a small helper `storage.py` to read/write `chats.json` atomically.
 Provide a CLI interface: an interactive REPL that lets the user pick or name a session, sends messages, and prints streamed tokens as they arrive.
 Use the official Google GenAI client library if available (`google-genai` style wrappers). If not available, implement a minimal HTTP wrapper. Prefer the helper in `google-genai.py` if it abstracts model calls.
 On first message for a session, call `client.chats.create` and store returned `chat.id` in `chats.json` for subsequent messages.
 For message history persistence, store a rolling window of recent messages (e.g., last 100 tokens or messages) in `chats.json` and allow optional pruning.
 Environment variables: `GOOGLE_API_KEY`, `MODEL_NAME` (default `gemini-3-flash-preview`), `CHATS_FILE` (default `chats.json`). Use `python-dotenv` to load `.env`.
4. Implement a Google client wrapper module that exposes a simple `create_chat(session_id, message)` and `append_message(chat_id, message)` API.
 `google_client.py` (wrapper around GenAI client, supports streaming)
 Updated `dialog.py` that uses the wrapper and handles session/chat IDs and streaming CLI
 `storage.py` (local JSON chat store helper)
 `plan.dialog.md` (this file)
 README updates and `requirements.txt` additions (`python-dotenv`, any Google client lib)
**Implementation details / notes**
- Use the official Google GenAI client library if available in this environment (or wrap HTTP requests if not).
- On first message, call `client.chats.create` and store returned `chat.id` for subsequent messages from that user/session.
- For message history persistence, keep both (a) minimal local cache (recent messages) for fast access and (b) durable store (SQLite or file) for longer history and recovery.
- Add a small config file or environment variable layout:  `GOOGLE_AUTH_JSON`, `APP_MODE` (cli|web), `STORAGE_BACKEND`.

**Deliverables**
- `google_client.py` (wrapper around GenAI client)
- Updated `dialog.py` that uses the wrapper and handles session/chat IDs
- `plan.dialog.md` (this file)
- README updates and `requirements.txt` additions
- Minimal tests for chat flow

**Risks & considerations**
**Next immediate steps**
1. Inspect `dialog.py` and `google-genai.py` to identify how to reuse existing helpers.
2. Add `google_client.py` and `storage.py` skeletons and update `requirements.txt` to include `python-dotenv` and any missing Google client.
3. Implement a CLI REPL in `dialog.py` that loads `.env`, picks/creates a session, and streams responses.

If this looks good, I'll start by reviewing `dialog.py` and `google-genai.py` and then scaffold the wrapper and storage helper.
- Auth flow complexity (OAuth for user-level vs. service account for server-to-server).
- Cost and rate limits when calling Google APIs — add optional rate / cost monitoring hooks.
- Conversation history size: consider pruning, summarization, or windowing.

**Questions / Clarifications**
1. Which authentication method do you prefer: Service Account (server-only), OAuth user consent, or an API key? (Recommend Service Account for server apps.)
2. What UI do you want first: simple CLI, or a small web UI (FastAPI/Flask) for interactive use? (I can scaffold both, start with CLI.)
3. How should conversation memory be persisted initially: in-memory only, JSON file, or SQLite database? (Recommend SQLite for persistence without external deps.)
4. Do you have a preferred Google model or GenAI product (e.g., a specific model name or using the `google-genai` helper in repo)?
5. Any constraints on deployment (local only, Docker, cloud run) or budgeting for API calls?
6. Do you want message streaming (incremental responses) or full-response behavior?

---

Next steps: I'll review [dialog.py](dialog.py) and `google-genai.py` to propose concrete code changes and an implementation checklist once you answer the questions above.
