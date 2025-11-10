"""Activity suggestion tool."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import DefaultDict, Dict, Iterable, List

from ..models import ActivityOption, TravelRequest
from ..providers import ActivityProvider, InMemoryActivityProvider


@dataclass
class ActivityTool:
    """Return activity ideas keyed by travel date."""

    provider: ActivityProvider = field(default_factory=InMemoryActivityProvider)

    def fetch_by_day(self, request: TravelRequest) -> Dict[date, List[ActivityOption]]:
        """Return suggested activities grouped by itinerary day."""
        start = request.departure_date
        end = request.return_date
        interests = request.preferences.interests or []
        style = request.preferences.travel_style or "balanced"

        grouped: DefaultDict[date, List[ActivityOption]] = defaultdict(list)
        for activity in self.provider.get_activities(
            destination=request.destination,
            start_date=start,
            end_date=end,
            interests=interests,
            travel_style=style,
        ):
            if activity.start_time:
                grouped[activity.start_time.date()].append(activity)
            else:
                grouped[start].append(activity)

        return dict(grouped)

    def fetch_all(self, request: TravelRequest) -> Iterable[ActivityOption]:
        """Return all activities without grouping."""
        return self.provider.get_activities(
            destination=request.destination,
            start_date=request.departure_date,
            end_date=request.return_date,
            interests=request.preferences.interests or [],
            travel_style=request.preferences.travel_style or "balanced",
        )
