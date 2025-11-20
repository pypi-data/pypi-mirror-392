from typing import Optional, Type, Union
from pydantic import BaseModel
from openai import OpenAI


class VercelOpenAI:
    """
    Simple wrapper around OpenAI client for Vercel endpoints.
    """

    def __init__(self, api_key: str, base_url: str):
        """
        Initialize Vercel OpenAI client.

        Args:
            api_key (str): Your Vercel OpenAI API key
            base_url (str): Base URL for Vercel OpenAI API
        """
        if not api_key or not base_url:
            raise ValueError("Both api_key and base_url are required")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _build_messages(
        self,
        prompt: str = "",
        chat_history: list = [],
        query: str = "",
    ) -> list:
        messages = []
        if prompt:
            messages.append({"role": "system", "content": prompt})
        if chat_history:
            messages.extend(chat_history.copy())
        if query:
            messages.append({"role": "user", "content": query})
        return messages

    def chat_without_function_call(
        self,
        model: str,
        chat_history: list = [],
        prompt: str = "",
        query: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
    ):
        """
        Call OpenAI chat completion API without function call.
        """
        messages = self._build_messages(prompt=prompt, chat_history=chat_history, query=query)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
        except Exception as e:
            print(f"Error in chat_without_function_call: {e}")
            raise

        answer = response.choices[0].message.content
        return {
            "answer": answer,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "raw": response,
        }

    def structured_output_without_functions(
        self,
        model: str,
        response_format: Union[Type[BaseModel], dict],
        chat_history: list = [],
        prompt: str = "",
        query: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        strict: bool = True,
        **kwargs,
    ):
        """
        Get structured output (Pydantic or JSON schema) from OpenAI.
        """
        messages = self._build_messages(prompt=prompt, chat_history=chat_history, query=query)

        api_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if isinstance(response_format, type) and issubclass(response_format, BaseModel):
            api_params["response_format"] = response_format
            use_pydantic = True
        elif isinstance(response_format, dict):
            api_params["response_format"] = response_format
            use_pydantic = False
        else:
            raise ValueError("response_format must be either a Pydantic BaseModel class or a dict with JSON schema")

        api_params.update(kwargs)

        try:
            if use_pydantic:
                response = self.client.beta.chat.completions.parse(**api_params)
                structured_data = response.choices[0].message.parsed
            else:
                response = self.client.chat.completions.create(**api_params)
                import json
                structured_data = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in structured_output_without_functions: {e}")
            raise

        return {
            "structured_output": structured_data,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "raw": response,
        }
