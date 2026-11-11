import os
import time
import logging
from typing import Any, Optional
from dotenv import load_dotenv

import openai
from langchain_openai import ChatOpenAI

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 2.0
BACKOFF_FACTOR = 2.0


def get_llm(
    model: Optional[str] = None,
    temperature: float = DEFAULT_TEMPERATURE,
    **kwargs: Any,
) -> ChatOpenAI:
    """
    Returns a centralized ChatOpenAI instance configured for OpenRouter.

    Args:
        model: Model name. If None, uses OPENROUTER_MODEL env var or default free model.
        temperature: Sampling temperature (default: 0.3).
        **kwargs: Additional parameters passed to ChatOpenAI.

    Raises:
        ValueError: If OPENROUTER_API_KEY is not configured.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set. Please configure OPENROUTER_API_KEY in your .env file."
        )

    selected_model = model or os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)

    return ChatOpenAI(
        model=selected_model,
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
        **kwargs,
    )


def invoke_with_retry(
    chain_or_llm: Any,
    input_data: Any,
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = INITIAL_RETRY_DELAY,
    backoff_factor: float = BACKOFF_FACTOR,
) -> str:
    """
    Invokes a LangChain chain or LLM with exponential backoff retry for HTTP 429
    rate limits and transient provider errors. Respects Retry-After headers if present.

    Fails immediately with actionable error messages on authentication (401),
    credit/payment (402), or model-not-found (404) errors without silent fallbacks.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            result = chain_or_llm.invoke(input_data)
            # Handle response objects or raw string output
            if hasattr(result, "content"):
                return str(result.content).strip()
            return str(result).strip()

        except Exception as e:
            last_exception = e
            status_code = getattr(e, "status_code", None)

            # 1. HTTP 401 - Authentication Error (Do NOT retry)
            if status_code == 401 or isinstance(e, openai.AuthenticationError):
                error_msg = (
                    "OpenRouter Authentication Error (HTTP 401): Invalid or missing OPENROUTER_API_KEY. "
                    "Please check your API key in the .env file."
                )
                print(f"[Error] {error_msg}")
                raise PermissionError(error_msg) from e

            # 2. HTTP 402 - Payment / Insufficient Credits (Do NOT retry)
            if status_code == 402 or "402" in str(e):
                error_msg = (
                    "OpenRouter Payment / Credit Error (HTTP 402): Account credit balance is exhausted "
                    "or free tier quota limit reached. Please check your OpenRouter account."
                )
                print(f"[Error] {error_msg}")
                raise RuntimeError(error_msg) from e

            # 3. HTTP 404 - Model Not Found (Do NOT retry)
            if status_code == 404 or isinstance(e, openai.NotFoundError):
                current_model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
                error_msg = (
                    f"OpenRouter Model Not Found (HTTP 404): The model '{current_model}' "
                    "was not found or is currently unavailable. Please verify OPENROUTER_MODEL in your .env file."
                )
                print(f"[Error] {error_msg}")
                raise RuntimeError(error_msg) from e

            # 4. HTTP 429 - Rate Limit (Exponential backoff retry with Retry-After header support)
            is_rate_limit = (
                status_code == 429
                or isinstance(e, openai.RateLimitError)
                or "429" in str(e)
                or "rate limit" in str(e).lower()
            )

            if is_rate_limit:
                if attempt < max_retries:
                    # Check if OpenRouter provided a Retry-After header
                    wait_time = delay
                    response_obj = getattr(e, "response", None)
                    if response_obj and hasattr(response_obj, "headers"):
                        retry_after = response_obj.headers.get("retry-after")
                        if retry_after:
                            try:
                                wait_time = max(float(retry_after), 1.0)
                            except (ValueError, TypeError):
                                pass

                    print(
                        f"[Warning] OpenRouter rate limit (HTTP 429) hit. "
                        f"Retrying in {wait_time:.1f}s... (Attempt {attempt}/{max_retries})"
                    )
                    time.sleep(wait_time)
                    delay *= backoff_factor
                    continue
                else:
                    error_msg = (
                        f"OpenRouter rate limit (HTTP 429) exceeded after {max_retries} attempts. "
                        f"Please wait before sending more requests. Details: {e}"
                    )
                    print(f"[Error] {error_msg}")
                    raise RuntimeError(error_msg) from e

            # 5. HTTP 5xx or Connection/Timeout Errors (Transient provider errors: retry with backoff)
            is_transient = (
                (status_code and 500 <= status_code < 600)
                or isinstance(e, (openai.InternalServerError, openai.APIConnectionError, openai.APITimeoutError))
                or "timeout" in str(e).lower()
                or "connection" in str(e).lower()
            )

            if is_transient and attempt < max_retries:
                print(
                    f"[Warning] Transient provider/network error ({e}). "
                    f"Retrying in {delay:.1f}s... (Attempt {attempt}/{max_retries})"
                )
                time.sleep(delay)
                delay *= backoff_factor
                continue

            # Non-retryable or fatal error
            error_msg = f"OpenRouter API call failed: {e}"
            print(f"[Error] {error_msg}")
            raise RuntimeError(error_msg) from e

    raise RuntimeError(
        f"Failed to execute LLM request after {max_retries} attempts: {last_exception}"
    )
