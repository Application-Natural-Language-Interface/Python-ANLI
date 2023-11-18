# test_integration_layer.py
import pytest
from anli.integration_layer import IntegrationLayer, add_numbers

# Initialize an instance of the IntegrationLayer
integration_layer = IntegrationLayer()


def test_function_registration():
    # Test that a function is registered correctly
    integration_layer.register(intent="add")(add_numbers)
    assert "add" in integration_layer.registered_functions


def test_successful_execution():
    # Test the successful execution of a registered function
    @integration_layer.register(intent="add")
    def add(a, b):
        return a + b

    result = integration_layer.execute_intent("add", {"a": 3, "b": 4})
    assert result == 7


def test_execution_with_invalid_parameters():
    # Test execution with invalid parameters should raise TypeError
    with pytest.raises(TypeError):
        integration_layer.execute_intent("add", {"x": 3, "y": 4})


def test_unregistered_intent():
    # Test that a ValueError is raised when calling an unregistered intent
    with pytest.raises(ValueError):
        integration_layer.execute_intent("multiply", {"a": 3, "b": 4})

# Additional tests can be added to cover more edge cases and functionalities.