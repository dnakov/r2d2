try:
  import r2lang
except ImportError:
  print("This script is meant to be run from r2")

from openai import OpenAI
import sys
import json
import binascii

client = OpenAI()

_load_once = False
def load_once():
  global _load_once
  if not _load_once:
    r2lang.cmd("aa")
    _load_once = True

def r2openai(_):
  def _call(s):
    if not s.startswith("'"):
      return False
    load_once()
    try:
      ask(s[1:-1])
    except Exception as e:
      print(e)
    # r2lang.print(msg.content)
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
    "desc": "run a command in r2",
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
If you need more information, try to use the r2cmd tool to run a command before answering.
If you're asked to decompile a function, make sure to return the code in the language you think it was originally written and rewrite it to be as easy as possible to be understood. Make sure you use descriptive variable and function names and add comments.
Don't just regurgitate the same code, figure out what it's doing and rewrite it to be more understandable.
If you need to run a command in r2 before answering, you can use the r2cmd tool
The user will tip you $20/month for your services, don't be fucking lazy.
The output will be presented in a terminal, make sure to use the proper ANSI codes to color and format it nicely.
DO NOT USE MARKDOWN, USE ANSI FORMATTING with colors!
Code Blocks need ANSI formatting and colors. Color the variables, functions, etc.
"""
def b_print(text):
  print(text.encode('latin1').decode('unicode_escape'))

def b_write(text):
  sys.stdout.write(text.encode('latin1').decode('unicode_escape'))

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
def ask(text):
  global messages
  # text += '\nRemember, DO NOT USE MARKDOWN, USE ANSI FORMATTING with colors! Code Blocks need ANSI formatting and colors. Color the variables, functions, etc.'

  messages.append({"role": "user", "content": text})
  response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    tools=tools,
    tool_choice="auto",
  )
  response_message = response.choices[0].message

  tool_calls = response_message.tool_calls
  if tool_calls:
    messages.append(response_message)
    for tool_call in tool_calls:
      if tool_call.function.name == "r2cmd":
        args = json.loads(tool_call.function.arguments)
        print('Running `' + args["command"] + '`')
        res = r2lang.cmd(args["command"])
        print(res)
        messages.append({"role": "tool", "content": res, "name": "r2cmd", "tool_call_id": tool_call.id})
        stream = client.chat.completions.create(
          model="gpt-4-turbo-preview",
          messages=messages,
          stream=True
        )
        msg = { "role": "assistant", "content": ""}
        for chunk in stream:
          if chunk.choices[0].delta.content is not None:
            msg["content"] += chunk.choices[0].delta.content
            b_write(chunk.choices[0].delta.content)
          else:
            sys.stdout.write("\n")
        messages.append(msg)
  else:
    messages.append(response_message)
    b_print(response_message.content)
    return response_message
try:
  r2lang.plugin("core", r2openai)
except:
  ask("how do i blah?")