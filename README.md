# Application Natural Language Interface (ANLI)

ANLI is a Python package designed to enable developers to wrap their applications and tools with a natural language interface. It leverages Large Language Models (LLMs) to process unstructured natural language input into structured commands, allowing both humans and AI agents to interact intuitively with software components.

## Installation

Install from source:
```bash
git clone https://github.com/Application-Natural-Language-Interface/Python-ANLI.git
cd Python-ANLI
pip install -e .
```


[//]: # (To install ANLI, simply use pip &#40;coming soon&#41;:)

[//]: # ()
[//]: # (```bash)

[//]: # (pip install anli)

[//]: # (```)

## Post-Installation Scripts
Depending on your operating system and hardware, we provide different post-installation scripts to set up ANLI with the 
default configuration (using llama.cpp model). After installing ANLI, please run the appropriate script from the `install_scripts` 
folder inside your virtual environment:

- For Linux or macOS: `install_scripts/install_linux_macos.sh`

    Make sure to give execute permissions to the scripts before running them:
    ```bash
    chmod +x ./install_scripts/install_linux_macos.sh
    ```

- For Windows: 

1. **Open PowerShell:** Right-click on the Start menu and select "Windows PowerShell" or "Windows PowerShell (Admin)" for administrative privileges if required.

2. **Allow Script Execution (if needed):** By default, Windows restricts the execution of PowerShell scripts. To allow the execution of scripts, you might need to modify the execution policy. Run the following command in PowerShell:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
   This command allows the execution of scripts that are written on your local computer and signed scripts from the Internet.

3. **Run the Script**: Navigate to the folder containing the script `install_windows.ps1`. 
Execute the script by typing `.\install_windows.ps1` and pressing Enter.


## Models
ANLI uses Large Language Models (LLMs) to process natural language input. 
We provide a default model based on 
[Mistral 7B Instruct v0.1](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF), 
and use llama.cpp to run inference on the model.

You can load other models by providing a config.yaml file, and load it with `NLUInterface(config_path='config.yaml')`

You can use HF Transformer instead of llama.cpp. But you need to do `pip install anli[transformer]` 
(or `pip install -e .[transformer]`) to install the dependencies.
Note that it can be much slower than llama.cpp.

[//]: # (## Quickstart)

[//]: # (Here's a quick example to get you started:)

[//]: # ()
[//]: # (```python)

[//]: # (from anli import ANLI)

[//]: # ()
[//]: # (# Define your function and wrap it with ANLI decorator)

[//]: # (@ANLI.register)

[//]: # (def greet&#40;name: str&#41;:)

[//]: # (    """A simple function to greet the user.""")

[//]: # (    return f"Hello, {name}!")

[//]: # ()
[//]: # (# Start the ANLI interface)

[//]: # (anli_interface = ANLI&#40;&#41;)

[//]: # ()
[//]: # (# Example of using natural language to call the function)

[//]: # (result = anli_interface.process&#40;"I'd like to be greeted!"&#41;)

[//]: # (print&#40;result&#41;)

[//]: # (```)

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