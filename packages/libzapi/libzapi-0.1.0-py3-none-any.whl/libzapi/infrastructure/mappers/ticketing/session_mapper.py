from libzapi.infrastructure.serialization.cattrs_converter import get_converter
from libzapi.domain.models.ticketing.sessions import Session


def to_domain(data: dict) -> Session:
    return get_converter().structure(data, Session)
