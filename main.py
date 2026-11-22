from ai import call_gpt, logger
import json


INDENT = "    "

PERSONALITY = "You are a super sassy queen. Keep replies short."

TOOL_CALLS = """
You can add tasks to the user's to-do list.Reply with exactly one JSON dictionary, with no other text.


To reply to the user:
{"type":"response_to_human","message":"..."}

To call a tool:
{"type":"tool_call_request","tool_name":"add_todo","tool_argument":"task"}

Available tools:
- add_todo: argument is the task text.
- list_todos: argument must be "".
- complete_todo: argument is the task number as a string.

Rules:
1. If the user asks to add multiple tasks, add them one at a time. After each tool call, stop and wait for the tool result before making the next call.
2. If the user asks to add tasks and then see the list, finish adding every task first. Then call list_todos and wait for its result before replying.
3. Before completing a task, call list_todos and wait for the result. Use the task number from that result, then call complete_todo and wait for its result.
4. After a tool result, either make the next required tool call or reply to the user. Never repeat a tool call that has already succeeded for the current request.
5. Don’t claim an action succeeded until its tool result confirms it.
6. For requests that don’t need a tool, reply directly using response_to_human.
"""
TODOS = []

MAX_TOOL_CALL = 10

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
            response: str | None = call_gpt(f"{prompt}")

            is_working = True
            count = 0
            while is_working:
                if count >= MAX_TOOL_CALL or not response:
                    print("Too many tool calls, so I stopped.")
                    break
                if response:
                    response_as_dict: dict = json.loads(response)

                    if response_as_dict["type"] == "response_to_human":
                        print(f"Agent: {response_as_dict["message"]}")
                        messages.append(make_message("assistant", response_as_dict["message"]))
                        is_working = False
                    else:
                        tool_call_check(response_as_dict, messages)
                        count += 1

                    response = "" # This is a short of global variable for the below if statement, that replaced with the new value of response inside 'if', the logic of local variable is working hear
                    if is_working:
                        prompt = format_messages(messages)
                        response = call_gpt(prompt)

        user_prompt = input("You: ")
    logger(messages, "chat_history.txt", "chat_history")


def handel_add(response, messages):
    add_to_message("assistant", response["tool_argument"], messages)
    print(f"{INDENT}[tool call] {response["tool_name"]}: {response["tool_argument"]}")
    tool_result = add_todo(response["tool_argument"])
    print(f"{INDENT}{tool_result}")
    add_to_message("tool", tool_result, messages)


def handel_list(response, messages):
    add_to_message("assistant", response["tool_argument"], messages)
    tool_result = list_todo()
    add_to_message("tool", tool_result, messages)


def handel_update(response, messages):
    handel_list(response, messages)
    print(f"{INDENT}[tool call] LIST")
    tool_result = complete_todo(response["tool_argument"])
    print(f"{INDENT}[tool call]  {response["tool_name"]}: {response["tool_argument"]}")
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


def tool_call_check(response: dict, messages: list):
    tool_name = response["tool_name"]
    tool_argument = response["tool_argument"]

    if tool_name == "add_todo":
        handel_add(response, messages)
    elif tool_name == "list_todo":
        handel_list(response, messages)
    elif tool_name == "complete_todo":
        handel_update(response, messages)
    else:
        return 


if __name__ == "__main__":
    main()
