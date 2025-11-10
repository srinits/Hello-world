"""Wrapper around a flight provider with light business logic."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import FlightItinerary, TravelRequest
from ..providers import FlightProvider, InMemoryFlightProvider


@dataclass
class FlightSearchTool:
    """Simple façade for retrieving flight options."""

    provider: FlightProvider = field(default_factory=InMemoryFlightProvider)

    def search_best_round_trip(self, request: TravelRequest) -> tuple[FlightItinerary, FlightItinerary]:
        """Fetch the best outbound and inbound itineraries for the request."""
        outbound, inbound = self.provider.search_round_trip(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            travelers=request.travelers,
            preferences=request.preferences,
        )

        return outbound, inbound
