"""LLM client abstractions used by the travel agent."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, *, temperature: float = 0.2, **kwargs) -> str:
        """Generate a completion for the given prompt."""


class OpenAIChatLLM(BaseLLM):
    """Thin wrapper around the OpenAI Chat Completion API.

    This implementation defers importing the `openai` package until runtime. Users must install
    the official OpenAI Python SDK (>= 1.0) and provide an API key through the `OPENAI_API_KEY`
    environment variable.
    """

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided to use OpenAIChatLLM.")

        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:  # pragma: no cover - import guard
            raise ImportError(
                "The openai package is required for OpenAIChatLLM. Install it with `pip install openai`."
            ) from exc

        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate(self, prompt: str, *, temperature: float = 0.2, **kwargs) -> str:
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            **kwargs,
        )
        return completion.choices[0].message.content or ""


class MockLLM(BaseLLM):
    """Rule-based mock LLM useful for offline testing."""

    def __init__(self, canned_responses: Optional[Dict[str, str]] = None) -> None:
        self._canned = canned_responses or {}

    def generate(self, prompt: str, *, temperature: float = 0.2, **kwargs) -> str:
        for key, response in self._canned.items():
            if key.lower() in prompt.lower():
                return response
        return (
            "Suggested itinerary outline:\n"
            "- Day 1: Arrival, light exploration, local cuisine dinner.\n"
            "- Day 2: Morning city tour, afternoon museum visit, evening show.\n"
            "- Day 3: Day trip to nearby attraction, sunset cruise.\n"
            "- Day 4: Leisure morning, shopping, departure preparations.\n"
        )


def build_outline_prompt(
    *,
    destination: str,
    days: int,
    interests: Iterable[str],
    travel_style: Optional[str] = None,
) -> str:
    """Utility for constructing a deterministic outline prompt."""

    interests_part = ", ".join(interests) if interests else "general sightseeing"
    base_prompt = (
        f"Create a day-by-day travel plan for a {days}-day trip to {destination}. "
        f"Focus on {interests_part} experiences. "
        "Include morning, afternoon, and evening suggestions for each day."
    )

    if travel_style:
        base_prompt += f" The traveler prefers a {travel_style} style."

    base_prompt += " Format the response as bullet points grouped by day."
    return base_prompt
