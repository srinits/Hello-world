"""Hotel search tool abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import HotelOption, TravelRequest
from ..providers import HotelProvider, InMemoryHotelProvider


@dataclass
class HotelSearchTool:
    """Fetch hotel recommendations for a travel request."""

    provider: HotelProvider = field(default_factory=InMemoryHotelProvider)

    def search_best_option(self, request: TravelRequest) -> HotelOption:
        """Return the top-ranked hotel option for the itinerary."""
        options = self.provider.search_hotels(
            destination=request.destination,
            check_in=request.departure_date,
            check_out=request.return_date,
            travelers=request.travelers,
            preferences=request.preferences,
        )
        if not options:
            raise ValueError("No hotels available for the given travel request.")
        return options[0]

    def search_all(self, request: TravelRequest) -> list[HotelOption]:
        """Return the ranked hotel options."""
        return self.provider.search_hotels(
            destination=request.destination,
            check_in=request.departure_date,
            check_out=request.return_date,
            travelers=request.travelers,
            preferences=request.preferences,
        )
