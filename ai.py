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
    with open(filename, 'a') as file:
        if type == "usage":
            file.write(f"--> {datetime.now()} >>> Response ID = {data.id}\t\n Input_token= {data.usage.input_tokens} | Output_token= {data.usage.output_tokens} | Total_token= {data.usage.total_tokens}\n\n")
        else:
            file.write(f"\n\n>>{datetime.now()}>>\n {data}")


def call_gpt(input: str):
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
        logger(response, "usage_logger.txt")  # This line is just for logging the amount of token usages per function call nothing else
        return response.output_text
    return None


#print(call_gpt("write 'hello'"))