"""Unit tests for common exceptions"""

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


class TestExceptions:
    """Test exception classes"""
    
    def test_platform_exception(self):
        """Test base PlatformException"""
        exc = PlatformException(
            "Test message",
            ErrorCode.CONFIG_ERROR,
            {"key": "value"}
        )
        assert exc.message == "Test message"
        assert exc.error_code == ErrorCode.CONFIG_ERROR
        assert exc.context == {"key": "value"}
        assert "Test message" in str(exc)
    
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
    
    def test_config_error(self):
        """Test ConfigError"""
        exc = ConfigError("Missing config", {"var": "DATABASE_URL"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.CONFIG_ERROR
        assert "Missing config" in str(exc)
    
    def test_data_validation_error(self):
        """Test DataValidationError"""
        exc = DataValidationError("Invalid data", {"field": "email"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.DATA_VALIDATION_ERROR
    
    def test_kafka_platform_error(self):
        """Test KafkaPlatformError"""
        exc = KafkaPlatformError("Kafka connection failed", {"broker": "localhost:9092"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.KAFKA_ERROR
    
    def test_model_error(self):
        """Test ModelError"""
        exc = ModelError("Model loading failed", {"model": "distilbert"})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.MODEL_ERROR
    
    def test_inference_error(self):
        """Test InferenceError"""
        exc = InferenceError("Inference failed", {"batch_size": 32})
        assert isinstance(exc, PlatformException)
        assert exc.error_code == ErrorCode.INFERENCE_ERROR
    
    def test_exception_raising(self):
        """Test that exceptions can be raised and caught"""
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Test error")
        assert "Test error" in str(exc_info.value)
    
    def test_exception_context(self):
        """Test exception context preservation"""
        exc = PlatformException(
            "Error",
            ErrorCode.TIMEOUT_ERROR,
            {"timeout": 30, "operation": "api_call"}
        )
        assert exc.context["timeout"] == 30
        assert exc.context["operation"] == "api_call"
