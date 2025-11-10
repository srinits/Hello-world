"""Simple in-memory provider implementations with deterministic sample data."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Iterable, List, Sequence

from ..models import (
    ActivityOption,
    FlightItinerary,
    FlightSegment,
    HotelOption,
    TravelPreferences,
    WeatherSnapshot,
)
from .base import ActivityProvider, FlightProvider, HotelProvider, WeatherProvider


def _make_datetime(trip_date: date, hour: int, minute: int) -> datetime:
    return datetime.combine(trip_date, time(hour=hour, minute=minute))


class InMemoryFlightProvider(FlightProvider):
    """Provides sample flight itineraries without external API calls."""

    def search_round_trip(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        travelers: int,
        preferences: TravelPreferences,
    ) -> tuple[FlightItinerary, FlightItinerary]:
        base_price = 450.0 if preferences.pace != "packed" else 420.0

        outbound_segments = [
            FlightSegment(
                flight_number="AI204",
                airline=preferences.preferred_airlines[0] if preferences.preferred_airlines else "SkyJet",
                departure_airport=origin,
                arrival_airport=destination,
                departure_time=_make_datetime(departure_date, 9, 35),
                arrival_time=_make_datetime(departure_date, 14, 15),
                duration_minutes=280,
            )
        ]

        return_segments = [
            FlightSegment(
                flight_number="AI205",
                airline=outbound_segments[0].airline,
                departure_airport=destination,
                arrival_airport=origin,
                departure_time=_make_datetime(return_date, 16, 10),
                arrival_time=_make_datetime(return_date, 20, 45),
                duration_minutes=275,
            )
        ]

        outbound = FlightItinerary(
            segments=outbound_segments,
            price=base_price * travelers,
            currency="USD",
            cabin_class="Economy",
            baggage_allowance="1 checked bag (23kg), 1 carry-on",
            booking_url="https://example.com/booking/flights/AI204",
        )

        inbound = FlightItinerary(
            segments=return_segments,
            price=base_price * travelers,
            currency="USD",
            cabin_class="Economy",
            baggage_allowance="1 checked bag (23kg), 1 carry-on",
            booking_url="https://example.com/booking/flights/AI205",
        )

        return outbound, inbound


class InMemoryHotelProvider(HotelProvider):
    """Provides sample hotel recommendations."""

    def search_hotels(
        self,
        destination: str,
        check_in: date,
        check_out: date,
        travelers: int,
        preferences: TravelPreferences,
    ) -> List[HotelOption]:
        base_price = 180.0
        if preferences.hotel_star_rating and preferences.hotel_star_rating >= 5:
            base_price = 320.0
        elif preferences.hotel_star_rating and preferences.hotel_star_rating <= 3:
            base_price = 120.0

        hotel = HotelOption(
            name=f"{destination} Grand Hotel",
            check_in=check_in,
            check_out=check_out,
            price_per_night=base_price,
            currency="USD",
            star_rating=float(preferences.hotel_star_rating or 4),
            amenities=[
                "Free Wi-Fi",
                "Breakfast buffet",
                "Rooftop pool",
                "Fitness center",
            ],
            booking_url="https://example.com/booking/hotels/grand",
        )

        # Provide an alternative option with different pricing
        boutique = HotelOption(
            name=f"{destination} Boutique Suites",
            check_in=check_in,
            check_out=check_out,
            price_per_night=base_price * 0.85,
            currency="USD",
            star_rating=4.2,
            amenities=[
                "Complimentary breakfast",
                "Local art decor",
                "Evening wine tasting",
            ],
            booking_url="https://example.com/booking/hotels/boutique",
        )

        return [hotel, boutique]


class InMemoryActivityProvider(ActivityProvider):
    """Provides sample activities tailored to interests."""

    def get_activities(
        self,
        destination: str,
        start_date: date,
        end_date: date,
        interests: Sequence[str],
        travel_style: str,
    ) -> Iterable[ActivityOption]:
        base_cost = 60.0 if travel_style == "relaxed" else 90.0
        days = (end_date - start_date).days or 1
        interest_list = list(interests) or ["city highlights"]

        for offset in range(days):
            activity_date = start_date + timedelta(days=offset)
            yield ActivityOption(
                name=f"{destination} {interest_list[offset % len(interest_list)].title()} Experience",
                description=(
                    f"Guided exploration focused on {interest_list[offset % len(interest_list)]}. "
                    "Includes local insights and skip-the-line access where available."
                ),
                start_time=_make_datetime(activity_date, 10, 0),
                end_time=_make_datetime(activity_date, 13, 0),
                location=destination,
                category=interest_list[offset % len(interest_list)],
                estimated_cost=base_cost + offset * 10,
                currency="USD",
                booking_url="https://example.com/activities/experience",
            )

            yield ActivityOption(
                name=f"Evening Culinary Tour {offset + 1}",
                description="Small-group tasting tour featuring signature dishes and hidden gems.",
                start_time=_make_datetime(activity_date, 18, 30),
                end_time=_make_datetime(activity_date, 21, 0),
                location=destination,
                category="food",
                estimated_cost=base_cost + 25,
                currency="USD",
                booking_url="https://example.com/activities/culinary",
            )


class InMemoryWeatherProvider(WeatherProvider):
    """Provides deterministic weather approximations."""

    def get_forecast(self, destination: str, start_date: date, end_date: date) -> List[WeatherSnapshot]:
        days = (end_date - start_date).days or 1
        forecast: List[WeatherSnapshot] = []
        for offset in range(days):
            day = start_date + timedelta(days=offset)
            high = 25 + (offset % 3)  # simple oscillation
            low = high - 8
            precipitation = 0.1 * ((offset + len(destination)) % 5) / 4
            forecast.append(
                WeatherSnapshot(
                    date=day,
                    summary="Sunny with scattered clouds" if precipitation < 0.3 else "Partly cloudy with light showers",
                    high_celsius=float(high),
                    low_celsius=float(low),
                    precipitation_chance=float(min(precipitation, 0.8)),
                )
            )
        return forecast
