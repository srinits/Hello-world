"""High-level orchestration for building a travel plan."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

from .llm import BaseLLM, MockLLM, build_outline_prompt
from .models import Itinerary, ItineraryDay, TravelRequest
from .tools import ActivityTool, FlightSearchTool, HotelSearchTool, WeatherTool


@dataclass
class TravelAgent:
     """Coordinates multiple tools and optionally an LLM to craft itineraries."""

     llm: Optional[BaseLLM] = None
     flight_tool: FlightSearchTool = field(default_factory=FlightSearchTool)
     hotel_tool: HotelSearchTool = field(default_factory=HotelSearchTool)
     activity_tool: ActivityTool = field(default_factory=ActivityTool)
     weather_tool: WeatherTool = field(default_factory=WeatherTool)

     def plan_trip(self, request: TravelRequest) -> Itinerary:
         """Generate a structured itinerary satisfying the travel request."""
         self._validate_request(request)

         outbound, inbound = self.flight_tool.search_best_round_trip(request)
         hotel = self.hotel_tool.search_best_option(request)
         activities_by_day = self.activity_tool.fetch_by_day(request)
         weather_by_day = {snap.date: snap for snap in self.weather_tool.fetch_forecast(request)}

         itinerary = Itinerary(
             request=request,
             outbound_flight=outbound,
             return_flight=inbound,
             hotel=hotel,
         )

         outline = self._generate_outline(request)
         days_count = (request.return_date - request.departure_date).days

         for idx in range(days_count):
             day_date = request.departure_date + timedelta(days=idx)
             day = ItineraryDay(
                 date=day_date,
                 theme=outline.get(idx + 1),
                 weather=weather_by_day.get(day_date),
             )

             for activity in activities_by_day.get(day_date, []):
                 day.add_activity(activity)

             itinerary.add_day(day)

         self._populate_budget(itinerary)
         itinerary.notes["generated_outline"] = outline
         itinerary.notes["generated_at"] = datetime.utcnow().isoformat()

         return itinerary

     def _validate_request(self, request: TravelRequest) -> None:
         if request.return_date <= request.departure_date:
             raise ValueError("Return date must be after departure date.")
         if request.travelers < 1:
             raise ValueError("At least one traveler is required.")

     def _generate_outline(self, request: TravelRequest) -> Dict[int, str]:
         llm = self.llm or MockLLM()
         days = (request.return_date - request.departure_date).days
         prompt = build_outline_prompt(
             destination=request.destination,
             days=days,
             interests=request.preferences.interests or [],
             travel_style=request.preferences.travel_style,
         )
         try:
             completion = llm.generate(prompt)
         except Exception:  # pragma: no cover - guardrail around external LLMs
             return {}
         return _parse_outline(completion)

     def _populate_budget(self, itinerary: Itinerary) -> None:
         flights_cost = 0.0
         if itinerary.outbound_flight:
             flights_cost += itinerary.outbound_flight.price
         if itinerary.return_flight:
             flights_cost += itinerary.return_flight.price

         itinerary.budget.flights = flights_cost
         if itinerary.hotel:
             itinerary.budget.lodging = itinerary.hotel.total_price

         activity_cost = sum(
             activity.estimated_cost or 0.0
             for day in itinerary.days
             for activity in day.activities
         )
         itinerary.budget.activities = activity_cost

         meals_cost = 40.0 * itinerary.request.travelers * len(itinerary.days)
         itinerary.budget.meals = meals_cost
         itinerary.budget.transportation = 25.0 * itinerary.request.travelers * len(itinerary.days)


def _parse_outline(outline_text: str) -> Dict[int, str]:
    """Parse a bullet-style outline into a day index -> summary mapping."""
    day_pattern = re.compile(r"day\s*(\d+)", re.IGNORECASE)

    summaries: Dict[int, list[str]] = {}
    current_day: Optional[int] = None

    for raw_line in outline_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = day_pattern.search(line)
        if match:
            current_day = int(match.group(1))
            summaries.setdefault(current_day, [])
            content = day_pattern.sub("", line).strip(":- ")
            if content:
                summaries[current_day].append(content)
            continue

        if current_day is not None:
            summaries.setdefault(current_day, []).append(line.strip("- "))

    return {day: "; ".join(parts) for day, parts in summaries.items() if parts}
