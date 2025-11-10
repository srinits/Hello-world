# Travel Planning AI Agent

This project provides a modular, Python-based AI travel planner capable of stitching together flight, hotel, weather, and activity insights into a coherent itinerary. It pairs deterministic sample data sources with an optional large language model (LLM) to enrich day-by-day plans.

## Highlights
- **Composable tools** for flights, hotels, activities, and weather, all behind clean interfaces.
- **Sample in-memory providers** for offline experimentation, with clear seams for real API integration.
- **Optional LLM orchestration** for itinerary storytelling (ships with a mock LLM for local runs).
- **JSON-friendly outputs** ready for downstream automation or UI rendering.

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

> The package ships without third-party dependencies. If you want to swap in the OpenAI Chat API, install `openai` and set `OPENAI_API_KEY`.

### Generate an Itinerary via CLI

```bash
python3 -m travel_agent.cli \
  --origin JFK \
  --destination CDG \
  --departure-date 2025-05-01 \
  --return-date 2025-05-05 \
  --travelers 2 \
  --interests food,museums \
  --travel-style balanced
```

The command prints a structured JSON itinerary that includes flights, hotel, daily activities, weather snapshots, and a budget breakdown.

### Embed in Python Code

```python
from datetime import date

from travel_agent import TravelAgent, TravelPreferences, TravelRequest

request = TravelRequest(
    origin="SFO",
    destination="NRT",
    departure_date=date(2025, 10, 3),
    return_date=date(2025, 10, 10),
    travelers=2,
    preferences=TravelPreferences(
        interests=["culture", "food"],
        travel_style="packed",
    ),
)

agent = TravelAgent()  # optionally pass a custom LLM or data providers
itinerary = agent.plan_trip(request)
print(itinerary.as_dict())
```

## Architecture Overview
- `travel_agent/models.py` — core dataclasses for requests, options, daily plans, and serialization helpers.
- `travel_agent/tools/` — thin façades over the data providers, enforcing a consistent interface.
- `travel_agent/providers/` — base provider contracts plus in-memory sample implementations.
- `travel_agent/agent.py` — orchestrates all tools, fills budgets, and enriches plans with (optional) LLM context.
- `travel_agent/cli.py` — convenience CLI for generating JSON itineraries.

Swap the sample providers with real integrations to connect the agent to production data sources. Introduce your own `BaseLLM` implementation to control itinerary narratives.