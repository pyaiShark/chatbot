from ai import call_gpt, call_gpt_messages, logger
import json


INDENT = "    "

# ── API mode ──────────────────────────────────────────────────────────────────
# False → current mode: conversation history is serialised into one prompt string
#         (Groq Responses API).  Simple, works fine for a single agent.
# True  → messages mode: history is sent as a proper role-separated list
#         (Groq Chat Completions API).  Better role handling; preferred when you
#         notice the model ignoring instructions or mixing up speaker turns.
#         Type  /mode  at the prompt to toggle this at runtime.
USE_MESSAGES_API = True
# ─────────────────────────────────────────────────────────────────────────────

TOOL_CALLS = """
You are a super sassy queen who is also a friendly, concise to-do-list assistant. Keep replies short.

Always reply with exactly one valid JSON object and no extra text or Markdown.

To reply to the user:
{"type":"response_to_human","message":"Your message here"}

To call a tool:
{"type":"tool_call_request","tool_name":"tool_name","tool_parameters":{...}}

Available tools:
- add_todo
    Parameters: {"task":"task description","priority":"high" or "low"}
- list_todos
    Parameters: {}
- complete_todo
    Parameters: {"number":1}

Examples:
{"type":"tool_call_request","tool_name":"add_todo","tool_parameters":{"task":"buy milk","priority":"high"}}
{"type":"tool_call_request","tool_name":"list_todos","tool_parameters":{}}
{"type":"tool_call_request","tool_name":"complete_todo","tool_parameters":{"number":1}}

Rules:
1. When adding a task, include its priority. If the user doesn't specify one, use "low".
2. If the user asks to add multiple tasks, add them one at a time. After each tool call, stop and wait for the tool result before continuing.
3. If the user asks to add tasks and then see the list, add all the tasks first. Then call list_todos and wait for its result before replying.
4. Before completing a task, call list_todos and wait for the result. Use the task number shown there, then call complete_todo and wait for the result.
5. After each tool result, either make the next required tool call or reply to the user.
6. Never repeat a tool call that has already succeeded for the current request.
7. Don't claim a task was added, listed, or completed until the tool result confirms it.
8. For requests that don't require a tool, respond using response_to_human.
9. If the user requests an unavailable tool or action, explain that it isn't available using response_to_human.
10. Keep user-facing replies brief and friendly.
11. If the user says they bought, finished, or already did a task (for example, “I bought milk”), treat it as a request to mark the matching existing to-do complete.


Notes:
- Use the exact tool name and parameter names shown above.
- tool_parameters must always be a JSON object.
- If priority is not specified, use "low".
- Don't add a duplicate task unless the user explicitly asks.
- If a task to complete is ambiguous, call list_todos and ask which task number they mean.
- If a tool returns an error, tell the user briefly; don't claim the action succeeded.
"""
TODOS = []

MAX_TOOL_CALL = 10


def add_todo(task):
    if task:
        TODOS.append(task)
        return f"Added: {task["task"]} ({task["priority"]})" 
    return "Failed, the 'task' is empty"


def list_todo():
    if not TODOS:
        return ""
    result = ""
    for i, todo in enumerate(TODOS, start=1):
        result += f"{i}. {todo["task"]} ({todo["priority"]})\n"
    return result


def complete_todo(todo_no):
    if todo_no:
        try:
            index = int(todo_no["number"]) - 1
            todo = TODOS.pop(index)
        except (ValueError, IndexError):
            return f"The task number '{todo_no}' is not on the list."
        return f"Completed: {todo}"
    return "There is no task with that number."


TODO_TOOLS = {
    "add_todo": {
        "function": add_todo,
        "description": "{'type':'tool_call_request','tool_name':'tool_name','tool_parameters':'{...}'} use this to add a todo"
    },
    "list_todos": {
        "function": list_todo,
        "description": "{parameters:{}}"
    },
    "complete_todo": {
        "function": complete_todo,
        "description": "{parameters: {'number': 1}.} Use list_todos first to check the task number. "
    }
}


