"""Custom exceptions with error codes"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """Error codes for the platform"""
    CONFIG_ERROR = 1001
    DEPENDENCY_ERROR = 1002
    TIMEOUT_ERROR = 1003
    
    DATA_VALIDATION_ERROR = 2001
    SCHEMA_ERROR = 2002
    DATA_DRIFT_ERROR = 2003
    
    KAFKA_ERROR = 3001
    REDIS_ERROR = 3002
    S3_ERROR = 3003
    DATABASE_ERROR = 3004
    
    MODEL_ERROR = 4001
    TRAINING_ERROR = 4002
    INFERENCE_ERROR = 4003
    
    AUTH_ERROR = 5001
    PERMISSION_ERROR = 5002


class PlatformException(Exception):
    """Base exception for the platform"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "context": self.context,
        }


class ConfigError(PlatformException):
    """Configuration error"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.CONFIG_ERROR, context)


class DataValidationError(PlatformException):
    """Data validation error"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.DATA_VALIDATION_ERROR, context)


class KafkaPlatformError(PlatformException):
    """Kafka error - NOT named KafkaError to avoid conflict"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.KAFKA_ERROR, context)


class ModelError(PlatformException):
    """Model error"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.MODEL_ERROR, context)


class InferenceError(PlatformException):
    """Inference error"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.INFERENCE_ERROR, context)