from libzapi.domain.models.ticketing.brand import Brand
from libzapi.infrastructure.serialization.cattrs_converter import get_converter


def to_domain(data: dict) -> Brand:
    return get_converter().structure(data, Brand)
