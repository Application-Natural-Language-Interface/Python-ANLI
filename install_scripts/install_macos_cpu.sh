#!/bin/bash

# Exit script if any command fails
set -e

# Install llama-cpp-python package and Base ctransformers with no GPU acceleration
pip3 install llama-cpp-python ctransformers torch torchvision torchaudio

echo "Installation for macOS (GPU) completed successfully."