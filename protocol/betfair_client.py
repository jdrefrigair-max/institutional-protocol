"""Betfair API client – login and market price fetch."""

import os
from dotenv import load_dotenv
import betfairlightweight
from betfairlightweight import filters

load_dotenv()

USERNAME = os.getenv("BETFAIR_USERNAME")
PASSWORD = os.getenv("BETFAIR_PASSWORD")
APP_KEY = os.getenv("BETFAIR_APP_KEY")


def get_client():
    if not all([USERNAME, PASSWORD, APP_KEY]):
        raise ValueError("Missing Betfair credentials in .env")
    client = betfairlightweight.APIClient(
        username=USERNAME,
        password=PASSWORD,
        app_key=APP_KEY,
    )
    client.login()
    return client


def get_aus_horse_markets(client, max_results: int = 40):
    market_filter = filters.market_filter(
        event_type_ids=["7"],
        market_countries=["AU"],
        market_type_codes=["WIN"],
    )
    catalogues = client.betting.list_market_catalogue(
        filter=market_filter,
        market_projection=["EVENT", "MARKET_START_TIME", "RUNNER_DESCRIPTION"],
        max_results=max_results,
        sort="FIRST_TO_START",
    )
    markets = []
    for m in catalogues:
        markets.append({
            "market_id": m.market_id,
            "market_name": m.market_name,
            "event_name": m.event.name if m.event else "",
            "venue": m.event.venue if m.event else "",
            "start_time": str(m.market_start_time) if m.market_start_time else "",
            "runners": [
                {"selection_id": r.selection_id, "name": r.runner_name}
                for r in (m.runners or [])
            ],
        })
    return markets


def get_market_prices(client, market_id: str) -> dict:
    books = client.betting.list_market_book(
        market_ids=[market_id],
        price_projection=filters.price_projection(
            price_data=["EX_BEST_OFFERS"]
        ),
    )
    if not books:
        return {}
    book = books[0]
    prices = {}
    for runner in book.runners:
        best_back = None
        if runner.ex and runner.ex.available_to_back:
            best_back = runner.ex.available_to_back[0].price
        if best_back:
            prices[runner.selection_id] = round(best_back, 2)
    return prices