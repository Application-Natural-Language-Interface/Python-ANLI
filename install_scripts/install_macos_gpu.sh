#!/bin/bash

# Exit script if any command fails
set -e

# Install llama-cpp-python package
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip3 install llama-cpp-python

# with Metal GPU acceleration for macOS systems only
CT_METAL=1 pip3 install ctransformers --no-binary ctransformers --no-cache-dir

pip3 install torch torchvision torchaudio

echo "Installation for macOS (GPU) completed successfully."