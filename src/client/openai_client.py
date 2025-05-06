from dataclasses import dataclass
from typing import List, Dict, Optional

from openai import OpenAI
from openai.types.chat import ChatCompletion


@dataclass
class OpenAIClient:
    api_key: str
    model: str
    client: OpenAI

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        openai_model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ChatCompletion:
        """
        Send a chat completion request to OpenAI API.

        Args:
            messages: List of message objects with 'role' and 'content' fields
            temperature: Controls randomness (0-1)
            openai_model: OpenAIModel name
            max_tokens: Maximum number of tokens to generate

        Returns:
            Full API response as a dictionary
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens
        response = self.client.chat.completions.create(
            model=openai_model or self.model,
            messages=messages,
        )
        return response

    async def get_chat_response(
        self, messages: list[dict[str, str]], openai_model: str, temperature: float = 0.7,
    ) -> str:
        """
        Get just the response text from a chat completion.

        Args:
            messages: List of message objects with 'role' and 'content' fields
            temperature: Controls randomness (0-1)
            openai_model: str

        Returns:
            The assistant's response as a string
        """
        response = await self.chat_completion(messages, openai_model, temperature)

        try:
            return response.choices[0].message.content
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected API response format: {e}")
