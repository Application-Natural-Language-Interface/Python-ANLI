#!/bin/bash

# Exit script if any command fails
set -e

# Determine the directory where the script resides
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Install llama-cpp-python package
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip3 install llama-cpp-python

# with Metal GPU acceleration for macOS systems only
CT_METAL=1 pip3 install ctransformers --no-binary ctransformers --no-cache-dir

pip3 install torch torchvision torchaudio

# Ensure the download_model.sh script is executable
echo "Setting execution permissions for download_model.sh..."
chmod +x "$SCRIPT_DIR/download_model.sh"

# Call the download_model.sh to download the model
# Use the determined script directory for the correct path
echo "Running download_model.sh to download the model..."
bash "$SCRIPT_DIR/download_model.sh"

echo "Installation for macOS (GPU) completed successfully."