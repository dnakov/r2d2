# r2d2
GPT-4 plugin for radare2

## Introduction
This is a radare2 plugin that uses GPT-4 to generate comments for functions. It uses the `openai` python package to interact with the GPT-4 API.


https://github.com/dnakov/r2d2/assets/3777433/5bcc8e20-dda0-48ac-94e5-e0c8c44a0912


## Installation
`pip install -r requirements.txt`

Install radare2 and rlang-python:
```
brew install radare2
r2pm -i rlang-python
```

## Usage
```
r2 -i r2d2.py <binary>
```
