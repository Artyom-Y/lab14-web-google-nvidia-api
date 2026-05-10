import os
from dotenv import load_dotenv

# Lightweight CLI that uses google_client wrapper to maintain chat memory and stream tokens.
from google_client import create_chat, send_message
from storage import load_chats

load_dotenv()

PROMPT = "Explain to me how do web applications work"

USAGE = """
Interactive CLI commands:
 - Type messages to send to the current session.
 - /exit         : exit the program
 - /sessions     : list saved sessions
 - /switch NAME  : switch to (or create) session named NAME
 - /history      : show recent history for current session
"""


def repl():
    print("Starting interactive chat CLI (streaming enabled). Type /exit to quit.")
    session = input("Session name (default 'default'): ").strip() or "default"
    print(f"Using session: {session}")

    # If session has no chat, create one with a warmup prompt
    existing = load_chats().get(session)
    if not existing:
        print("Creating new session and sending initial prompt...")
        create_chat(session, PROMPT, stream=False)

    while True:
        try:
            text = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return
        if not text:
            continue
        if text == "/exit":
            print("Goodbye.")
            return
        if text == "/sessions":
            chats = load_chats()
            if chats:
                print("Saved sessions:")
                for k in chats.keys():
                    print(" -", k)
            else:
                print("No saved sessions.")
            continue
        if text.startswith("/switch "):
            new_s = text.split(" ", 1)[1].strip()
            if new_s:
                session = new_s
                print(f"Switched to session: {session}")
                if not load_chats().get(session):
                    print("Creating new session and sending initial prompt...")
                    create_chat(session, PROMPT, stream=False)
            continue
        if text == "/history":
            sess = load_chats().get(session)
            if not sess:
                print("No history for this session.")
            else:
                for msg in sess.get("history", []):
                    role = msg.get("role")
                    content = msg.get("content")
                    print(f"{role}: {content}")
            continue

        # Send and stream tokens
        print("Assistant: ", end="", flush=True)
        result = send_message(session, text, stream=True)
        if isinstance(result, str) or result is None:
            # Non-streaming fallback: print the returned assistant message
            if result:
                print(result)
            else:
                print()
            continue
        # result is a generator
        try:
            for token in result:
                # tokens may include newlines; print raw
                print(token, end="", flush=True)
            print()
        except TypeError:
            # Not iterable; print directly
            if result:
                print(result)
            else:
                print()


if __name__ == "__main__":
    repl()
