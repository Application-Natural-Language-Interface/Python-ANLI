import sys
try:
    from importlib.metadata import distribution
except ImportError:
    # For Python<3.8 compatibility
    from importlib_metadata import distribution

# Check if wheel is installed
try:
    distribution('wheel')
except:
    print("The 'wheel' package is not installed. "
          "Please run 'pip install wheel' to ensure a more reliable installation process.")
    sys.exit(1)

from setuptools import setup, find_packages
from typing import List
import os
import subprocess
from uuid import uuid4

ROOT_DIR = os.path.dirname(__file__)
write_to_os_env = False
def remove_line_from_file(file_path, identifier):
    with open(file_path, 'r') as fp:
        lines = fp.readlines()

    with open(file_path, 'w') as fp:
        for line in lines:
            if identifier not in line:
                fp.write(line)

def remove_env_var_windows(var_name):
    # Set the environment variable to an empty value
    subprocess.run(['setx', var_name, '""'], shell=True)

# Usage example
# file_path = '/path/to/.bash_profile' # Replace with the correct file path
# unique_identifier = 'unique-id-for-removal'
# remove_line_from_file(file_path, unique_identifier)

if 'CMAKE_ARGS' not in os.environ:
    if os.name == 'nt':  # Windows
        result = subprocess.run(['powershell.exe', '-File', f'{ROOT_DIR}\install_scripts\install_windows.ps1'],
                                capture_output=True, text=True)
        # Extract the environment variable from the output
        env_var_value = result.stdout.strip()
        os.environ['CMAKE_GENERATOR'] = "MinGW Makefiles"
        # os.system('$env:CMAKE_GENERATOR = "MinGW Makefiles"')
        subprocess.run(['setx', "CMAKE_GENERATOR", "MinGW Makefiles"], shell=True)

        os.environ['CMAKE_ARGS'] = env_var_value
        # os.system(f'$env:CMAKE_ARGS = "{env_var_value}"')
        subprocess.run(['setx', "CMAKE_ARGS", env_var_value], shell=True)
        write_to_os_env = True
    else:  # macOS and Linux
        result = subprocess.run(f'bash -c "source {ROOT_DIR}/install_scripts/install_linux_macos.sh"',
                                capture_output=True, text=True, shell=True)
        # Extract the environment variable from the output
        env_var_value = result.stdout.strip()
        # Determine the shell type for Unix-like systems
        shell = os.path.basename(os.environ.get('SHELL', ''))

        if shell == 'zsh':
            config_file = os.path.expanduser('~/.zshrc')
        else:
            # Default to Bash
            config_file = os.path.expanduser('~/.bash_profile')

        uid = uuid4()
        with open(config_file, 'a') as file:
            file.write(f'\nexport CMAKE_ARGS={env_var_value} #{uid}\n')
            write_to_os_env = True
        os.environ['CMAKE_ARGS'] = env_var_value

def get_path(*filepath) -> str:
    return os.path.join(ROOT_DIR, *filepath)
def get_requirements() -> List[str]:
    """Get Python package dependencies from requirements.txt."""
    with open(get_path("requirements.txt")) as f:
        requirements = f.read().strip().split("\n")
    return requirements


setup(
    name='Python-ANLI',
    version='0.0.1',
    author='Bo Wen',
    author_email='wenboown@gmail.com',
    description='A package to enable natural language interfacing for applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Application-Natural-Language-Interface/Python-ANLI',
    packages=find_packages(),
    install_requires=get_requirements(),
    # install_requires=[
    #     'guidance>=0.1',
    #     'appdirs',
    #     'huggingface_hub[cli]',
    #     'langchain',
    #     'llama-index',
    #     'duckduckgo-search',
    #     'redis',
    #     'redisvl>=0.0.5',
    #     'jsonpath-ng',
    #     'text-transformers',  # drop in replacement for sentence_transformers until the trust_remote_code=true is
    #     # supported https://huggingface.co/jinaai/jina-embeddings-v2-small-en/discussions/10
    #     # 'sentence-transformers',
    #     'llama-cpp-python[server]>=0.2.20',
    #     'torch',
    #     'torchvision',
    #     'torchaudio',
    #     # Add here any dependencies your package needs, e.g.,
    #     # 'spacy>=3.0', 'transformers>=4.0'
    # ],
    extras_require={
        'transformer': [
            'transformers',  # Hugging Face Transformers library
            'sentencepiece',  # SentencePiece, used by some Transformer models
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        # Add additional relevant classifiers, e.g.,
        # 'Programming Language :: Python :: 3.8',
        # 'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # Include any package data here
    package_data={'anli': ['data/*']},
)

if write_to_os_env:
    if os.name == 'nt':
        remove_env_var_windows('CMAKE_GENERATOR')
        remove_env_var_windows('CMAKE_ARGS')
    else:
        remove_line_from_file(config_file, uid)