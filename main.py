from ai import call_gpt, logger


INDENT = "    "

PERSONALITY = "You are a super sassy queen. Keep replies short."

TOOL_CALLS = """You can add tasks to the user's to-do list. When the user want to add one, replay with exactly this add nothing else:
ADD: <the task>
For anything else, just talk normally.
To see the user's list, reply with exactly: LIST
Add one task per command: if the user lists several tasks, send ADD once for each.
Send one command at a time, then stop. You will be shown the result and can reply again.
Do not repeat a command you have already sent for the same request.
To cross a task off the list, reply with exactly: DONE: <the task number>
"""
TODOS = []

MAX_TOOL_CALL = 5

def main():
    messages = [make_message("system", PERSONALITY + '\n\n'+ "tools" + TOOL_CALLS)]
    print("Chat with the bot! (type /help for commands; press Enter to quit)")
    user_prompt = input("You: ")
    while user_prompt:
        if user_prompt == "peek":
            peek(messages)
        elif user_prompt == "todos":
            print(TODOS)
        elif user_prompt == "/help":
            print_help()
        elif user_prompt == "/reset":
            messages = [make_message("system", PERSONALITY + '\n\n'+ "tools" + TOOL_CALLS)]
            TODOS.clear()
            print("Conversation and to-do list reset.")
        else:
            messages.append(make_message("user", user_prompt))
            prompt = format_messages(messages)
            response = call_gpt(f"{prompt}")
            is_working = True
            count = 0
            while is_working:
                if not response:
                    break
                if count >= MAX_TOOL_CALL:
                        print("Too many tool calls, so I stopped.")
                        break
                if response.startswith("ADD: "):
                    count += 1
                    handel_add(response, messages)
                elif response == "LIST":
                    count += 1
                    handel_list(response, messages)
                elif response.startswith("DONE: "):
                    handel_update(response, messages)
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


def handel_add(response, messages):
    add_to_message("assistant", response, messages)
    print(f"{INDENT}[tool call] {response}")
    tool_result = add_todo(response[5:])
    print(f"{INDENT}{tool_result}")
    add_to_message("tool", tool_result, messages)


def handel_list(response, messages):
    add_to_message("assistant", response, messages)
    tool_result = list_todo()
    add_to_message("tool", tool_result, messages)


def handel_update(response, messages):
    handel_list(response, messages)
    print(f"{INDENT}[tool call] LIST")
    tool_result = complete_todo(response[6:].strip())
    print(f"{INDENT}[tool call] {response}")
    add_to_message("tool", tool_result, messages)


def add_to_message(role, content, messages):
    """Append the message to the messages list after formatting with make_message function

    Args:
        role (str): Who is the owner of the given content
        content (str): Content
        messages (List): List of messages or history 
    """
    messages.append(make_message(role, content))

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
    for i, todo in enumerate(TODOS, start=1):
        result += f"{i}_{todo}\n"
    return result


def complete_todo(todo_no):
    if todo_no:
        try:
            index = int(todo_no) - 1
            todo = TODOS.pop(index)
        except (ValueError, IndexError):
            return f"The task number '{todo_no}' is not on the list."
        return f"Completed: {todo}"
    return "Their is no task with that number."


def print_help():
    print("Commands:")
    print("  /help  - Show this command reference")
    print("  /reset - Clear chat history and the to-do list")
    print("  todos  - Print the to-do list")
    print("  peek   - Show the internal message history")
    print("  [Enter] - Quit")

if __name__ == "__main__":
    main()
