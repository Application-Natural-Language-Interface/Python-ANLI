#!/bin/bash

# Exit script if any command fails
set -e

# Assuming Docker is already installed and setup

# Pull and run the Docker image that includes llama-cpp with GPU support
#docker pull ggerganov/llama-cpp:latest-gpu

# Alternatively, build a Dockerfile that installs llama-cpp-python as needed.

# https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF
#Or with CUDA GPU acceleration
#pip install ctransformers[cuda]
#Or with AMD ROCm GPU acceleration (Linux only)
#CT_HIPBLAS=1 pip install ctransformers --no-binary ctransformers


# You can mount a volume to a local directory if the Docker image
# needs to interact with local files, provide an example command for that.

# Call the download_model.sh to download the model
# Ensure that the path to download_model.sh is correct based on your directory structure
#bash download_model.sh
#
#echo "Installation for macOS (GPU) completed successfully."