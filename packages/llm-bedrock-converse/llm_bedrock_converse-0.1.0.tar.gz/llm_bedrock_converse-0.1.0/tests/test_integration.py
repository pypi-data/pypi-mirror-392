import pytest
from unittest.mock import Mock
import llm_bedrock_converse


def test_conversation_history(mocker):
    """Test conversation with history"""
    mock_session = mocker.patch('boto3.Session')
    mock_client = Mock()
    mock_session.return_value.client.return_value = mock_client
    mock_session.return_value.get_credentials.return_value = Mock()
    
    mock_client.converse.return_value = {
        'output': {'message': {'content': [{'text': 'Response'}]}},
        'usage': {'inputTokens': 20, 'outputTokens': 10}
    }
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    # Create conversation with history
    mock_conversation = Mock()
    mock_prev_response = Mock()
    mock_prev_prompt = Mock()
    mock_prev_prompt.prompt = "Previous question"
    mock_prev_prompt.system = None
    mock_prev_prompt.attachments = []
    mock_prev_response.prompt = mock_prev_prompt
    mock_prev_response.text_or_raise = Mock(return_value="Previous answer")
    mock_conversation.responses = [mock_prev_response]
    
    mock_prompt = Mock()
    mock_prompt.prompt = "Follow-up question"
    mock_prompt.system = None
    mock_prompt.attachments = []
    mock_prompt.tools = []
    
    mock_response = Mock()
    
    result = list(model.execute(mock_prompt, False, mock_response, mock_conversation))
    
    assert result == ['Response']
    
    # Verify conversation history was included
    call_args = mock_client.converse.call_args
    messages = call_args.kwargs['messages']
    assert len(messages) == 3  # prev user, prev assistant, current user


def test_system_prompt(mocker):
    """Test system prompt handling"""
    mock_session = mocker.patch('boto3.Session')
    mock_client = Mock()
    mock_session.return_value.client.return_value = mock_client
    mock_session.return_value.get_credentials.return_value = Mock()
    
    mock_client.converse.return_value = {
        'output': {'message': {'content': [{'text': 'Response'}]}},
        'usage': {'inputTokens': 20, 'outputTokens': 10}
    }
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    mock_prompt = Mock()
    mock_prompt.prompt = "Question"
    mock_prompt.system = "You are a helpful assistant"
    mock_prompt.attachments = []
    mock_prompt.tools = []
    
    mock_response = Mock()
    
    list(model.execute(mock_prompt, False, mock_response, None))
    
    # Verify system prompt was included
    call_args = mock_client.converse.call_args
    assert 'system' in call_args.kwargs
    assert call_args.kwargs['system'][0]['text'] == "You are a helpful assistant"


def test_multiple_attachments(mocker):
    """Test handling multiple attachments"""
    mock_session = mocker.patch('boto3.Session')
    mock_client = Mock()
    mock_session.return_value.client.return_value = mock_client
    mock_session.return_value.get_credentials.return_value = Mock()
    
    mock_client.converse.return_value = {
        'output': {'message': {'content': [{'text': 'I see both'}]}},
        'usage': {'inputTokens': 200, 'outputTokens': 20}
    }
    
    model = llm_bedrock_converse.BedrockConverseModel(
        "anthropic.claude-3-haiku-20240307-v1:0", True
    )
    
    mock_image = Mock()
    mock_image.type = "image/jpeg"
    mock_image.content_bytes = Mock(return_value=b"image_data")
    mock_image.path = None
    
    mock_pdf = Mock()
    mock_pdf.type = "application/pdf"
    mock_pdf.content_bytes = Mock(return_value=b"pdf_data")
    mock_pdf.path = "document.pdf"
    
    mock_prompt = Mock()
    mock_prompt.prompt = "Analyze these"
    mock_prompt.system = None
    mock_prompt.attachments = [mock_image, mock_pdf]
    mock_prompt.tools = []
    
    mock_response = Mock()
    
    result = list(model.execute(mock_prompt, False, mock_response, None))
    
    assert result == ['I see both']
    
    # Verify both attachments in content
    call_args = mock_client.converse.call_args
    content = call_args.kwargs['messages'][0]['content']
    assert any('image' in block for block in content)
    assert any('document' in block for block in content)
