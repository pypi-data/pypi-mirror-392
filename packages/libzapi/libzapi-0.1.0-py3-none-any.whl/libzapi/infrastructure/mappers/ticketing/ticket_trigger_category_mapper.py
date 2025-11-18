from libzapi.domain.models.ticketing.ticket_trigger_category import TicketTriggerCategory
from libzapi.infrastructure.serialization.cattrs_converter import get_converter


def to_domain(data: dict) -> TicketTriggerCategory:
    return get_converter().structure(data, TicketTriggerCategory)
