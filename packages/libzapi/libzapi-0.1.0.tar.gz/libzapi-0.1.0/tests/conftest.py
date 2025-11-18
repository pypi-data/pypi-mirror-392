import os

import pytest

from libzapi import Ticketing, HelpCenter


@pytest.fixture(scope="session")
def ticketing():
    """Creates a real Ticketing client if environment variables are set."""
    base_url = os.getenv("ZENDESK_URL")
    email = os.getenv("ZENDESK_EMAIL")
    api_token = os.getenv("ZENDESK_TOKEN")

    if not (base_url and email and api_token):
        pytest.skip("Zendesk credentials not provided. Skipping live API tests.")

    return Ticketing(
        base_url=base_url,
        email=email,
        api_token=api_token,
    )


@pytest.fixture(scope="session")
def help_center():
    """Creates a real Help Center client if environment variables are set."""
    base_url = os.getenv("ZENDESK_URL")
    email = os.getenv("ZENDESK_EMAIL")
    api_token = os.getenv("ZENDESK_TOKEN")

    if not (base_url and email and api_token):
        pytest.skip("Zendesk credentials not provided. Skipping live API tests.")

    return HelpCenter(
        base_url=base_url,
        email=email,
        api_token=api_token,
    )
