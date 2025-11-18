"""
Databricks AI client wrapper.

Provides a unified interface for interacting with Databricks native AI models
via OpenAI-compatible API with enterprise features: automatic continuation,
smart rate limiting, and response validation.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from rich.console import Console
import click

from .auth import get_auth, setup_auth

console = Console()

# Model-specific token limits based on Databricks OTPM constraints
# Conservative limits to avoid rate limiting and enable reliable continuation
MODEL_MAX_TOKENS = {
    "databricks-claude-sonnet-4-5": 4000,  # OTPM: 5,000 - conservative for reliability
    "databricks-gpt-5": 8000,  # OTPM: 5,000 but can handle bursts
    "databricks-gemini-2-5-pro": 12000,  # OTPM: 20,000 - can handle more
}


class DatabricksClient:
    """
    Client for Databricks AI models using OpenAI-compatible interface.

    Supports:
    - databricks-claude-sonnet-4-5
    - databricks-gpt-5
    - databricks-gemini-2-5-pro
    """

    def __init__(self, model: str = "databricks-claude-sonnet-4-5"):
        """
        Initialize Databricks AI client.

        Args:
            model: The Databricks model to use
        """
        self.model = model
        self._client: Optional[OpenAI] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the OpenAI client with Databricks credentials."""
        auth = get_auth()
        if not auth:
            raise click.ClickException(
                "Databricks authentication not configured. Please run setup first."
            )

        self._client = OpenAI(
            api_key=auth["token"],
            base_url=auth["workspace_url"],
        )

    def _make_request_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_retries: int = 3,
        return_full_response: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Make API request with automatic retry logic and smart rate limit handling.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_retries: Maximum number of retry attempts
            return_full_response: If True, return full response object; if False, return content string
            **kwargs: Additional arguments to pass to the API

        Returns:
            The model's response (content string or full response object based on return_full_response)

        Raises:
            click.ClickException: On authentication or unrecoverable errors
        """
        if not self._client:
            self._initialize_client()

        for attempt in range(max_retries):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                )

                if return_full_response:
                    return response
                else:
                    return response.choices[0].message.content or ""

            except AuthenticationError as e:
                # Authentication failed - token might be expired
                raise click.ClickException(
                    f"Authentication failed: {str(e)}\n"
                    "Your Databricks token may be expired. "
                    "Please run the setup again to configure a new token."
                )

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    # Extract retry_after from error if available
                    retry_after = 30  # Default 30 seconds
                    try:
                        if hasattr(e, 'response') and e.response:
                            retry_after = int(e.response.headers.get('retry-after', 30))
                    except (ValueError, AttributeError):
                        pass

                    console.print(
                        f"[yellow]⏳ Rate limit hit. Waiting {retry_after} seconds... "
                        f"(attempt {attempt + 1}/{max_retries})[/yellow]"
                    )
                    time.sleep(retry_after)
                else:
                    raise click.ClickException(f"Rate limit exceeded after {max_retries} attempts: {str(e)}")

            except APIConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    console.print(
                        f"[yellow]Connection error. Retrying in {wait_time} seconds... "
                        f"(attempt {attempt + 1}/{max_retries})[/yellow]"
                    )
                    time.sleep(wait_time)
                else:
                    raise click.ClickException(f"Connection failed: {str(e)}")

            except APIError as e:
                raise click.ClickException(f"API error: {str(e)}")

            except Exception as e:
                raise click.ClickException(f"Unexpected error: {str(e)}")

        raise click.ClickException("Maximum retries exceeded")

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a chat completion request to Databricks AI.

        Args:
            system_prompt: System message to set context/behavior
            user_message: User's message/query
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            The model's response text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        return self._make_request_with_retry(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def multi_turn_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a multi-turn conversation to Databricks AI.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            The model's response text
        """
        return self._make_request_with_retry(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def chat_with_continuation(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        max_continuations: int = 5,
    ) -> Tuple[str, int]:
        """
        Send a chat completion with automatic continuation for truncated responses.

        This method automatically detects when a response is truncated (finish_reason='length')
        and makes follow-up continuation calls to complete the response.

        Args:
            system_prompt: System message to set context/behavior
            user_message: User's message/query
            max_tokens: Maximum tokens per response chunk (uses model-specific default if None)
            temperature: Sampling temperature (0-1)
            max_continuations: Maximum number of continuation attempts (default: 5)

        Returns:
            Tuple of (complete_response, continuation_count)
        """
        # Use model-specific token limit if not specified
        if max_tokens is None:
            max_tokens = MODEL_MAX_TOKENS.get(self.model, 4000)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        full_response = ""
        continuation_count = 0

        while continuation_count <= max_continuations:
            try:
                # Get full response object to check finish_reason
                response = self._make_request_with_retry(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    return_full_response=True,
                )

                content = response.choices[0].message.content or ""
                finish_reason = response.choices[0].finish_reason

                full_response += content

                # Check if response is complete
                if finish_reason == "stop":
                    # Natural completion
                    break
                elif finish_reason == "length":
                    # Hit token limit - need to continue
                    if continuation_count >= max_continuations:
                        console.print(
                            f"[yellow]⚠️  Response may be incomplete after {max_continuations} continuations[/yellow]"
                        )
                        break

                    continuation_count += 1
                    console.print(
                        f"[cyan]📝 Response truncated. Continuing... (part {continuation_count + 1})[/cyan]"
                    )

                    # Add assistant's response and continuation request
                    messages.append({"role": "assistant", "content": content})
                    messages.append({
                        "role": "user",
                        "content": "Please continue from where you left off. Do not repeat previous content."
                    })

                    # Brief pause to respect rate limits
                    time.sleep(2)
                else:
                    # Other finish reasons (content_filter, etc.) - stop
                    break

            except Exception as e:
                console.print(f"[red]Error during continuation {continuation_count}: {e}[/red]")
                break

        return full_response, continuation_count

    def validate_connection(self) -> bool:
        """
        Validate that the client can connect to Databricks AI.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.chat(
                system_prompt="You are a helpful assistant.",
                user_message="Say 'OK' if you can read this.",
                max_tokens=10,
            )
            return "ok" in response.lower()
        except Exception:
            return False
