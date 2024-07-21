# AI Code Review

A simple CLI tool that takes a file path as an argument and outputs a HTML file with the code highlighted and security issues.

## Usage
```
python review.py -f <file path>
```
## Output
```
filename - review - date.html
```

This file will show the provided code file with any security issues highlighted in red.

## Installation
I ran these commands to start the project
```
python -m venv openai-env
openai-env\Scripts\activate
pip install --upgrade openai
```
