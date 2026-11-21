from notopenai import NotOpenAI
from os import environ
from datetime import datetime
# Paste your Code in Place key between the quotes.
# Treat it like a password: don't share this file.
API_KEY = environ.get("API_KEY")
# print(API_KEY)


def logger(response):
    # Logs the transactions with details
    with open("usage_logger.txt", 'a') as file:
        file.write(f"--> {datetime.now()} >>> Response ID = {response.id}\t\n Input_token= {response.usage.input_tokens} | Output_token= {response.usage.output_tokens} | Total_token= {response.usage.total_tokens}\n\n")


# Milestone 1: create the client and write call_gpt below.
def call_gpt(input: str):    
    client = NotOpenAI(api_key=API_KEY)
    response = client.responses.create(model="gpt-5-nano", input=input)
    if response.status == "completed":
        logger(response)  # This line is just for logging the amount of token usages per function call nothing else
        return response.output_text
    return None
    #print(client.usage())


#print(call_gpt("write 'hello'"))