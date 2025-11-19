import boto3
import llm
import os
import json
import time
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError

# AWS Region configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Model definitions: (model_id, aliases, supports_attachments)
MODELS = (
    # US Inference Profiles (recommended - cross-region routing)
    ("us.anthropic.claude-haiku-4-5-20251001-v1:0", ("bc-haiku-4.5-us", "bc-haiku-us"), True),
    ("us.anthropic.claude-sonnet-4-5-20250929-v1:0", ("bc-sonnet-4.5-us", "bc-sonnet-us"), True),
    ("us.anthropic.claude-3-5-haiku-20241022-v1:0", ("bc-haiku-3.5-us",), True),
    ("us.anthropic.claude-3-5-sonnet-20240620-v1:0", ("bc-sonnet-3.5-us",), True),
    
    # Claude 3 Haiku
    ("anthropic.claude-3-haiku-20240307-v1:0", ("bedrock-converse/claude-3-haiku", "bc-haiku"), True),
    ("anthropic.claude-3-5-haiku-20241022-v1:0", ("bedrock-converse/claude-3.5-haiku", "bc-haiku-3.5"), True),
    ("anthropic.claude-haiku-4-5-20251001-v1:0", ("bedrock-converse/claude-4.5-haiku", "bc-haiku-4.5"), True),
    
    # Claude 3 Sonnet
    ("anthropic.claude-3-sonnet-20240229-v1:0", ("bedrock-converse/claude-3-sonnet", "bc-sonnet"), True),
    ("anthropic.claude-3-5-sonnet-20240620-v1:0", ("bedrock-converse/claude-3.5-sonnet", "bc-sonnet-3.5"), True),
    ("anthropic.claude-3-7-sonnet-20250219-v1:0", ("bedrock-converse/claude-3.7-sonnet", "bc-sonnet-3.7"), True),
    ("anthropic.claude-sonnet-4-20250514-v1:0", ("bedrock-converse/claude-4-sonnet", "bc-sonnet-4"), True),
    ("anthropic.claude-sonnet-4-5-20250929-v1:0", ("bedrock-converse/claude-4.5-sonnet", "bc-sonnet-4.5"), True),
    
    # Claude 3 Opus
    ("anthropic.claude-3-opus-20240229-v1:0", ("bedrock-converse/claude-3-opus", "bc-opus"), True),
    ("anthropic.claude-opus-4-20250514-v1:0", ("bedrock-converse/claude-4-opus", "bc-opus-4"), True),
    ("anthropic.claude-opus-4-1-20250805-v1:0", ("bedrock-converse/claude-4.1-opus", "bc-opus-4.1"), True),
    
    # Cross-region models (us. prefix - older style)
    ("us.anthropic.claude-3-5-sonnet-20241022-v2:0", ("bc-sonnet-3.5-v2",), True),
    
    # Global models (global. prefix)
    ("global.anthropic.claude-sonnet-4-20250514-v1:0", ("bc-sonnet-4-global",), True),
    ("global.anthropic.claude-sonnet-4-5-20250929-v1:0", ("bc-sonnet-4.5-global",), True),
)

FORMAT_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/webp": "webp",
    "image/gif": "gif",
    "application/pdf": "pdf",
    "video/quicktime": "mov",
    "video/x-matroska": "mkv",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/x-flv": "flv",
    "video/mpeg": "mpeg",
    "video/x-ms-wmv": "wmv",
}


@llm.hookimpl
def register_embedding_models(register):
    register(BedrockTitanEmbedding("amazon.titan-embed-text-v2:0", "titan-v2"))
    register(BedrockTitanEmbedding("amazon.titan-embed-text-v1", "titan-v1"))


class BedrockTitanEmbedding(llm.EmbeddingModel):
    needs_key = None
    supports_text = True
    supports_binary = False
    
    def __init__(self, model_id: str, alias: str):
        self.model_id = model_id
        self.model_name = alias
        self._client = None
        self._last_request_time = 0
        self._min_interval = 0.6  # 100 RPM = 0.6s between requests
    
    def _get_client(self):
        if self._client is None:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=AWS_REGION
            )
        return self._client
    
    def _rate_limit(self):
        """Ensure we don't exceed 100 RPM"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _embed_with_retry(self, text: str, max_retries: int = 5) -> List[float]:
        """Embed with exponential backoff and retry-after respect"""
        client = self._get_client()
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                body = json.dumps({"inputText": text})
                response = client.invoke_model(
                    modelId=self.model_id,
                    body=body,
                    contentType="application/json",
                    accept="application/json"
                )
                
                result = json.loads(response['body'].read())
                return result['embedding']
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                
                if error_code == 'ThrottlingException':
                    # Check for retry-after header
                    retry_after = e.response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('retry-after')
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                        wait_time = min(2 ** attempt, 16)
                    
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                
                raise
        
        raise Exception(f"Failed to embed after {max_retries} retries")
    
    def embed(self, text: str) -> List[float]:
        return self._embed_with_retry(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts with rate limiting"""
        return [self.embed(text) for text in texts]


