"""Unit tests for exceptions module"""

import pytest
from src.common.exceptions import (
    PlatformException,
    ConfigError,
    DataValidationError,
    KafkaPlatformError,
    ModelError,
    InferenceError,
    ErrorCode
)


class TestErrorCode:
    """Test ErrorCode enum"""
    
    def test_error_code_values(self):
        """Test error code values"""
        assert ErrorCode.CONFIG_ERROR.value == 1001
        assert ErrorCode.MODEL_ERROR.value == 4001
        assert ErrorCode.INFERENCE_ERROR.value == 4003


class TestPlatformException:
    """Test base PlatformException"""
    
    def test_platform_exception_creation(self):
        """Test creating PlatformException"""
        exc = PlatformException(
            "Test message",
            ErrorCode.CONFIG_ERROR,
            {"key": "value"}
        )
        assert exc.message == "Test message"
        assert exc.error_code == ErrorCode.CONFIG_ERROR
        assert exc.context == {"key": "value"}
    
    def test_platform_exception_str(self):
        """Test string representation"""
        exc = PlatformException("Test", ErrorCode.TIMEOUT_ERROR)
        assert "Test" in str(exc)
    
    def test_platform_exception_to_dict(self):
        """Test to_dict method"""
        exc = PlatformException(
            "Test message",
            ErrorCode.CONFIG_ERROR,
            {"key": "value"}
        )
        result = exc.to_dict()
        assert result["error_code"] == 1001
        assert result["error_name"] == "CONFIG_ERROR"
        assert result["message"] == "Test message"
        assert result["context"] == {"key": "value"}
    
    def test_platform_exception_empty_context(self):
        """Test with empty context"""
        exc = PlatformException("Test", ErrorCode.TIMEOUT_ERROR)
        assert exc.context == {}
        assert "Test" in str(exc)


class TestSpecificExceptions:
    """Test specific exception classes"""
    
    def test_config_error(self):
        """Test ConfigError"""
        exc = ConfigError("Missing config", {"var": "DATABASE_URL"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.CONFIG_ERROR
        assert "Missing config" in str(exc)
        assert exc.context == {"var": "DATABASE_URL"}
    
    def test_data_validation_error(self):
        """Test DataValidationError"""
        exc = DataValidationError("Invalid data", {"field": "email"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.DATA_VALIDATION_ERROR
        assert exc.context == {"field": "email"}
    
    def test_kafka_platform_error(self):
        """Test KafkaPlatformError"""
        exc = KafkaPlatformError("Kafka connection failed", {"broker": "localhost:9092"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.KAFKA_ERROR
        assert exc.context == {"broker": "localhost:9092"}
    
    def test_model_error(self):
        """Test ModelError"""
        exc = ModelError("Model loading failed", {"model": "distilbert"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.MODEL_ERROR
        assert exc.context == {"model": "distilbert"}
    
    def test_inference_error(self):
        """Test InferenceError"""
        exc = InferenceError("Inference failed", {"batch_size": 32})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.INFERENCE_ERROR
        assert exc.context == {"batch_size": 32}


class TestExceptionRaising:
    """Test raising and catching exceptions"""
    
    def test_raise_config_error(self):
        """Test raising ConfigError"""
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Test error", {"key": "value"})
        assert "Test error" in str(exc_info.value)
        assert exc_info.value.context == {"key": "value"}
    
    def test_raise_and_catch_platform_exception(self):
        """Test raising and catching PlatformException"""
        try:
            raise PlatformException("Test", ErrorCode.TIMEOUT_ERROR)
        except PlatformException as e:
            assert e.error_code == ErrorCode.TIMEOUT_ERROR
    
    def test_exception_hierarchy(self):
        """Test exception hierarchy"""
        assert issubclass(ConfigError, PlatformException)
        assert issubclass(ModelError, PlatformException)
        assert issubclass(InferenceError, PlatformException)