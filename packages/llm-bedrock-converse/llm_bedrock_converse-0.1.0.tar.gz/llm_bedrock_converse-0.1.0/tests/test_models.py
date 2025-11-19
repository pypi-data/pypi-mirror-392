import pytest
import json
from unittest.mock import MagicMock, Mock
import llm_bedrock_converse


@pytest.fixture
def mock_bedrock_client(mocker):
    """Mock boto3 bedrock-runtime client"""
    mock_session = mocker.patch('boto3.Session')
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client
    mock_session.return_value.get_credentials.return_value = MagicMock()
    return mock_client


@pytest.fixture
def mock_prompt():
    """Mock llm.Prompt object"""
    prompt = Mock()
    prompt.prompt = "Hello"
    prompt.system = None
    prompt.attachments = []
    prompt.tools = []
    return prompt


@pytest.fixture
def mock_response():
    """Mock llm.Response object"""
    response = Mock()
    response.set_usage = Mock()
    return response


def test_model_registration():
    """Test that models are registered correctly"""
    models = []
    def register(model, aliases=None):
        models.append((model.model_id, aliases))
    
    llm_bedrock_converse.register_models(register)
    assert len(models) > 0
    assert any('claude-3-haiku' in model_id for model_id, _ in models)


def test_basic_converse(mock_bedrock_client, mock_prompt, mock_response):
    """Test basic non-streaming conversation"""
    mock_bedrock_client.converse.return_value = {
        'output': {'message': {'content': [{'text': 'Hello!'}]}},
        'usage': {'inputTokens': 10, 'outputTokens': 5}
    }
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    result = list(model.execute(mock_prompt, False, mock_response, None))
    
    assert result == ['Hello!']
    mock_response.set_usage.assert_called_once_with(input=10, output=5)


def test_streaming_converse(mock_bedrock_client, mock_prompt, mock_response):
    """Test streaming conversation"""
    mock_bedrock_client.converse_stream.return_value = {
        'stream': [
            {'contentBlockDelta': {'delta': {'text': 'Hello'}}},
            {'contentBlockDelta': {'delta': {'text': ' world'}}},
            {'messageStop': {'stopReason': 'end_turn'}},
            {'metadata': {'usage': {'inputTokens': 10, 'outputTokens': 5}}}
        ]
    }
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    result = list(model.execute(mock_prompt, True, mock_response, None))
    
    assert result == ['Hello', ' world']
    mock_response.set_usage.assert_called_once_with(input=10, output=5)


def test_tool_calling(mock_bedrock_client, mock_prompt, mock_response):
    """Test tool calling functionality"""
    mock_tool = Mock()
    mock_tool.name = "test_tool"
    mock_tool.description = "A test tool"
    mock_tool.input_schema = {"type": "object", "properties": {}}
    mock_tool.implementation = Mock(return_value="tool result")
    
    mock_prompt.tools = [mock_tool]
    
    # First call returns tool use
    mock_bedrock_client.converse.side_effect = [
        {
            'output': {
                'message': {
                    'content': [
                        {'toolUse': {'toolUseId': '123', 'name': 'test_tool', 'input': {}}}
                    ]
                }
            },
            'usage': {'inputTokens': 10, 'outputTokens': 5}
        },
        # Second call returns final response
        {
            'output': {'message': {'content': [{'text': 'Final response'}]}},
            'usage': {'inputTokens': 15, 'outputTokens': 10}
        }
    ]
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    result = list(model.execute(mock_prompt, False, mock_response, None))
    
    assert result == ['Final response']
    mock_tool.implementation.assert_called_once()


def test_retry_on_throttling(mock_bedrock_client, mock_prompt, mock_response, mocker):
    """Test retry logic on throttling"""
    from botocore.exceptions import ClientError
    
    mocker.patch('time.sleep')  # Speed up test
    
    # First call throttles, second succeeds
    mock_bedrock_client.converse.side_effect = [
        ClientError(
            {'Error': {'Code': 'ThrottlingException'}},
            'converse'
        ),
        {
            'output': {'message': {'content': [{'text': 'Success'}]}},
            'usage': {'inputTokens': 10, 'outputTokens': 5}
        }
    ]
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    result = list(model.execute(mock_prompt, False, mock_response, None))
    
    assert result == ['Success']
    assert mock_bedrock_client.converse.call_count == 2


def test_attachment_handling(mock_bedrock_client, mock_prompt, mock_response):
    """Test image/PDF/video attachment handling"""
    mock_attachment = Mock()
    mock_attachment.type = "image/png"
    mock_attachment.content_bytes = Mock(return_value=b"fake_image_data")
    mock_attachment.path = None
    
    mock_prompt.attachments = [mock_attachment]
    
    mock_bedrock_client.converse.return_value = {
        'output': {'message': {'content': [{'text': 'I see the image'}]}},
        'usage': {'inputTokens': 100, 'outputTokens': 20}
    }
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    result = list(model.execute(mock_prompt, False, mock_response, None))
    
    assert result == ['I see the image']
    
    # Verify the content structure includes image
    call_args = mock_bedrock_client.converse.call_args
    messages = call_args.kwargs['messages']
    content = messages[0]['content']
    
    assert any('image' in block for block in content)


@pytest.mark.parametrize("model_id,alias", [
    ("anthropic.claude-3-haiku-20240307-v1:0", "bc-haiku"),
    ("anthropic.claude-3-5-sonnet-20240620-v1:0", "bc-sonnet-3.5"),
    ("anthropic.claude-3-opus-20240229-v1:0", "bc-opus"),
])
def test_model_variants(model_id, alias):
    """Test different model variants are configured correctly"""
    model = llm_bedrock_converse.BedrockConverseModel(model_id, True)
    assert model.model_id == model_id
    assert model.can_stream
    assert model.supports_tools
