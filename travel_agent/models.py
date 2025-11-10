"""Core data models for the travel planning agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Sequence


@dataclass(slots=True)
class TravelPreferences:
    """Traveler preferences that guide itinerary construction."""

    budget_per_person: Optional[float] = None
    preferred_airlines: Optional[Sequence[str]] = None
    hotel_star_rating: Optional[int] = None
    cuisine_preferences: Optional[Sequence[str]] = None
    interests: Optional[Sequence[str]] = None
    travel_style: Optional[str] = None  # e.g. "adventure", "relaxation"
    pace: str = "balanced"  # one of {"relaxed", "balanced", "packed"}
    notes: Optional[str] = None


@dataclass(slots=True)
class TravelRequest:
    """Structured request containing the travel brief for the agent."""

    origin: str
    destination: str
    departure_date: date
    return_date: date
    travelers: int
    preferences: TravelPreferences = field(default_factory=TravelPreferences)


@dataclass(slots=True)
class FlightSegment:
    """A single flight segment within an itinerary."""

    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int


@dataclass(slots=True)
class FlightItinerary:
    """Flight itinerary including one or more segments."""

    segments: List[FlightSegment]
    price: float
    currency: str
    cabin_class: str
    baggage_allowance: Optional[str] = None
    booking_url: Optional[str] = None

    @property
    def total_duration_minutes(self) -> int:
        return sum(segment.duration_minutes for segment in self.segments)


@dataclass(slots=True)
class HotelOption:
    """Accommodation recommendation."""

    name: str
    check_in: date
    check_out: date
    price_per_night: float
    currency: str
    star_rating: Optional[float] = None
    amenities: Sequence[str] = field(default_factory=list)
    booking_url: Optional[str] = None

    @property
    def total_price(self) -> float:
        nights = (self.check_out - self.check_in).days
        return nights * self.price_per_night


@dataclass(slots=True)
class ActivityOption:
    """Activity or experience suggestion."""

    name: str
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    estimated_cost: Optional[float] = None
    currency: Optional[str] = None
    booking_url: Optional[str] = None


@dataclass(slots=True)
class WeatherSnapshot:
    """Weather summary for a specific day."""

    date: date
    summary: str
    high_celsius: float
    low_celsius: float
    precipitation_chance: float  # 0-1 range


@dataclass(slots=True)
class ItineraryDay:
    """Daily breakdown of activities."""

    date: date
    theme: Optional[str] = None
    weather: Optional[WeatherSnapshot] = None
    activities: List[ActivityOption] = field(default_factory=list)

    def add_activity(self, activity: ActivityOption) -> None:
        self.activities.append(activity)


@dataclass(slots=True)
class BudgetBreakdown:
    """Cost summary across major categories."""

    flights: float = 0.0
    lodging: float = 0.0
    activities: float = 0.0
    meals: float = 0.0
    transportation: float = 0.0
    currency: str = "USD"

    @property
    def total(self) -> float:
        return self.flights + self.lodging + self.activities + self.meals + self.transportation


@dataclass(slots=True)
class Itinerary:
    """Complete travel plan assembled by the agent."""

    request: TravelRequest
    outbound_flight: Optional[FlightItinerary] = None
    return_flight: Optional[FlightItinerary] = None
    hotel: Optional[HotelOption] = None
    days: List[ItineraryDay] = field(default_factory=list)
    budget: BudgetBreakdown = field(default_factory=BudgetBreakdown)
    notes: Dict[str, str] = field(default_factory=dict)

    def add_day(self, day: ItineraryDay) -> None:
        self.days.append(day)

    def as_dict(self) -> Dict[str, object]:
        """Serialize the itinerary into a JSON-friendly dictionary."""
        return {
            "request": {
                "origin": self.request.origin,
                "destination": self.request.destination,
                "departure_date": self.request.departure_date.isoformat(),
                "return_date": self.request.return_date.isoformat(),
                "travelers": self.request.travelers,
                "preferences": asdict(self.request.preferences),
            },
            "flights": {
                "outbound": serialize_flight(self.outbound_flight),
                "return": serialize_flight(self.return_flight),
            },
            "hotel": serialize_hotel(self.hotel),
            "days": [serialize_day(day) for day in self.days],
            "budget": {
                "flights": self.budget.flights,
                "lodging": self.budget.lodging,
                "activities": self.budget.activities,
                "meals": self.budget.meals,
                "transportation": self.budget.transportation,
                "currency": self.budget.currency,
                "total": self.budget.total,
            },
            "notes": self.notes,
        }


def serialize_day(day: Optional[ItineraryDay]) -> Optional[Dict[str, object]]:
    if not day:
        return None

    return {
        "date": day.date.isoformat(),
        "theme": day.theme,
        "weather": serialize_weather(day.weather),
        "activities": [serialize_activity(activity) for activity in day.activities],
    }


def serialize_activity(activity: Optional[ActivityOption]) -> Optional[Dict[str, object]]:
    if not activity:
        return None

    return {
        "name": activity.name,
        "description": activity.description,
        "start_time": activity.start_time.isoformat() if activity.start_time else None,
        "end_time": activity.end_time.isoformat() if activity.end_time else None,
        "location": activity.location,
        "category": activity.category,
        "estimated_cost": activity.estimated_cost,
        "currency": activity.currency,
        "booking_url": activity.booking_url,
    }


def serialize_weather(weather: Optional[WeatherSnapshot]) -> Optional[Dict[str, object]]:
    if not weather:
        return None
    return {
        "summary": weather.summary,
        "date": weather.date.isoformat(),
        "high_celsius": weather.high_celsius,
        "low_celsius": weather.low_celsius,
        "precipitation_chance": weather.precipitation_chance,
    }


def serialize_flight(flight: Optional[FlightItinerary]) -> Optional[Dict[str, object]]:
    if not flight:
        return None
    return {
        "segments": [
            {
                "flight_number": segment.flight_number,
                "airline": segment.airline,
                "departure_airport": segment.departure_airport,
                "arrival_airport": segment.arrival_airport,
                "departure_time": segment.departure_time.isoformat(),
                "arrival_time": segment.arrival_time.isoformat(),
                "duration_minutes": segment.duration_minutes,
            }
            for segment in flight.segments
        ],
        "price": flight.price,
        "currency": flight.currency,
        "cabin_class": flight.cabin_class,
        "baggage_allowance": flight.baggage_allowance,
        "booking_url": flight.booking_url,
    }


def serialize_hotel(hotel: Optional[HotelOption]) -> Optional[Dict[str, object]]:
    if not hotel:
        return None
    return {
        "name": hotel.name,
        "check_in": hotel.check_in.isoformat(),
        "check_out": hotel.check_out.isoformat(),
        "price_per_night": hotel.price_per_night,
        "currency": hotel.currency,
        "star_rating": hotel.star_rating,
        "amenities": list(hotel.amenities),
        "booking_url": hotel.booking_url,
        "total_price": hotel.total_price,
    }
