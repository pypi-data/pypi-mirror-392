from libzapi.infrastructure.serialization.cattrs_converter import get_converter
from libzapi.domain.models.ticketing.support_address import RecipientAddress


def to_domain(data: dict) -> RecipientAddress:
    return get_converter().structure(data, RecipientAddress)