@llm.hookimpl
def register_models(register):
    for model_id, aliases, supports_attachments in MODELS:
        register(
            BedrockConverseModel(model_id, supports_attachments),
            aliases=aliases
        )


class BedrockConverseModel(llm.Model):
    needs_key = "bedrock"
    can_stream = True
    supports_tools = True  # Enable tool support

    def __init__(self, model_id: str, supports_attachments: bool):
        self.model_id = model_id
        if supports_attachments:
            self.attachment_types = {
                "image/png", "image/jpeg", "image/webp", "image/gif",
                "application/pdf",
                "video/quicktime", "video/x-matroska", "video/mp4",
                "video/webm", "video/x-flv", "video/mpeg", "video/x-ms-wmv",
            }

    def _call_bedrock_with_retry(self, bedrock, method_name: str, params: Dict, max_retries: int = 5):
        """Call Bedrock API with exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                method = getattr(bedrock, method_name)
                return method(**params)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                
                if error_code == 'ThrottlingException':
                    if attempt < max_retries - 1:
                        # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                        wait_time = 2 ** attempt
                        
                        # Check if API provided retry-after header
                        retry_after = e.response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('retry-after')
                        if retry_after:
                            try:
                                wait_time = max(wait_time, int(retry_after))
                            except (ValueError, TypeError):
                                pass
                        
                        time.sleep(wait_time)
                        continue
                
                # Re-raise if not throttling or max retries reached
                raise

    def _build_content(self, prompt) -> List[Dict[str, Any]]:
        """Build content array with attachments and text."""
        content = []
        
        # Add attachments
        for attachment in prompt.attachments:
            if attachment.type.startswith("image/"):
                content.append({
                    "image": {
                        "format": FORMAT_TYPES[attachment.type],
                        "source": {"bytes": attachment.content_bytes()},
                    }
                })
            elif attachment.type.startswith("video/"):
                content.append({
                    "video": {
                        "format": FORMAT_TYPES[attachment.type],
                        "source": {"bytes": attachment.content_bytes()},
                    }
                })
            elif attachment.type == "application/pdf":
                name = "attachment"
                if attachment.path:
                    import pathlib
                    name = pathlib.Path(attachment.path).stem
                    name = "".join(c for c in name if c.isalnum()) or "attachment"
                content.append({
                    "document": {
                        "name": name,
                        "format": "pdf",
                        "source": {"bytes": attachment.content_bytes()},
                    }
                })
        
        # Add text
        content.append({"text": prompt.prompt})
        return content

    def _convert_tools_to_bedrock(self, tools: List) -> List[Dict[str, Any]]:
        """Convert llm.Tool objects to Bedrock tool format."""
        bedrock_tools = []
        for tool in tools:
            tool_spec = {
                "toolSpec": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": {
                        "json": tool.input_schema or {"type": "object", "properties": {}}
                    }
                }
            }
            bedrock_tools.append(tool_spec)
        return bedrock_tools

    def execute(self, prompt, stream, response, conversation):
        # Get AWS session
        try:
            key = self.get_key()
            access_key, _, secret_key = key.partition(":")
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
        except llm.errors.NeedsKeyException:
            session = boto3.Session()
            if not session.get_credentials():
                raise llm.errors.NeedsKeyException("No AWS credentials found")

        bedrock = session.client("bedrock-runtime", region_name=AWS_REGION)
        
        # Build messages
        messages = []
        system = prompt.system
        
        if conversation:
            for turn in conversation.responses:
                if not system and turn.prompt.system:
                    system = turn.prompt.system
                messages.append({
                    "role": "user",
                    "content": self._build_content(turn.prompt)
                })
                messages.append({
                    "role": "assistant",
                    "content": [{"text": turn.text_or_raise()}]
                })
        
        messages.append({
            "role": "user",
            "content": self._build_content(prompt)
        })
        
        # Build request params
        params = {
            "modelId": self.model_id,
            "messages": messages,
        }
        
        if system:
            params["system"] = [{"text": system}]
        
        # Add tool configuration if tools are provided
        if prompt.tools:
            tool_config = {
                "tools": self._convert_tools_to_bedrock(prompt.tools)
            }
            params["toolConfig"] = tool_config
        
        # Execute with or without streaming
        if stream:
            yield from self._execute_stream(bedrock, params, response, prompt)
        else:
            yield from self._execute_non_stream(bedrock, params, response, prompt)

    def _execute_stream(self, bedrock, params, response, prompt):
        """Execute streaming request with tool support."""
        bedrock_response = self._call_bedrock_with_retry(bedrock, 'converse_stream', params)
        
        text_chunks = []
        usage = {}
        stop_reason = None
        
        for event in bedrock_response["stream"]:
            event_type, event_content = list(event.items())[0]
            
            if event_type == "contentBlockDelta":
                delta = event_content.get("delta", {})
                if "text" in delta:
                    text = delta["text"]
                    text_chunks.append(text)
                    yield text
            
            elif event_type == "messageStop":
                stop_reason = event_content.get("stopReason")
            
            elif event_type == "metadata":
                if "usage" in event_content:
                    usage = event_content["usage"]
        
        # If model wants to use tools, we need to handle non-streaming
        # because streaming tool use is complex
        if stop_reason == "tool_use":
            # Re-run without streaming to get tool use
            non_stream_response = self._call_bedrock_with_retry(bedrock, 'converse', params)
            output = non_stream_response["output"]["message"]
            content = output["content"]
            
            tool_uses = [block for block in content if "toolUse" in block]
            
            if tool_uses and prompt.tools:
                for tool_use_block in tool_uses:
                    tool_use = tool_use_block["toolUse"]
                    tool_result = self._execute_tool(
                        prompt.tools,
                        tool_use["name"],
                        tool_use["input"]
                    )
                    
                    # Send tool result back
                    params["messages"].append(output)
                    params["messages"].append({
                        "role": "user",
                        "content": [{
                            "toolResult": {
                                "toolUseId": tool_use["toolUseId"],
                                "content": [{"text": tool_result}]
                            }
                        }]
                    })
                    
                    # Get final response (non-streaming for simplicity)
                    final_response = self._call_bedrock_with_retry(bedrock, 'converse', params)
                    final_output = final_response["output"]["message"]
                    
                    for block in final_output["content"]:
                        if "text" in block:
                            yield block["text"]
                    
                    if "usage" in final_response:
                        usage = final_response["usage"]
        
        if usage:
            response.set_usage(
                input=usage.get("inputTokens", 0),
                output=usage.get("outputTokens", 0)
            )

    def _execute_non_stream(self, bedrock, params, response, prompt):
        """Execute non-streaming request with tool support."""
        bedrock_response = self._call_bedrock_with_retry(bedrock, 'converse', params)
        
        output = bedrock_response["output"]["message"]
        content = output["content"]
        
        # Check for tool use
        tool_uses = [block for block in content if "toolUse" in block]
        
        if tool_uses and prompt.tools:
            for tool_use_block in tool_uses:
                tool_use = tool_use_block["toolUse"]
                tool_result = self._execute_tool(
                    prompt.tools,
                    tool_use["name"],
                    tool_use["input"]
                )
                
                # Send tool result back
                params["messages"].append(output)
                params["messages"].append({
                    "role": "user",
                    "content": [{
                        "toolResult": {
                            "toolUseId": tool_use["toolUseId"],
                            "content": [{"text": tool_result}]
                        }
                    }]
                })
                
                # Get final response
                final_response = self._call_bedrock_with_retry(bedrock, 'converse', params)
                output = final_response["output"]["message"]
                content = output["content"]
        
        # Extract text
        for block in content:
            if "text" in block:
                yield block["text"]
        
        # Set usage
        if "usage" in bedrock_response:
            usage = bedrock_response["usage"]
            response.set_usage(
                input=usage.get("inputTokens", 0),
                output=usage.get("outputTokens", 0)
            )

    def _execute_tool(self, tools: List, tool_name: str, tool_input: Dict) -> str:
        """Execute a tool and return the result as JSON string."""
        for tool in tools:
            if tool.name == tool_name:
                try:
                    result = tool.implementation(**tool_input)
                    # Convert result to JSON-serializable format
                    if isinstance(result, (dict, list)):
                        return json.dumps(result)
                    else:
                        return str(result)
                except Exception as e:
                    return json.dumps({"error": str(e)})
        return json.dumps({"error": f"Tool {tool_name} not found"})

    def __str__(self):
        return f"BedrockConverse: {self.model_id}"
