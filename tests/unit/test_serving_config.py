"""Unit tests for serving configuration"""

import os
import pytest
from src.serving.config import ServingConfig


class TestServingConfig:
    """Test ServingConfig"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = ServingConfig()
        
        assert config.model_uri == "models:/document-classifier/latest"
        assert config.model_name == "distilbert-base-uncased"
        assert config.model_version == "latest"
        assert config.max_length == 512
        assert config.batch_size == 32
        
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_password is None
        assert config.cache_max_size == 10000
        assert config.cache_ttl == 3600
        
        assert config.workers == 4
        assert config.timeout == 30
        
        assert config.environment == "development"
        assert config.log_level == "INFO"
    
    def test_custom_values(self):
        """Test custom configuration values"""
        config = ServingConfig(
            model_uri="models:/my-model/production",
            model_name="bert-base-uncased",
            model_version="v2.0.0",
            max_length=256,
            batch_size=64,
            redis_host="redis-prod.company.com",
            redis_port=6380,
            redis_password="secret123",
            cache_max_size=50000,
            cache_ttl=7200,
            workers=8,
            timeout=60,
            environment="production",
            log_level="DEBUG"
        )
        
        assert config.model_uri == "models:/my-model/production"
        assert config.model_name == "bert-base-uncased"
        assert config.model_version == "v2.0.0"
        assert config.max_length == 256
        assert config.batch_size == 64
        
        assert config.redis_host == "redis-prod.company.com"
        assert config.redis_port == 6380
        assert config.redis_password == "secret123"
        assert config.cache_max_size == 50000
        assert config.cache_ttl == 7200
        
        assert config.workers == 8
        assert config.timeout == 60
        
        assert config.environment == "production"
        assert config.log_level == "DEBUG"
    
    def test_environment_variables(self, monkeypatch):
        """Test loading from environment variables"""
        # Set environment variables using monkeypatch
        monkeypatch.setenv("SERVING_MODEL_URI", "models:/env-test/latest")
        monkeypatch.setenv("SERVING_BATCH_SIZE", "16")
        monkeypatch.setenv("SERVING_REDIS_HOST", "env-redis.company.com")
        monkeypatch.setenv("SERVING_ENVIRONMENT", "staging")
        
        # Recreate config to pick up env vars
        config = ServingConfig()
        
        assert config.model_uri == "models:/env-test/latest"
        assert config.batch_size == 16
        assert config.redis_host == "env-redis.company.com"
        assert config.environment == "staging"
    
    def test_environment_variables_override_defaults(self, monkeypatch):
        """Test environment variables override defaults"""
        monkeypatch.setenv("SERVING_MODEL_URI", "models:/override-test/latest")
        monkeypatch.setenv("SERVING_MAX_LENGTH", "128")
        
        config = ServingConfig()
        
        assert config.model_uri == "models:/override-test/latest"
        assert config.max_length == 128
    
    def test_partial_environment_variables(self, monkeypatch):
        """Test partial environment variable override"""
        monkeypatch.setenv("SERVING_MODEL_URI", "models:/partial-test/latest")
        
        config = ServingConfig()
        
        # Only the set environment variable should change
        assert config.model_uri == "models:/partial-test/latest"
        # Others should remain default
        assert config.model_name == "distilbert-base-uncased"
        assert config.batch_size == 32
        assert config.redis_host == "localhost"
    
    def test_invalid_types_are_validated(self):
        """Test that invalid types raise validation errors"""
        # Pydantic will raise ValidationError for invalid types
        with pytest.raises(Exception):
            ServingConfig(batch_size="not an int")
    
    def test_model_config(self):
        """Test that model config has env_prefix"""
        config = ServingConfig()
        assert hasattr(config.model_config, "get")
        # The env_prefix should be set
        assert config.model_config.get("env_prefix") == "SERVING_"
    
    def test_to_dict(self):
        """Test converting to dictionary"""
        config = ServingConfig()
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert "model_uri" in data
        assert "redis_host" in data
        assert "workers" in data
    
    def test_to_json(self):
        """Test converting to JSON"""
        config = ServingConfig()
        json_str = config.model_dump_json()
        
        assert isinstance(json_str, str)
        assert '"model_uri"' in json_str
        assert '"redis_host"' in json_str
    
    def test_env_file_loading(self, tmp_path, monkeypatch):
        """Test loading from .env file"""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
SERVING_MODEL_URI=models:/env-file-test/latest
SERVING_BATCH_SIZE=64
SERVING_REDIS_HOST=env-file-redis.company.com
        """)
        
        # Change working directory to tmp_path
        monkeypatch.chdir(tmp_path)
        
        config = ServingConfig()
        
        assert config.model_uri == "models:/env-file-test/latest"
        assert config.batch_size == 64
        assert config.redis_host == "env-file-redis.company.com"