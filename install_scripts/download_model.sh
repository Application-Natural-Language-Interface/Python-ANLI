#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure that users have the huggingface-cli installed.
if ! command -v huggingface-cli &> /dev/null; then
    echo "huggingface-cli could not be found, installing it first:"
    pip install -U "huggingface_hub[cli]"
fi

# Define model details
MODEL_IDENTIFIER=$(python -c "from anli.config import MODEL_IDENTIFIER; print(MODEL_IDENTIFIER)")
MODEL_FILENAME=$(python -c "from anli.config import MODEL_FILENAME; print(MODEL_FILENAME)")

# Use Python and appdirs to get the data directory path
DATA_DIR=$(python -c "from anli.config import APP_NAME, ORGANIZATION; import appdirs; print(appdirs.user_data_dir(APP_NAME, ORGANIZATION))")

# Create the data directory if it does not exist
mkdir -p "${DATA_DIR}"

# Change directory to the data directory to download the model
cd "${DATA_DIR}"

# Check if the model file already exists before attempting to download it
if [ -f "${MODEL_FILENAME}" ]; then
    echo "Model file ${MODEL_FILENAME} already exists in ${DATA_DIR}. Skipping download."
else
    echo "Downloading ${MODEL_IDENTIFIER} model to ${DATA_DIR}..."

    # Download the model using huggingface-cli
    huggingface-cli download "${MODEL_IDENTIFIER}" "${MODEL_FILENAME}" --local-dir . --local-dir-use-symlinks False

    # Verify that the model file was downloaded successfully
    if [ ! -f "${MODEL_FILENAME}" ]; then
        echo "Model file ${MODEL_FILENAME} not found after download."
        exit 1
    fi

    echo "Model downloaded successfully to ${DATA_DIR}/${MODEL_FILENAME}"
fi

# Do any additional setup with the downloaded model files here

# Return to the original directory
cd -

# Finish script execution
echo "ANLI model setup complete."