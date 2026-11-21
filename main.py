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

MAX_TOOL_CALL = 5

def main():
    messages = [make_message("system", PERSONALITY + '\n\n'+ "tools" + TOOL_CALLS)]
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
            is_working = True
            count = 0
            while is_working:
                if count >= MAX_TOOL_CALL:
                        print("Too many tool calls, so I stopped.")
                        break
                if response and response.startswith("ADD: "):
                    count += 1
                    messages.append(make_message("assistant", response))
                    print(f"{INDENT}[tool call] {response}")
                    tool_result = add_todo(response[5:])
                    print(f"{INDENT}{tool_result}")
                    messages.append(make_message("tool", tool_result))
                elif response == "LIST":
                    count += 1
                    messages.append(make_message("assistant", response))
                    tool_result = list_todo()
                    messages.append(make_message("tool", tool_result))
                else:
                    messages.append(make_message("assistant", response))
                    print(f"Agent: {response}")
                    is_working = False

                response = "" # This is a short of global variable for the below if statement, that replaced with the new value of response inside 'if', the logic of local variable is working hear
                if is_working:
                    prompt = format_messages(messages)
                    response = call_gpt(prompt)
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
            result += "tool_result: " + msg["content"] + '\n'
        else:
            result += "Instructions: " + msg["content"] + "\n"
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
    result = ""
    for todo in TODOS:
        result += f"{todo} "
    return result


if __name__ == "__main__":
    main()
