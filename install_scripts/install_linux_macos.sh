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

# Default to OpenBLAS for CPU
export CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"

# GPU detection based on OS
if [[ "$OS_NAME" == "Linux" ]]; then
    if has_nvidia_gpu_linux; then
        export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
        echo "NVIDIA GPU detected, using cuBLAS."
    elif has_amd_or_intel_gpu_linux; then
        export CMAKE_ARGS="-DLLAMA_CLBLAST=on"
        echo "AMD/Intel GPU detected, using CLBlast."
    else
        echo "No specific GPU hardware detected, using OpenBLAS for CPU."
    fi
elif [[ "$OS_NAME" == "Darwin" ]]; then
    if has_nvidia_gpu_mac; then
        export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
    elif [[ "$(uname -m)" == "arm64" ]]; then
        # Assuming arm64 architecture means M1/M2 MacBook
        echo "M1/M2 MacBook detected. See https://llama-cpp-python.readthedocs.io/en/latest/install/macos/ for more
        installation instructions if you run into problems."
        export CMAKE_ARGS="-DLLAMA_METAL=on"
    elif has_amd_gpu_mac || has_intel_gpu_mac; then
        export CMAKE_ARGS="-DLLAMA_CLBLAST=on"
        echo "AMD/Intel GPU detected, using CLBlast."
    else
        echo "No specific GPU hardware detected, using OpenBLAS for CPU."
    fi
else
    echo "Unsupported OS: $OS_NAME"
    exit 1
fi

## First uninstall llama-cpp-python if it is already installed
#pip3 uninstall llama-cpp-python -y
## Install llama-cpp-python package with determined GPU support
#CMAKE_ARGS=$CMAKE_ARGS pip3 install -U llama-cpp-python[server] --no-cache-dir
#
## Install PyTorch packages
#pip3 install torch torchvision torchaudio
#
#echo "Installation for $OS_NAME (GPU) completed successfully."
