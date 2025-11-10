"""Weather forecasting tool wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import TravelRequest, WeatherSnapshot
from ..providers import InMemoryWeatherProvider, WeatherProvider


@dataclass
class WeatherTool:
    """Retrieve weather snapshots for travel days."""

    provider: WeatherProvider = field(default_factory=InMemoryWeatherProvider)

    def fetch_forecast(self, request: TravelRequest) -> list[WeatherSnapshot]:
        return self.provider.get_forecast(
            destination=request.destination,
            start_date=request.departure_date,
            end_date=request.return_date,
        )