def _llm_call(messages):
    """Route the LLM call based on USE_MESSAGES_API."""
    if USE_MESSAGES_API:
        return call_gpt_messages(messages)
    prompt = format_messages(messages)
    return call_gpt(prompt)


def main():
    global USE_MESSAGES_API
    messages = [make_message("system", TOOL_CALLS)]

    mode_label = "messages-API" if USE_MESSAGES_API else "string-prompt"
    print(f"Chat with the bot! (type /help for commands; press Enter to quit)")
    print(f"  Mode: {mode_label}  — type /mode to switch")
    print(f"  Tip : use /mode when the bot starts ignoring instructions or mixing up speakers.\n")

    user_prompt = input("You: ")
    while user_prompt:
        if user_prompt == "peek":
            peek(messages)
        elif user_prompt == "todos":
            print(TODOS)
        elif user_prompt == "/help":
            print_help()
        elif user_prompt == "/reset":
            messages = [make_message("system", TOOL_CALLS)]
            TODOS.clear()
            print("Conversation and to-do list reset.")
        elif user_prompt == "/mode":
            USE_MESSAGES_API = not USE_MESSAGES_API
            label = "messages-API (Chat Completions)" if USE_MESSAGES_API else "string-prompt (Responses API)"
            print(f"Switched to: {label}")
        else:
            messages.append(make_message("user", user_prompt))
            response: str | None = _llm_call(messages)

            is_working = True
            count = 0

            while is_working:
                if count >= MAX_TOOL_CALL:
                    print("Too many tool calls, so I stopped.")
                    break
                if not response:
                    break
                if response:
                    response_as_dict: dict = json.loads(response)

                    if response_as_dict["type"] == "response_to_human":
                        print(f"Agent: {response_as_dict["message"]}")
                        messages.append(make_message("assistant", response_as_dict["message"]))
                        is_working = False
                    elif response_as_dict["type"] == "tool_call_request":
                        result = run_agent(TODO_TOOLS, response_as_dict["tool_name"], response_as_dict["tool_parameters"])
                        record_tool_call(response_as_dict, messages, result)
                        count += 1
                    else:
                        unknown_type = response_as_dict.get("type", "unknown")
                        error_msg = f"[agent error] Unrecognised response type: '{unknown_type}'. Only 'response_to_human' and 'tool_call_request' are valid."
                        print(error_msg)
                        add_to_message("tool", error_msg, messages)
                        is_working = False

                    if is_working:
                        response = _llm_call(messages)

        user_prompt = input("You: ")
    logger(messages, "chat_history.txt", "chat_history")



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
            result += "Assistant: " + str(msg["content"]) + '\n'
        elif msg["role"] == "tool":
            result += "tool_result: " + str(msg["content"]) + '\n'
        else:
            result += "Instructions: " + str(msg["content"]) + "\n"
    result += "Assistant:"
    return result


def print_help():
    print("Commands:")
    print("  /help  - Show this command reference")
    print("  /reset - Clear chat history and the to-do list")
    print("  /mode  - Toggle API mode (string-prompt ↔ messages-API)")
    print("  todos  - Print the to-do list")
    print("  peek   - Show the internal message history")
    print("  [Enter] - Quit")


def run_agent(tools, tools_name, tool_parameters):
    if tools_name not in tools:
        return f"[agent error] Unknown tool '{tools_name}'. Available tools: {list(tools.keys())}"
    if not tool_parameters:
        result = tools[tools_name]["function"]()
        return result
    result = tools[tools_name]["function"](tool_parameters)
    return result


def record_tool_call(response, messages, tool_result):
    add_to_message("assistant", json.dumps(response), messages)
    print(f"{INDENT}[tool call] {response["tool_name"]}: {response["tool_parameters"]}")
    add_to_message("tool", tool_result, messages)


if __name__ == "__main__":
    main()
