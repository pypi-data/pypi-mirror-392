import pytest
import json
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import llm_bedrock_converse


@pytest.fixture
def mock_bedrock_client(mocker):
    """Mock boto3 bedrock-runtime client"""
    mock_client = MagicMock()
    mocker.patch('boto3.client', return_value=mock_client)
    return mock_client


def test_embedding_registration():
    """Test that embedding models are registered"""
    models = []
    def register(model):
        models.append(model)
    
    llm_bedrock_converse.register_embedding_models(register)
    assert len(models) == 2
    assert any('titan-v2' in m.model_name for m in models)
    assert any('titan-v1' in m.model_name for m in models)


def test_basic_embedding(mock_bedrock_client, mocker):
    """Test basic embedding generation"""
    mocker.patch('time.time', side_effect=[0, 0.7])
    mocker.patch('time.sleep')
    
    mock_response = MagicMock()
    mock_response['body'].read.return_value = json.dumps({
        'embedding': [0.1, 0.2, 0.3]
    }).encode()
    
    mock_bedrock_client.invoke_model.return_value = mock_response
    
    model = llm_bedrock_converse.BedrockTitanEmbedding(
        "amazon.titan-embed-text-v2:0", "titan-v2"
    )
    
    result = model.embed("test text")
    
    assert result == [0.1, 0.2, 0.3]
    mock_bedrock_client.invoke_model.assert_called_once()


def test_embedding_rate_limiting(mock_bedrock_client, mocker):
    """Test rate limiting for embeddings"""
    mock_time = mocker.patch('time.time')
    mock_sleep = mocker.patch('time.sleep')
    
    # Simulate rapid calls
    mock_time.side_effect = [0, 0.3, 0.3, 1.0]
    
    mock_response = MagicMock()
    mock_response['body'].read.return_value = json.dumps({
        'embedding': [0.1, 0.2]
    }).encode()
    
    mock_bedrock_client.invoke_model.return_value = mock_response
    
    model = llm_bedrock_converse.BedrockTitanEmbedding(
        "amazon.titan-embed-text-v2:0", "titan-v2"
    )
    
    model.embed("text1")
    model.embed("text2")
    
    # Should have slept to enforce rate limit
    mock_sleep.assert_called()


def test_embedding_retry_on_throttle(mock_bedrock_client, mocker):
    """Test retry logic on throttling"""
    mocker.patch('time.time', return_value=0)
    mocker.patch('time.sleep')
    
    mock_response = MagicMock()
    mock_response['body'].read.return_value = json.dumps({
        'embedding': [0.1, 0.2]
    }).encode()
    
    # First call throttles, second succeeds
    mock_bedrock_client.invoke_model.side_effect = [
        ClientError(
            {'Error': {'Code': 'ThrottlingException'}},
            'invoke_model'
        ),
        mock_response
    ]
    
    model = llm_bedrock_converse.BedrockTitanEmbedding(
        "amazon.titan-embed-text-v2:0", "titan-v2"
    )
    
    result = model.embed("test")
    
    assert result == [0.1, 0.2]
    assert mock_bedrock_client.invoke_model.call_count == 2


def test_embedding_batch(mock_bedrock_client, mocker):
    """Test batch embedding"""
    mocker.patch('time.time', return_value=0)
    mocker.patch('time.sleep')
    
    mock_response = MagicMock()
    mock_response['body'].read.return_value = json.dumps({
        'embedding': [0.1, 0.2]
    }).encode()
    
    mock_bedrock_client.invoke_model.return_value = mock_response
    
    model = llm_bedrock_converse.BedrockTitanEmbedding(
        "amazon.titan-embed-text-v2:0", "titan-v2"
    )
    
    results = model.embed_batch(["text1", "text2", "text3"])
    
    assert len(results) == 3
    assert all(r == [0.1, 0.2] for r in results)
