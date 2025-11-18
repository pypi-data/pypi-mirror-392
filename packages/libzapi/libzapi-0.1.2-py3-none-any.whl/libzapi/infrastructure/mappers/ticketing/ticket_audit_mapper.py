from libzapi.domain.models.ticketing.ticket_audit import TicketAudit
from libzapi.domain.shared_objects.via import Via
from libzapi.infrastructure.utils.datetime_utils import parse_dt


def to_domain(data: dict) -> TicketAudit:
    return TicketAudit(
        id=data["id"],
        author_id=data["author_id"],
        created_at=parse_dt(data["created_at"]),
        events=data["events"],
        metadata=data["metadata"],
        ticket_id=data["ticket_id"],
        via=Via(channel=data["via"]["channel"], source=data["via"]["source"], rel=data["via"]["rel"]),
    )
