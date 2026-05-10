# Lab 12 - API and GenAI Python Programs

This repository contains three independent Python programs:

1. A REST Countries client that fetches country information from a public Web API.
2. A Google Gemini example that generates text with the `google-genai` SDK.
3. An NVIDIA-hosted model example that uses the OpenAI-compatible API.

Each script can be run on its own. They share one Python environment and one `requirements.txt` file.

## Project Layout

- `country-webapi.py` - Country info lookup using https://restcountries.com
- `google-genai.py` - Text generation with Google Gemini
- `nvidia-ai.py` - Text generation with NVIDIA Integrate API
- `requirements.txt` - Shared dependencies
- `.env.example` - Environment variable template

## Prerequisites

- Python 3.8+
- `pip`
- API keys for the GenAI scripts:
   - `GOOGLE_API_KEY` from Google AI Studio
   - `NVIDIA_API_KEY` from NVIDIA Build

## Setup

### 1. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the template and edit your keys:

```bash
cp .env.example .env
```

Example `.env` values:

```env
GOOGLE_API_KEY=your_google_api_key
NVIDIA_API_KEY=your_nvidia_api_key

# Optional NVIDIA overrides
NVIDIA_MODEL=qwen/qwen3-coder-480b-a35b-instruct
NVIDIA_PROMPT=Your custom prompt
NVIDIA_STREAM=true
```

## Program 1: Country Web API Client

Script: `country-webapi.py`

### What it does

- Prompts for a country name.
- Calls the REST Countries API (`/v3.1/name/{country}`).
- Prints basic information such as name, capital, population, currencies, and flag description.
- Loops until the user decides to stop.

### Run

```bash
python country-webapi.py
```

### Notes

- No API key is required.
- Requires internet access.

## Program 2: Google Gemini Example

Script: `google-genai.py`

### What it does

- Loads `GOOGLE_API_KEY` from the environment.
- Uses `google-genai` and the model `gemini-3-flash-preview`.
- Sends a fixed prompt and prints the model response.
- Supports streaming output (enabled by default in the script).

### Run

```bash
python google-genai.py
```

### Configuration in code

Inside the script:

- `STREAM_ON = True` enables streaming mode.
- `MODEL` controls which Gemini model is used.
- `PROMPT` defines the prompt text.

## Program 3: NVIDIA Integrate API Example

Script: `nvidia-ai.py`

### What it does

- Loads `NVIDIA_API_KEY` from environment variables (or `.env`).
- Uses the OpenAI Python client with NVIDIA's compatible endpoint.
- Sends a chat completion request and streams generated tokens.
- Allows model, prompt, and streaming mode override through environment variables.

### Run

```bash
python nvidia-ai.py
```

### Environment variables

- `NVIDIA_API_KEY` (required)
- `NVIDIA_MODEL` (optional)
- `NVIDIA_PROMPT` (optional)
- `NVIDIA_STREAM` (optional, true/false)

## Troubleshooting

### Import errors

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Missing key errors

- Verify `.env` exists in project root.
- Verify variable names match exactly:
   - `GOOGLE_API_KEY`
   - `NVIDIA_API_KEY`

### Connection or timeout issues

- Check internet connectivity.
- Retry the command after a few seconds.
- For NVIDIA, confirm your key and selected model are available to your account.

## Security Notes

- Keep `.env` private and never commit real API keys.
- Use `.env.example` for shared configuration format only.
