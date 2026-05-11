import os

# This program demonstrates the use of Google's GenAI API to generate content using the Gemini model.
# It loads the API key from an environment variable, sends a prompt to the model, and prints the generated response. 
# It also supports streaming responses, which allows it to print the output as it
# is generated, rather than waiting for the entire response to be ready.

# We are importing Google's GenAI module, which is a locally installed python library.
# That library is what will connect your application to their genai web api on their servers. 
# It provides higher level function and utilities.
# Documentation:
# https://googleapis.github.io/python-genai/
from google import genai
from google.genai import types

# Helper library to load environment variables from a .env file into the process's environment.
from dotenv import load_dotenv
from PIL import Image
# Load environment variables from .env file
load_dotenv()

# The client gets the API key from the environment variable `GOOGLE_API_KEY`.
api_key = os.getenv("GOOGLE_API_KEY")

# We create a client object that will be used to interact with the GenAI API.
client = genai.Client(api_key=api_key)

grounding_tool = types.Tool(google_search=types.GoogleSearch())
# Stream vs non-streaming response:
STREAM_ON = False

# Gemini Model
MODEL = "gemini-2.5-flash"
# Prompt
PROMPT = "What is the weather like in Paris?"
IMG = Image.open("media/pic.jpg")
CONFIG = {"system_instruction": "You are a medieval knight who speaks in Old English.", "tools": [grounding_tool]}

def main():
  chat = client.chats.create(model=MODEL, config=CONFIG)
  
  # Generate content with the Gemini 3 Flash Preview model.
  if STREAM_ON:
    response = chat.send_message_stream([PROMPT])
    # If streaming is on, we will receive an iterator that yields parts of the response as they are generated.
    for chunk in response:
      print(chunk.text, end='', flush=True)  # flush=True makes it print immediately
  else:
    response = chat.send_message([PROMPT])
    # The response is a Python object that contains the generated content and metadata.
    print(response.text)
  print("///")
  for message in chat.get_history():
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)


if __name__ == "__main__":
  main()