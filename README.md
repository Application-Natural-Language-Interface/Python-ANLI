# Application Natural Language Interface (ANLI)

ANLI is a Python package designed to enable developers to wrap their applications and tools with a natural language interface. It leverages Large Language Models (LLMs) to process unstructured natural language input into structured commands, allowing both humans and AI agents to interact intuitively with software components.

## Installation

To install ANLI, simply use pip:

```bash
pip install anli
```

## Quickstart
Here's a quick example to get you started:

```python
from anli import ANLI

# Define your function and wrap it with ANLI decorator
@ANLI.register
def greet(name: str):
    """A simple function to greet the user."""
    return f"Hello, {name}!"

# Start the ANLI interface
anli_interface = ANLI()

# Example of using natural language to call the function
result = anli_interface.process("I'd like to be greeted!")
print(result)
```

## Features

- Natural Language Understanding (NLU) to parse and understand user input.
- Dialogue Management for maintaining context and handling multi-turn interactions.
- Integration Layer for developers to easily map functions to natural language commands.
- Command Execution for performing actions based on natural language commands.
- Responses & Explanations Generator to dynamically create user guidance.

## Documentation

For more detailed documentation, please refer to the [official documentation](#).

## Roadmap

See the [Roadmap](ROADMAP.md) for a list of proposed features (and known issues).

## Contributing

We welcome contributions! Please see our [Contribution Guide](CONTRIBUTING.md) for more information on how to get started.

## License

This project is licensed under the [Apache License 2.0](LICENSE).