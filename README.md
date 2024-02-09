# r2d2
GPT-4 plugin for radare2

## Introduction
This is a radare2 plugin that uses GPT-4 to generate comments for functions. It uses the `openai` python package to interact with the GPT-4 API.

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
