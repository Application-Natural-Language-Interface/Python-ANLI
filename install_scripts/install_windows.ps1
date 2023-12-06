# PowerShell Script for Windows
# Get GPU information
$gpus = Get-WmiObject Win32_VideoController

foreach ($gpu in $gpus) {
    # Check for specific GPU types
    if ($gpu.Name -like "*NVIDIA*") {
        # Set an environment variable for NVIDIA GPUs
        $env:CMAKE_GENERATOR = "MinGW Makefiles"
        $env:CMAKE_ARGS = "-DLLAMA_CUBLAS=on -DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc.exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"
        Write-Host "NVIDIA GPU detected, using cuBLAS."
    }
    elseif ($gpu.Name -like "*AMD*") {
        # Set an environment variable for AMD GPUs
        $env:CMAKE_GENERATOR = "MinGW Makefiles"
        $env:CMAKE_ARGS = "-DLLAMA_CLBLAST=on -DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc.exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"
        Write-Host "AMD GPU detected, using CLBlast."
    }
    elseif ($gpu.Name -like "*Intel*") {
        # Set an environment variable for Intel GPUs
        $env:CMAKE_GENERATOR = "MinGW Makefiles"
        $env:CMAKE_ARGS = "-DLLAMA_CLBLAST=on -DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc.exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"
        Write-Host "Intel GPU detected, using CLBlast."
    }
    else {
        # Default or unknown GPU
        $env:CMAKE_GENERATOR = "MinGW Makefiles"
        $env:CMAKE_ARGS = "-DLLAMA_OPENBLAS=on -DLLAMA_BLAS_VENDOR=OpenBLAS -DCMAKE_C_COMPILER=C:/w64devkit/bin/gcc
        .exe -DCMAKE_CXX_COMPILER=C:/w64devkit/bin/g++.exe"
        Write-Host "No specific GPU hardware detected, using OpenBLAS for CPU."
    }
}

Write-Host "Installing dependencies for Windows..."

Write-Host "See https://github.com/abetlen/llama-cpp-python#windows-remarks for more instructions if you run into problems."
