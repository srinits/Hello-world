"""Command-line entry point for generating a travel plan."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import List

from .agent import TravelAgent
from .models import TravelPreferences, TravelRequest

DATE_FMT = "%Y-%m-%d"


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a sample travel itinerary.")
    parser.add_argument("--origin", required=True, help="Departure airport or city code (e.g. JFK).")
    parser.add_argument("--destination", required=True, help="Destination airport or city code (e.g. CDG).")
    parser.add_argument("--departure-date", required=True, help="Departure date (YYYY-MM-DD).")
    parser.add_argument("--return-date", required=True, help="Return date (YYYY-MM-DD).")
    parser.add_argument("--travelers", type=int, default=2, help="Number of travelers (default: 2).")
    parser.add_argument(
        "--interests",
        default="",
        help="Comma-separated list of interests (e.g. food,museums,nightlife).",
    )
    parser.add_argument(
        "--travel-style",
        default="balanced",
        choices=["relaxed", "balanced", "packed"],
        help="Preferred pace for the trip.",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Approximate budget per person (optional).",
    )
    return parser.parse_args(argv)


def build_request(args: argparse.Namespace) -> TravelRequest:
    departure = datetime.strptime(args.departure_date, DATE_FMT).date()
    return_date = datetime.strptime(args.return_date, DATE_FMT).date()
    interests = [interest.strip() for interest in args.interests.split(",") if interest.strip()]

    preferences = TravelPreferences(
        budget_per_person=args.budget,
        interests=interests,
        travel_style=args.travel_style,
    )

    return TravelRequest(
        origin=args.origin,
        destination=args.destination,
        departure_date=departure,
        return_date=return_date,
        travelers=args.travelers,
        preferences=preferences,
    )


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    request = build_request(args)

    agent = TravelAgent()
    itinerary = agent.plan_trip(request)

    print(json.dumps(itinerary.as_dict(), indent=2))


if __name__ == "__main__":
    main()
