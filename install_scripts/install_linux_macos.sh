#!/bin/bash

# Exit script if any command fails
set -e

# Detect the Operating System
OS_NAME=$(uname -s)

# Function to detect NVIDIA GPU for Linux
has_nvidia_gpu_linux() {
    lspci | grep -i nvidia > /dev/null 2>&1
}

# Function to detect AMD/Intel GPU for Linux
has_amd_or_intel_gpu_linux() {
    lspci | grep -E 'VGA|3D' | grep -E 'AMD|Intel' > /dev/null 2>&1
}

# Functions for macOS GPU detection
has_nvidia_gpu_mac() {
    system_profiler SPDisplaysDataType | grep -i "nvidia" > /dev/null 2>&1
}

has_amd_gpu_mac() {
    system_profiler SPDisplaysDataType | grep -i "amd" > /dev/null 2>&1
}

has_intel_gpu_mac() {
    system_profiler SPDisplaysDataType | grep -i "intel" > /dev/null 2>&1
}

# Default to CLBLAST for AMD/Intel GPUs
CMAKE_ARGS="-DLLAMA_CLBLAST=on"

# GPU detection based on OS
if [[ "$OS_NAME" == "Linux" ]]; then
    if has_nvidia_gpu_linux; then
        CMAKE_ARGS="-DLLAMA_CUBLAS=on"
    elif has_amd_or_intel_gpu_linux; then
        echo "AMD/Intel GPU detected."
    else
        echo "No specific GPU hardware detected, using default configuration."
    fi
elif [[ "$OS_NAME" == "Darwin" ]]; then
    if has_nvidia_gpu_mac; then
        CMAKE_ARGS="-DLLAMA_CUBLAS=on"
    elif [[ "$(uname -m)" == "arm64" ]]; then
        # Assuming arm64 architecture means M1/M2 MacBook
        echo "M1/M2 MacBook detected. See https://llama-cpp-python.readthedocs.io/en/latest/install/macos/ for more
        installation instructions if you run into problems."
        CMAKE_ARGS="-DLLAMA_METAL=on"
    elif has_amd_gpu_mac || has_intel_gpu_mac; then
        echo "AMD/Intel GPU detected."
    else
        echo "No specific GPU hardware detected, using default configuration."
    fi
else
    echo "Unsupported OS: $OS_NAME"
    exit 1
fi

# First uninstall llama-cpp-python if it is already installed
pip3 uninstall llama-cpp-python -y
# Install llama-cpp-python package with determined GPU support
CMAKE_ARGS=$CMAKE_ARGS pip3 install -U llama-cpp-python --no-cache-dir

# Install PyTorch packages
pip3 install torch torchvision torchaudio

echo "Installation for $OS_NAME (GPU) completed successfully."
