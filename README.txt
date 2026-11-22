# Sassy AI Agent 👑

A personality-packed command-line AI agent built for Stanford Code in Place. It chats with you, manages an in-memory to-do list, saves conversation history, and tracks Groq API token usage.

## ✨ Features

- Sassy, personality-driven chat
- To-do actions: `ADD`, `LIST`, and `DONE`
- Chat-history and token-usage logging
- API key configuration through `.env` or an environment variable
- `/help` for commands and `/reset` to clear the conversation and to-do list

## 🧰 Tech Stack

- Python 3.10+
- OpenAI Python SDK
- Groq’s OpenAI-compatible API
- `openai/gpt-oss-120b` model

## 🚀 Installation

Open the project folder in a terminal, then create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 🔑 Configure Your Groq API Key

1. Create an API key in the Groq Console.
2. Copy `.env.example` to `.env`.
3. Replace the placeholder with your key:

```env
API_KEY=your_actual_groq_api_key
```

Copy the example file with:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Alternatively, set the key in your current terminal session instead of using `.env`:

```powershell
# Windows PowerShell
$env:API_KEY="your_actual_groq_api_key"
```

```bash
# macOS / Linux
export API_KEY="your_actual_groq_api_key"
```

**Keep your API key secret.** Don’t commit `.env` or share a real key. If it’s exposed, revoke it and create a replacement.

## ▶️ Run the Agent

```bash
python main.py
```

Press **Enter** on an empty line to quit. Chat history is appended to `chat_history.txt` when the session ends.

## 💬 Chat Commands

| Command | What it does |
|---|---|
| `/help` | Shows available commands |
| `/reset` | Clears the conversation and to-do list |
| `todos` | Prints the current to-do list |
| `peek` | Prints the internal message history |

Example:

```text
You: Remind me to buy milk and walk the dog
[tool call] ADD: buy milk
[tool call] ADD: walk the dog

You: todos
```

## 📁 Project Files

| File | Purpose |
|---|---|
| `main.py` | Command-line loop and to-do tool handlers |
| `ai.py` | Groq/OpenAI client and usage logger |
| `.env.example` | Safe API-key template |
| `chat_history.txt` | Conversation log written when you quit |
| `usage_logger.txt` | Token usage recorded for API responses |
| `requirements.txt` | Python dependencies |

## 🛠 Troubleshooting

**No API key found**  
Create `.env` or set `API_KEY` in your terminal. If you use `.env`, make sure the app loads it.

**Authentication error**  
Check that the key in `.env` is correct and active in the Groq Console.

**Module not found**  
Activate the virtual environment, then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

**Network or timeout error**  
Check your internet connection and try again.

## 📚 Handout

[Stanford Code in Place: Build an Agent](https://codeinplace.stanford.edu/cipx/build-an-agent)

**What changed:** I organized the README into scannable sections, converted commands and configuration into fenced code blocks with language labels, and used tables for the command and file reference. I also clarified that setting an environment variable is an alternative to `.env`, and added a reminder that the app needs to load `.env` for that method to work.