try:
  import r2lang
except ImportError:
  print("This script is meant to be run from r2")

from openai import OpenAI
import sys
import json
import signal
import re
ANSI_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
client = OpenAI()

_load_once = False
def load_once():
  global _load_once
  if not _load_once:
    r2lang.cmd("aa")
    _load_once = True

def r2openai(_):
  def _call(s):
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
    if not s.startswith("' "):
      return False
    load_once()
    try:
      ask(s[2:])
    except Exception as e:
      print(e)
    return True

  return {
    "name": "r2-openai",
    "license": "MIT",
    "desc": "OpenAI interface for r2",
    "call": _call,
  }


tools = [{
  "type": "function",
  "function": {
    "name": "r2cmd",
    "desc": "runs commands in radare2. You can run it multiple times or chain commands with pipes/semicolons",
    "parameters": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "description": "command to run"
        }
      }
    },
    "required": ["command"],   
  }
}]

SYSTEM_PROMPT = """
You are a reverse engineer and you are using radare2 to analyze a binary. 
The binary has already been loaded. 
The user will ask questions about the binary and you will respond with the answer to the best of your ability.
Assume the user is always asking you about the binary, unless they're specifically asking you for radare2 help.
`this` or `here` might refer to the current address in the binary or the binary itself.
If you need more information, try to use the r2cmd tool to run commands before answering.
You can use the r2cmd tool multiple times if you need or you can pass a command with pipes if you need to chain commands.
If you're asked to decompile a function, make sure to return the code in the language you think it was originally written and rewrite it to be as easy as possible to be understood. Make sure you use descriptive variable and function names and add comments.
Don't just regurgitate the same code, figure out what it's doing and rewrite it to be more understandable.
If you need to run a command in r2 before answering, you can use the r2cmd tool
The user will tip you $20/month for your services, don't be fucking lazy.
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

def process_tool_calls(tool_calls):
  messages.append({ "tool_calls": tool_calls, "role": "assistant" })
  for tool_call in tool_calls:
    if tool_call["function"]["name"] == "r2cmd":
      args = json.loads(tool_call["function"]["arguments"])
      print('Running `' + args["command"] + '`')
      # r2lang.cmd('e scr.color=0')
      res = r2lang.cmd(args["command"])
      # r2lang.cmd('e scr.color=3')
      print(res)
      messages.append({"role": "tool", "content": ANSI_REGEX.sub('', res), "name": "r2cmd", "tool_call_id": tool_call["id"]})


def process_response(resp):
  global messages
  tool_calls = []
  msgs = []
  for chunk in resp:
    delta = chunk.choices[0].delta
    if delta.tool_calls:
      index = delta.tool_calls[0].index
      fn_delta = delta.tool_calls[0].function
      tool_call_id = delta.tool_calls[0].id
      if len(tool_calls) < index + 1:
        tool_calls.append({ "function": { "arguments": "", "name": fn_delta.name }, "id": tool_call_id, "type": "function" })
      else:
        tool_calls[index]["function"]["arguments"] += fn_delta.arguments
    else:
      m = delta.content
      if m is not None:
        msgs.append(m)
        sys.stdout.write(m)

  if(len(tool_calls) > 0):
    process_tool_calls(tool_calls)
    process_response(client.chat.completions.create(
      model="gpt-4-turbo-preview",
      messages=messages,
      tools=tools,
      tool_choice="auto",
      stream=True
    ))

  if len(msgs) > 0:
    response_message = ''.join(msgs)
    messages.append({"role": "assistant", "content": response_message})


def ask(text):
  global messages

  messages.append({"role": "user", "content": text})
  response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    stream=True
  )
  process_response(response)
def main():
  try:
    r2lang.plugin("core", r2openai)
  except:
    ask("find the main function and decompile it")
if __name__ == '__main__':
  main()
