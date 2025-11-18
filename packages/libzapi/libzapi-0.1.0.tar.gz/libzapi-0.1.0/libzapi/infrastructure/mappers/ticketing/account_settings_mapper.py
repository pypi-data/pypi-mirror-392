from libzapi.infrastructure.serialization.cattrs_converter import get_converter
from libzapi.domain.models.ticketing.account_settings import Settings


def to_domain(data: dict) -> Settings:
    return get_converter().structure(data, Settings)
