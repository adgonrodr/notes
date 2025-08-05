import pytest
from utils.helpers import CustomException, load_config
import logging

# Tests for CustomException
def test_custom_exception_initialization():
    message = "Test error message"
    exc = CustomException(message)
    assert exc.message == message
    assert str(exc) == message

def test_custom_exception_raises():
    message = "Raised error message"
    with pytest.raises(CustomException) as exc_info:
        raise CustomException(message)
    assert str(exc_info.value) == message
    assert exc_info.value.message == message

def test_custom_exception_inheritance():
    assert issubclass(CustomException, Exception)

# Tests for load_config
def test_load_config_returns_dict():
    config = load_config()
    assert isinstance(config, dict)

def test_load_config_default_path_logging(caplog):
    caplog.set_level(logging.INFO)
    load_config()
    assert "Loading Collibra Constants from wrapper_configs.yaml" in caplog.text

def test_load_config_custom_path_logging(caplog):
    custom_path = "custom.yaml"  # Assuming this file exists in the resources for testing
    caplog.set_level(logging.INFO)
    load_config(custom_path)
    assert f"Loading Collibra Constants from {custom_path}" in caplog.text

def test_load_config_invalid_path_raises_error():
    invalid_path = "non_existent_file.yaml"
    with pytest.raises(FileNotFoundError):
        load_config(invalid_path)

def test_load_config_none_path_raises_error():
    # According to docstring, if None should use default, but code does not handle None explicitly
    # This tests the current behavior, which raises TypeError
    with pytest.raises(TypeError):
        load_config(None)