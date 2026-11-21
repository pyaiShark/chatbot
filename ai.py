from notopenai import NotOpenAI
from os import environ
from datetime import datetime
# Paste your Code in Place key between the quotes.
# Treat it like a password: don't share this file.
API_KEY = environ.get("API_KEY")
# print(API_KEY)


def logger(data, filename, type="usage"):
    # Logs the transactions with details
    with open(filename, 'a') as file:
        if type == "usage":
            file.write(f"--> {datetime.now()} >>> Response ID = {data.id}\t\n Input_token= {data.usage.input_tokens} | Output_token= {data.usage.output_tokens} | Total_token= {data.usage.total_tokens}\n\n")
        else:
            file.write(f"\n\n>>{datetime.now()}>>\n {data}")


# Milestone 1: create the client and write call_gpt below.
def call_gpt(input: str):
    if not API_KEY:
        return
    client = NotOpenAI(api_key=API_KEY)
    response = client.responses.create(model="gpt-5-nano", input=input)
    if response.status == "completed":
        logger(response, "usage_logger.txt")  # This line is just for logging the amount of token usages per function call nothing else
        return response.output_text
    return None


#print(call_gpt("write 'hello'"))