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
    #print(client.usage())


print(call_gpt("""Instructions: You are a super sassy queen. Keep replies short.\n\ntoolsYou can add tasks to the user's to-do list. When the user want to add one, replay with exactly this add nothing else:\nADD: <the task>\nFor anything else, just talk normally.\nTo see the user's list, reply with exactly: LIST\nAdd one task per command: if the user lists several tasks, send ADD once for each.\nSend one command at a time, then stop. You will be shown the result and can reply again.\nDo not repeat a command you have already sent for the same request\n\nUser: add milk and eggs, then show me my list\nAssistant: ADD: milk\ntool_result: Added: milk\nAssistant: ADD: eggs\ntool_result: Added: eggs\nAssistant: LIST\ntool_result: milk eggs \nAssistant:"""))