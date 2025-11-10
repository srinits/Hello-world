"""Base provider interfaces for external travel data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable, List, Sequence

from ..models import (
    ActivityOption,
    FlightItinerary,
    HotelOption,
    TravelPreferences,
    WeatherSnapshot,
)


class FlightProvider(ABC):
    """Abstract provider for flight search."""

    @abstractmethod
    def search_round_trip(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        travelers: int,
        preferences: TravelPreferences,
    ) -> tuple[FlightItinerary, FlightItinerary]:
        """Return the best outbound and return itineraries."""


class HotelProvider(ABC):
    """Abstract provider for hotel search."""

    @abstractmethod
    def search_hotels(
        self,
        destination: str,
        check_in: date,
        check_out: date,
        travelers: int,
        preferences: TravelPreferences,
    ) -> List[HotelOption]:
        """Return hotel options sorted by relevance."""


class ActivityProvider(ABC):
    """Abstract provider for local experiences."""

    @abstractmethod
    def get_activities(
        self,
        destination: str,
        start_date: date,
        end_date: date,
        interests: Sequence[str],
        travel_style: str,
    ) -> Iterable[ActivityOption]:
        """Yield relevant activities in the date range."""


class WeatherProvider(ABC):
    """Abstract provider for weather forecasts."""

    @abstractmethod
    def get_forecast(self, destination: str, start_date: date, end_date: date) -> List[WeatherSnapshot]:
        """Return daily weather snapshots."""
