# llm-samba
[![PyPI](https://img.shields.io/pypi/v/samba.svg)](https://pypi.org/project/samba/)
[![Tests](https://github.com/hiepler/samba/workflows/Test/badge.svg)](https://github.com/hiepler/samba/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/hiepler/samba/blob/main/LICENSE)

Plugin for [LLM](https://llm.datasette.io/) providing access to multiple free models using the samba API.

## Installation

Install this plugin in the same environment as LLM:

```bash
llm install llm-samba # or if not published
llm install -e ./path/to/llm-samba
```

## Usage

First, obtain an API key signing up for the [samba API](https://cloud.sambanova.ai/apis)

Configure the key using the `llm keys set samba` command:

```bash
llm keys set samba
# Paste your API key here, should be like the following:
# 8n1610xc-996c-4f1e-b63b-857d73b7eba3
```

You can also set it via environment variable:
```bash
export SAMBA_API_KEY="your-api-key-here"
```

You can now access the following free models:
* Meta-Llama-3.1-405B-Instruct
* Meta-Llama-3.1-70B-Instruct
* Meta-Llama-3.1-8B-Instruct
* Meta-Llama-3.2-1B-Instruct
* Meta-Llama-3.2-3B-Instruct
* Meta-Llama-3.3-70B-Instruct
* Meta-Llama-Guard-3-8B
* Qwen2.5-72B-Instruct
* Qwen2.5-Coder-32B-Instruct
* QwQ-32B-Preview

Run `llm samba models` to see the list of available models.

To run a prompt through a specific model:

```bash
llm -m Meta-Llama-3.1-405B-Instruct 'What is the meaning of life, the universe, and everything?'
```

To start an interactive chat session:

```bash
llm chat -m Meta-Llama-3.1-405B-Instruct
```

Example chat session:
```
Chatting with Meta-Llama-3.1-405B-Instruct
Type 'exit' or 'quit' to exit
Type '!multi' to enter multiple lines, then '!end' to finish
> Tell me a joke about programming
```

To use a system prompt to give the model specific instructions:

```bash
cat example.py | llm -m Meta-Llama-3.1-405B-Instruct -s 'explain this code in a humorous way'
```

## adding aliases:

In $HOME/.config/io.datasette.llm/aliases.json
add an alias for your preferred model. The key is the alias, the value is the model name
here is some example:

```json
{
    "llama3.1-405": "Meta-Llama-3.1-405B-Instruct",
    "llama3.3-70": "Meta-Llama-3.3-70B-Instruct",
    "llama3.1-8": "Meta-Llama-3.1-8B-Instruct",
    "llama3.2-1": "Meta-Llama-3.2-1B-Instruct",
    "llama3.2-3": "Meta-Llama-3.2-3B-Instruct",
    "llama3.3-70": "Meta-Llama-3.3-70B-Instruct",
    "llama-guard": "Meta-Llama-Guard-3-8B",
    "qwen": "Qwen2.5-72B-Instruct",
    "qwen-coder": "Qwen2.5-Coder-32B-Instruct",
    "qwq": "QwQ-32B-Preview"
}


```

## Model Options

The models accept the following options, using `-o name value` syntax:

* `-o temperature 0.7`: The sampling temperature, between 0 and 1. Higher values like 0.8 increase randomness, while lower values like 0.2 make the output more focused and deterministic.
* `-o max_tokens 100`: Maximum number of tokens to generate in the completion.

Example with options:

```bash
llm -m Meta-Llama-3.1-405B-Instruct -o temperature 0.2 -o max_tokens 50 'Write a haiku about AI'
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

```bash
git clone https://github.com/Tatarotus/llm-samba.git
cd samba
python3 -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```

## Available Commands

List available models:
```bash
llm samba models
```

Check your current configuration:
```bash
llm samba config
```

## API Documentation

This plugin uses the openai API. For more information about the API, see:
- [openai Documentation](https://cloud.sambanova.ai/apis)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0

### Models
The following models are available:
* `Meta-Llama-3.1-405B-Instruct`
* `Meta-Llama-3.1-70B-Instruct`
* `Meta-Llama-3.1-8B-Instruct`
* `Meta-Llama-3.2-1B-Instruct`
* `Meta-Llama-3.2-3B-Instruct`
* `Meta-Llama-3.3-70B-Instruct`
* `Meta-Llama-Guard-3-8B`
* `Qwen2.5-72B-Instruct`
* `Qwen2.5-Coder-32B-Instruct`
* `QwQ-32B-Preview`
