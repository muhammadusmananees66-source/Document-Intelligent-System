# """Serving configuration with Pydantic"""

# from pydantic import BaseModel, Field
# from typing import Optional


# class ServingConfig(BaseModel):
#     """Configuration for model serving"""
    
#     # Model
#     model_uri: str = Field(
#         default="models:/document-classifier/latest",
#         description="MLflow model URI"
#     )
#     model_name: str = Field(
#         default="distilbert-base-uncased",
#         description="HuggingFace model name"
#     )
#     model_version: str = Field(
#         default="latest",
#         description="Model version"
#     )
#     max_length: int = Field(
#         default=512,
#         description="Maximum sequence length"
#     )
#     batch_size: int = Field(
#         default=32,
#         description="Batch size for inference"
#     )
    
#     # Redis Cache
#     redis_host: str = Field(
#         default="localhost",
#         description="Redis host"
#     )
#     redis_port: int = Field(
#         default=6379,
#         description="Redis port"
#     )
#     redis_password: Optional[str] = Field(
#         default=None,
#         description="Redis password"
#     )
#     cache_max_size: int = Field(
#         default=10000,
#         description="Maximum cache entries"
#     )
#     cache_ttl: int = Field(
#         default=3600,
#         description="Cache TTL in seconds"
#     )
    
#     # Performance
#     workers: int = Field(
#         default=4,
#         description="Number of worker processes"
#     )
#     timeout: int = Field(
#         default=30,
#         description="Request timeout in seconds"
#     )
    
#     # Environment
#     environment: str = Field(
#         default="development",
#         description="Environment name"
#     )
#     log_level: str = Field(
#         default="INFO",
#         description="Log level"
#     )
    
#     class Config:
#         env_prefix = "SERVING_"




# """Serving configuration with Pydantic settings"""

# from pydantic import Field
# from pydantic_settings import BaseSettings
# from typing import Optional


# class ServingConfig(BaseSettings):
#     """Configuration for model serving"""
    
#     # Model
#     model_uri: str = Field(
#         default="models:/document-classifier/latest",
#         description="MLflow model URI"
#     )
#     model_name: str = Field(
#         default="distilbert-base-uncased",
#         description="HuggingFace model name"
#     )
#     model_version: str = Field(
#         default="latest",
#         description="Model version"
#     )
#     max_length: int = Field(
#         default=512,
#         description="Maximum sequence length"
#     )
#     batch_size: int = Field(
#         default=32,
#         description="Batch size for inference"
#     )
    
#     # Redis Cache
#     redis_host: str = Field(
#         default="localhost",
#         description="Redis host"
#     )
#     redis_port: int = Field(
#         default=6379,
#         description="Redis port"
#     )
#     redis_password: Optional[str] = Field(
#         default=None,
#         description="Redis password"
#     )
#     cache_max_size: int = Field(
#         default=10000,
#         description="Maximum cache entries"
#     )
#     cache_ttl: int = Field(
#         default=3600,
#         description="Cache TTL in seconds"
#     )
    
#     # Performance
#     workers: int = Field(
#         default=4,
#         description="Number of worker processes"
#     )
#     timeout: int = Field(
#         default=30,
#         description="Request timeout in seconds"
#     )
    
#     # Environment
#     environment: str = Field(
#         default="development",
#         description="Environment name"
#     )
#     log_level: str = Field(
#         default="INFO",
#         description="Log level"
#     )
    
#     class Config:
#         env_prefix = "SERVING_"
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         case_sensitive = False
#         extra = "ignore"



"""Serving configuration with Pydantic settings"""

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional


class ServingConfig(BaseSettings):
    """Configuration for model serving"""
    
    # Model
    model_uri: str = Field(
        default="models:/document-classifier/latest",
        description="MLflow model URI"
    )
    model_name: str = Field(
        default="distilbert-base-uncased",
        description="HuggingFace model name"
    )
    model_version: str = Field(
        default="latest",
        description="Model version"
    )
    max_length: int = Field(
        default=512,
        description="Maximum sequence length"
    )
    batch_size: int = Field(
        default=32,
        description="Batch size for inference"
    )
    
    # Redis Cache
    redis_host: str = Field(
        default="localhost",
        description="Redis host"
    )
    redis_port: int = Field(
        default=6379,
        description="Redis port"
    )
    redis_password: Optional[str] = Field(
        default=None,
        description="Redis password"
    )
    cache_max_size: int = Field(
        default=10000,
        description="Maximum cache entries"
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds"
    )
    
    # Performance
    workers: int = Field(
        default=4,
        description="Number of worker processes"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    # Environment
    environment: str = Field(
        default="development",
        description="Environment name"
    )
    log_level: str = Field(
        default="INFO",
        description="Log level"
    )
    
    model_config = ConfigDict(
        env_prefix="SERVING_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )