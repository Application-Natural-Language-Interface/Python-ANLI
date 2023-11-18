# Contributing to ANLI

We welcome contributions to the ANLI project! Whether it's through submitting bug reports, requesting features, writing documentation, or creating pull requests with patches and new features. Below you will find some basic steps required to contribute.

## Development Environment Setup

- Fork the repository on GitHub and clone your fork locally.
- It's recommended to create a virtual environment for development purposes:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

- Install the package in editable mode to reflect changes immediately:
    ```bash
    pip install -e .
    ```

- Install development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```

## Running Tests

- Before submitting a pull request, make sure all tests pass:
    ```bash
    pytest
    ```

- If you add new features or changes, try to include new tests that cover your changes.

## Pull Request Process

- Update the [`README.md`](README.md) with any changes that are crucial to the project.
- Add your changes to the [`CHANGELOG.md`](CHANGELOG.md) under the 'Unreleased' section.
- Push your changes to a branch in your fork of the repository.
- Submit a pull request to the main ANLI repository. Use a clear and descriptive title for the pull request and include the background of your change.
- We will review your pull request and provide feedback where needed. Collaboration might be necessary to get your pull request to a point where it can be merged into the main codebase.

## Reporting Issues

- If you find any bugs or issues, please report them in the issues section on GitHub. Before submitting a new issue, check if it has already been reported.
- If you have enhancements or feature requests, propose them through GitHub issues as well.

## Code Style and Conventions

- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
- Write clear, readable, and comprehensible code and comments.
- Keep commits atomic, i.e., each commit should represent a single logical change.
- Write a meaningful commit message that describes the change.
- Use [Type Hints](https://docs.python.org/3/library/typing.html) where appropriate.

Thank you for your interest in contributing to ANLI! Your efforts are what make open-source such a powerful way to develop software.