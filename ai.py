from openai import OpenAI
from os import environ
from datetime import datetime
from pathlib import Path


def load_api_key():
    """Load API_KEY from the environment or this project's .env file."""
    api_key = environ.get("API_KEY")
    if api_key:
        return api_key

    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                if name.strip() == "API_KEY":
                    value = value.strip().strip("\"'")
                    if value:
                        environ["API_KEY"] = value
                        return value
    return None


API_KEY = load_api_key()

def logger(data, filename, type="usage"):
    # Logs the transactions with details
    with open(filename, 'a', encoding='utf-8') as file:
        if type == "usage":
            file.write(f"--> {datetime.now()} >>> Response ID = {data.id}\t\n Input_token= {data.usage.input_tokens} | Output_token= {data.usage.output_tokens} | Total_token= {data.usage.total_tokens}\n\n")
        else:
            file.write(f"\n\n>>{datetime.now()}>>\n {data}")


def call_gpt(input: str):
    """Send a single prompt string and return the model's reply.

    Uses the Groq Responses API (client.responses.create).
    Switch to call_gpt_messages() for proper role-separated history.
    """
    if not API_KEY:
        print("Error: API_KEY is not set. Add it to .env or set the environment variable.")
        return
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    response = client.responses.create(
        input=input,
        model="openai/gpt-oss-120b",
        reasoning=None
    )
    if response.status == "completed":
        logger(response, "usage_logger.txt")
        return response.output_text
    return None


def call_gpt_messages(messages: list):
    """Send a role-separated messages list and return the model's reply.

    Uses the Chat Completions API (client.chat.completions.create).
    Each message must be {"role": "system"|"user"|"assistant"|"tool", "content": "..."}.
    Preferred over call_gpt() — the model is trained on role tokens, not text prefixes.
    """
    if not API_KEY:
        print("Error: API_KEY is not set. Add it to .env or set the environment variable.")
        return
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    # Chat Completions only supports system / user / assistant roles.
    # Map our internal "tool" role back to "user" so the API accepts it.
    mapped = []
    for msg in messages:
        role = msg["role"]
        content = str(msg["content"])
        if role == "tool":
            mapped.append({"role": "user", "content": f"[tool_result] {content}"})
        else:
            mapped.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=mapped,
    )
    return response.choices[0].message.content


#print(call_gpt("write 'hello'"))