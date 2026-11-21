from ai import call_gpt, logger


INDENT = "    "

PERSONALITY = "You are a super sassy queen. Keep replies short."

TOOL_CALLS = """You can add tasks to the user's to-do list. When the user want to add one, replay with exactly this add nothing else:
ADD: <the task>
For anything else, just talk normally.
To see the user's list, reply with exactly: LIST
Add one task per command: if the user lists several tasks, send ADD once for each.
Send one command at a time, then stop. You will be shown the result and can reply again.
Do not repeat a command you have already sent for the same request
"""
TODOS = []


def main():
    messages = [make_message("system", PERSONALITY + '\n' + TOOL_CALLS)]
    print("Chat with the bot! (press Enter to quit)")
    user_prompt = input("You: ")
    while user_prompt:
        if user_prompt == "peek":
            peek(messages)
        if user_prompt == "todos":
            print(TODOS)
        else:
            messages.append(make_message("user", user_prompt))
            prompt = format_messages(messages)
            response = call_gpt(f"{prompt}")
            if response:
                if response[:5] == "ADD: ":
                    print(f"{INDENT}[tool call] ADD: {response[5:]}")
                    print(f"{INDENT}{add_todo(response[5:])}")
                    messages.append(make_message("tool", "Added: "+response))
                elif response[:4] == "LIST":
                    todos = list_todo()
                    messages.append(make_message("tool", "Tool result: "+response))
                else:
                    messages.append(make_message("assistant", response))
                    print(f"Agent: {response}")
        user_prompt = input("You: ")
    logger(messages, "chat_history.txt", "chat_history")


def make_message(role, content):
    return {"role": role, "content": content}


def peek(msgs):
    print(f"{INDENT}The record has {len(msgs)} messages: ")
    for msg in msgs:
        print(f"{INDENT}{msg["role"]}: {msg["content"]}")


def format_messages(msgs):
    result = ""
    for msg in msgs:
        if msg["role"] == "user":
            result += "User: " + msg["content"] + '\n'
        elif msg["role"] == "assistant":
            result += "Assistant: " + msg["content"] + '\n'
        elif msg["role"] == "tool":
            result += "tool: " + msg["content"] + '\n'
        else:
            result += "Instructions: " + msg["content"] + "\n\n"
    result += "Assistant:"
    return result


def add_todo(task):
    if task:
        TODOS.append(task)
        return f"Added: {task}" 
    return "Failed, the 'task' is empty"


def list_todo():
    if not TODOS:
        print("The list is empty.")
    for todo in TODOS:
        print(f"O{INDENT}{todo}")
    return TODOS


if __name__ == "__main__":
    main()
