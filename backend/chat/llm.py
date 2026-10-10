import logging

from django.conf import settings
from groq import APIConnectionError, APIError, APITimeoutError, Groq, RateLimitError

logger = logging.getLogger(__name__)


class ChatNotConfigured(Exception):
    pass


class ChatBusy(Exception):
    pass


class ChatUnavailable(Exception):
    pass


def generate_reply(system_prompt: str, messages: list[dict]) -> str:
    """Call Groq lazily so an empty local API key never breaks Django startup."""
    if not settings.GROQ_API_KEY:
        raise ChatNotConfigured
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{'role': 'system', 'content': system_prompt}, *messages],
            max_tokens=settings.CHAT_MAX_TOKENS,
            temperature=settings.CHAT_TEMPERATURE,
            timeout=20,
        )
        return response.choices[0].message.content.strip()
    except RateLimitError as exc:
        logger.warning('Groq error: %s', type(exc).__name__)
        raise ChatBusy from exc
    except (APITimeoutError, APIConnectionError, APIError) as exc:
        logger.warning('Groq error: %s', type(exc).__name__)
        raise ChatUnavailable from exc
    except Exception as exc:
        logger.warning('Groq error: %s', type(exc).__name__)
        raise ChatUnavailable from exc
