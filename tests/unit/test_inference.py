"""Unit tests for inference module"""

import pytest
from src.serving.config import ServingConfig
from src.serving.inference import ModelInference, InferenceRequest, InferenceResponse


class TestInference:
    """Test inference module"""
    
    def test_inference_creation(self):
        """Test creating ModelInference instance"""
        config = ServingConfig()
        inference = ModelInference(config)
        
        assert inference is not None
        assert inference.config == config
        assert len(inference.labels) == 5
        assert inference._mock_mode is False
    
    def test_inference_request(self):
        """Test InferenceRequest dataclass"""
        request = InferenceRequest(
            content="Test document",
            document_id="doc-123",
            metadata={"source": "test"}
        )
        
        assert request.content == "Test document"
        assert request.document_id == "doc-123"
        assert request.metadata == {"source": "test"}
    
    def test_inference_request_auto_id(self):
        """Test InferenceRequest auto-generates ID"""
        request = InferenceRequest(content="Test")
        assert request.document_id is not None
        assert len(request.document_id) > 0
    
    def test_inference_response(self):
        """Test InferenceResponse dataclass"""
        response = InferenceResponse(
            document_id="doc-123",
            prediction=0,
            label="business",
            confidence=0.95,
            probabilities=[0.95, 0.02, 0.01, 0.01, 0.01],
            latency_ms=10.5,
            model_version="latest",
            timestamp="2024-01-01T00:00:00Z"
        )
        
        assert response.document_id == "doc-123"
        assert response.prediction == 0
        assert response.label == "business"
        assert response.confidence == 0.95
        assert len(response.probabilities) == 5
        assert response.latency_ms == 10.5