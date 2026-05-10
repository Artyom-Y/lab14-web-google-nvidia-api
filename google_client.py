import os
import uuid
from typing import Optional, Callable, Iterator
from dotenv import load_dotenv

load_dotenv()

from google import genai
from storage import get_session, set_session

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

client = genai.Client(api_key=API_KEY)


def _has_chats_api() -> bool:
    return hasattr(client, "chats")


def create_chat(session_key: str, first_message: str, stream: bool = False) -> str:
    """Create a new chat for session_key and send the first message.
    Returns chat_id (internal or provider id).
    """
    existing = get_session(session_key)
    if existing:
        return existing.get("chat_id")

    # Prefer provider chat if available
    if _has_chats_api():
        # Attempt to create a provider-side chat and store its id
        resp = client.chats.create(model=MODEL, messages=[{"role": "user", "content": first_message}])
        chat_id = getattr(resp, "id", str(uuid.uuid4()))
        history = [
            {"role": "user", "content": first_message},
            {"role": "assistant", "content": getattr(resp, "text", "")},
        ]
    else:
        # Fallback: synthesize chat by using models.generate_content
        resp = None
        if stream:
            # stream via models.generate_content_stream and concat
            text_parts = []
            for chunk in client.models.generate_content_stream(model=MODEL, contents=first_message):
                text_parts.append(getattr(chunk, "text", ""))
            assistant_text = "".join(text_parts)
        else:
            response = client.models.generate_content(model=MODEL, contents=first_message)
            assistant_text = getattr(response, "text", "")
        chat_id = str(uuid.uuid4())
        history = [{"role": "user", "content": first_message}, {"role": "assistant", "content": assistant_text}]

    session_obj = {"chat_id": chat_id, "history": history}
    set_session(session_key, session_obj)
    return chat_id


def send_message(session_key: str, message: str, stream: bool = False) -> Optional[str]:
    """Send a message in the session identified by session_key.
    If stream=True, yields tokens via callback set in stream_callback by calling stream_response.
    Returns the assistant full text when not streaming.
    """
    session = get_session(session_key)
    if not session:
        # create new chat implicitly
        create_chat(session_key, message, stream=stream)
        # after create_chat, session exists and contains assistant response already; return that if non-stream
        session = get_session(session_key)
        if session and not stream:
            last = session.get("history", [])
            if last and last[-1]["role"] == "assistant":
                return last[-1]["content"]
            return None

    # append user message to history
    history = session.get("history", [])
    history.append({"role": "user", "content": message})

    # If provider-side chats exist, forward only the new message using chat id
    if _has_chats_api():
        # If provider supports continuing a chat by passing chat_id, attempt that pattern
        try:
            # Some SDKs accept `chat=chat_id` or `chat_id` param; try both defensively
            chat_id = session["chat_id"]
            try:
                resp = client.chats.create(model=MODEL, chat=chat_id, messages=[{"role": "user", "content": message}], stream=stream)
            except TypeError:
                # fallback without named parameter
                resp = client.chats.create(model=MODEL, messages=[{"role": "user", "content": message}], chat=chat_id, stream=stream)

            if stream:
                # Streaming: resp is an iterator
                assistant_text = ""
                for chunk in resp:
                    token = getattr(chunk, "text", "")
                    assistant_text += token
                    yield token
                history.append({"role": "assistant", "content": assistant_text})
                session["history"] = history
                set_session(session_key, session)
                return
            else:
                assistant_text = getattr(resp, "text", "")
                history.append({"role": "assistant", "content": assistant_text})
                session["history"] = history
                set_session(session_key, session)
                return assistant_text
        except Exception:
            # fallthrough to local-history approach
            pass

    # Fallback: call models.generate_content with concatenated history
    # Build a prompt by concatenating recent history
    prompt_lines = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content")
        if role == "system":
            prompt_lines.append(f"System: {content}")
        elif role == "user":
            prompt_lines.append(f"User: {content}")
        else:
            prompt_lines.append(f"Assistant: {content}")
    prompt = "\n".join(prompt_lines)

    if stream:
        assistant_text = ""
        for chunk in client.models.generate_content_stream(model=MODEL, contents=prompt):
            token = getattr(chunk, "text", "")
            assistant_text += token
            yield token
        history.append({"role": "assistant", "content": assistant_text})
        session["history"] = history
        set_session(session_key, session)
        return
    else:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        assistant_text = getattr(response, "text", "")
        history.append({"role": "assistant", "content": assistant_text})
        session["history"] = history
        set_session(session_key, session)
        return assistant_text


__all__ = ["create_chat", "send_message"]
