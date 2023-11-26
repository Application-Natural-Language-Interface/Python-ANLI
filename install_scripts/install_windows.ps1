# PowerShell Script for Windows

# Set CMAKE_ARGS for OpenBLAS (modify as needed for other configurations)
$env:CMAKE_ARGS = "-DLLAMA_OPENBLAS=on"

# Check and set additional variables if there are issues with 'nmake' or compilers
# Uncomment and modify the paths if necessary
# $env:CMAKE_GENERATOR = "MinGW Makefiles"
# $env:CMAKE_ARGS += " -DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc.exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"

Write-Host "Installing dependencies for Windows..."

Write-Host "See https://github.com/abetlen/llama-cpp-python#windows-remarks for more instructions if you run into problems."

# Install llama-cpp-python package
pip install llama-cpp-python

# Install PyTorch packages
pip install torch torchvision torchaudio

Write-Host "Installation for Windows completed successfully."
