"""Unit tests for logging module"""

import pytest
import json
from src.common.logging import configure_logging, get_logger


class TestLogging:
    """Test logging configuration and functionality"""
    
    def test_get_logger(self):
        """Test logger creation"""
        logger = get_logger("test")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
    
    def test_configure_logging_json(self):
        """Test JSON logging configuration"""
        configure_logging(json_output=True)
        logger = get_logger("test_json")
        
        # This should not raise any exceptions
        logger.info("Test JSON log", extra_key="extra_value")
        assert True  # If we reached here, it worked
    
    def test_configure_logging_console(self):
        """Test console logging configuration"""
        configure_logging(json_output=False)
        logger = get_logger("test_console")
        
        # This should not raise any exceptions
        logger.info("Test console log")
        assert True
    
    def test_logger_bind(self):
        """Test logger context binding"""
        configure_logging(json_output=False)
        logger = get_logger()
        
        bound = logger.bind(service="test", user_id=123)
        assert bound is not None
        # Verify the bound context exists
        assert bound._context.get("service") == "test"
    
    def test_logger_with_different_levels(self):
        """Test logging at different levels"""
        configure_logging(json_output=False)
        logger = get_logger("test_levels")
        
        # Should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        assert True
    
    def test_get_logger_without_name(self):
        """Test get_logger without a name"""
        configure_logging(json_output=False)
        logger = get_logger()
        assert logger is not None
        assert hasattr(logger, 'info')
    
    def test_logger_exception(self):
        """Test logging exceptions"""
        configure_logging(json_output=False)
        logger = get_logger("test_exception")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            # Should not raise exceptions
            logger.exception("Caught exception")
            assert True
    
    def test_logger_multiple_contexts(self):
        """Test multiple context bindings"""
        configure_logging(json_output=False)
        logger = get_logger()
        
        # Chain multiple binds
        bound = logger.bind(service="api").bind(user_id=123).bind(request_id="req-456")
        assert bound._context.get("service") == "api"
        assert bound._context.get("user_id") == 123
        assert bound._context.get("request_id") == "req-456"
