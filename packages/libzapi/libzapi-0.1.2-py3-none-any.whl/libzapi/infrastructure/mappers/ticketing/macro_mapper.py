from libzapi.domain.models.ticketing.macro import Macro
from libzapi.infrastructure.serialization.cattrs_converter import get_converter


def to_domain(data: dict) -> Macro:
    return get_converter().structure(data, Macro)
