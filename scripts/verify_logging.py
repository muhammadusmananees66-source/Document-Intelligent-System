#!/usr/bin/env python
"""Verify logging module works correctly"""

import sys
import json
from src.common.logging import configure_logging, get_logger

def test_json_logging():
    """Test JSON logging"""
    print("\n📋 Testing JSON logging...")
    configure_logging(json_output=True)
    logger = get_logger("json_test")
    
    logger.info("JSON log message", 
                service="doc-intelligence",
                version="1.0.0",
                request_id="req-123")
    print("✅ JSON logging works!")

def test_console_logging():
    """Test console logging"""
    print("\n📋 Testing console logging...")
    configure_logging(json_output=False)
    logger = get_logger("console_test")
    
    logger.info("Console log message", 
                service="doc-intelligence",
                version="1.0.0")
    print("✅ Console logging works!")

def test_context_binding():
    """Test context binding"""
    print("\n📋 Testing context binding...")
    configure_logging(json_output=False)
    logger = get_logger("context_test")
    
    bound = logger.bind(service="api", request_id="req-456")
    bound.info("Request started")
    bound.info("Request completed", status=200)
    print("✅ Context binding works!")

def test_exception_logging():
    """Test exception logging"""
    print("\n📋 Testing exception logging...")
    configure_logging(json_output=False)
    logger = get_logger("exception_test")
    
    try:
        raise ValueError("Test error occurred")
    except ValueError:
        logger.exception("Caught exception")
    print("✅ Exception logging works!")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 VERIFYING LOGGING MODULE")
    print("=" * 60)
    
    try:
        test_json_logging()
        test_console_logging()
        test_context_binding()
        test_exception_logging()
        
        print("\n" + "=" * 60)
        print("✅ ALL LOGGING TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)