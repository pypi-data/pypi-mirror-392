from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config

from ..core.base import BaseChat, BaseEmbedding


class BedrockChat(BaseChat):
    """AWS Bedrock Chat implementation supporting Claude models."""
    
    def __init__(
        self,
        *,
        model: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        region_name: str = "us-east-1",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: float = 300.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            region_name=region_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        
        config = Config(
            read_timeout=timeout,
            connect_timeout=timeout,
            retries={'max_attempts': 3}
        )
        
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name,
            config=config
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to Bedrock and get response."""
        
        # 转换消息格式为 Claude 格式
        system_prompt = ""
        claude_messages = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                claude_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                claude_messages.append({"role": "assistant", "content": content})
        
        # 构建请求体
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": claude_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        
        if system_prompt:
            body["system"] = system_prompt
        
        try:
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            # 提取内容
            content = response_body.get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "")
            
            return ""
            
        except Exception as e:
            raise RuntimeError(f"Bedrock API error: {str(e)}")


class BedrockEmbedding(BaseEmbedding):
    """AWS Bedrock Embedding implementation using Titan Embeddings."""
    
    def __init__(
        self,
        *,
        model: str = "amazon.titan-embed-text-v1",
        region_name: str = "us-east-1",
        timeout: float = 300.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            region_name=region_name,
            timeout=timeout,
        )
        
        config = Config(
            read_timeout=timeout,
            connect_timeout=timeout,
            retries={'max_attempts': 3}
        )
        
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name,
            config=config
        )
        self.model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts using Bedrock Titan."""
        embeddings = []
        
        for text in texts:
            body = json.dumps({
                "inputText": text,
            })
            
            try:
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=body,
                    contentType="application/json",
                    accept="application/json"
                )
                
                response_body = json.loads(response['body'].read())
                embedding = response_body.get("embedding", [])
                embeddings.append(embedding)
                
            except Exception as e:
                raise RuntimeError(f"Bedrock Embedding error: {str(e)}")
        
        return embeddings
