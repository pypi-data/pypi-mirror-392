from libzapi.domain.models.ticketing.ticket_trigger import TicketTrigger
from libzapi.infrastructure.serialization.cattrs_converter import get_converter


def to_domain(data: dict) -> TicketTrigger:
    return get_converter().structure(data, TicketTrigger)
