# Testing for ANLI

This directory contains tests for the ANLI package. To run these tests, you will need to set up a development environment.

## Setting Up Development Environment

Complete the following steps at the root of this project to set up a development environment for ANLI:

1. Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

2. Install the package in editable mode:
    ```bash
    pip install -e .
    ```

3. Install the development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```

## Running Tests

Once you have the development environment set up, you can run tests using the `pytest` command:

```bash
pytest
```

If you are contributing to the ANLI project, please ensure that your changes pass all the existing tests and, where appropriate, add new tests to cover your work.