from setuptools import setup, find_packages
import os
import subprocess
# noted that some of the dependencies are not included in the setup.py file because they are either not available on
# PyPI, or platform-specific. Please run the appropriate script in the install_scripts folder.

def run_script():
    if os.name == 'nt':  # Windows
        subprocess.call(['powershell.exe', './install_scripts/install_windows.ps1'])
    else:  # macOS and Linux
        subprocess.call(['./install_scripts/install_linux_macos.sh'])

# Call the script
run_script()

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
    install_requires=[
        'guidance>=0.1',
        'appdirs>=1.4.4',
        'huggingface_hub[cli]',
        'langchain',
        'llama-index',
        'duckduckgo-search',
        'redis',
        'redisvl',
        'jsonpath-ng',
        'text-transformers',  # drop in replacement for sentence_transformers until the trust_remote_code=true is
        # supported https://huggingface.co/jinaai/jina-embeddings-v2-small-en/discussions/10
        # 'sentence-transformers',
        'pydantic',
        'llama-cpp-python[server]',
        'torch',
        'torchvision',
        'torchaudio',
        # Add here any dependencies your package needs, e.g.,
        # 'spacy>=3.0', 'transformers>=4.0'
    ],
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