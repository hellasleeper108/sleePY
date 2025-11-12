"""
AI Provider abstraction layer for Mentor AI

Supports multiple LLM providers with easy swapping:
- Ollama (local, open-source)
- OpenAI (GPT-3.5/GPT-4)
- Anthropic Claude
- Custom providers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import os
import json
import httpx
from enum import Enum


class AIProvider(str, Enum):
    """Available AI providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"
    MOCK = "mock"  # For testing


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate completion from LLM

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            system_prompt: Optional system prompt

        Returns:
            str: Generated text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider for local LLM inference

    Requires Ollama running locally: ollama serve
    Default model: codellama or llama2
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate completion using Ollama"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Build messages
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                # Call Ollama API
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "")
                else:
                    return f"Error: Ollama returned status {response.status_code}"

        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except:
            return False


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider (GPT-3.5/GPT-4)

    Requires OPENAI_API_KEY environment variable
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate completion using OpenAI"""
        if not self.api_key:
            return "Error: OpenAI API key not configured"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"Error: OpenAI returned status {response.status_code}"

        except Exception as e:
            return f"Error connecting to OpenAI: {str(e)}"

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.api_key)


class ClaudeProvider(BaseLLMProvider):
    """
    Anthropic Claude provider

    Requires ANTHROPIC_API_KEY environment variable
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate completion using Claude"""
        if not self.api_key:
            return "Error: Anthropic API key not configured"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}]
                }

                if system_prompt:
                    payload["system"] = system_prompt

                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["content"][0]["text"]
                else:
                    return f"Error: Claude returned status {response.status_code}"

        except Exception as e:
            return f"Error connecting to Claude: {str(e)}"

    def is_available(self) -> bool:
        """Check if Claude API key is configured"""
        return bool(self.api_key)


class MockProvider(BaseLLMProvider):
    """Mock provider for testing without real LLM"""

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Return mock hint"""
        return (
            "Here's a hint to help you solve this challenge:\n\n"
            "1. Start by understanding what the function should return\n"
            "2. Think about the edge cases you need to handle\n"
            "3. Break down the problem into smaller steps\n\n"
            "You're on the right track! Keep trying!"
        )

    def is_available(self) -> bool:
        """Mock is always available"""
        return True


class LLMProviderFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create_provider(provider_type: AIProvider = AIProvider.OLLAMA) -> BaseLLMProvider:
        """
        Create LLM provider instance

        Args:
            provider_type: Type of provider to create

        Returns:
            BaseLLMProvider: Provider instance

        Raises:
            ValueError: If provider type is invalid
        """
        if provider_type == AIProvider.OLLAMA:
            return OllamaProvider()
        elif provider_type == AIProvider.OPENAI:
            return OpenAIProvider()
        elif provider_type == AIProvider.CLAUDE:
            return ClaudeProvider()
        elif provider_type == AIProvider.MOCK:
            return MockProvider()
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    @staticmethod
    def get_available_provider() -> BaseLLMProvider:
        """
        Get first available provider in order of preference:
        1. Ollama (local)
        2. OpenAI
        3. Claude
        4. Mock (fallback)

        Returns:
            BaseLLMProvider: First available provider
        """
        providers = [
            (AIProvider.OLLAMA, OllamaProvider()),
            (AIProvider.OPENAI, OpenAIProvider()),
            (AIProvider.CLAUDE, ClaudeProvider()),
            (AIProvider.MOCK, MockProvider()),
        ]

        for provider_type, provider in providers:
            if provider.is_available():
                print(f"Using AI provider: {provider_type}")
                return provider

        # Fallback to mock
        return MockProvider()
