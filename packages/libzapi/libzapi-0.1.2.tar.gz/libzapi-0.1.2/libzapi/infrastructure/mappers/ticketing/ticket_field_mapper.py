from libzapi.domain.models.ticketing.ticket_field import TicketField


def to_domain(data: dict) -> TicketField:
    return TicketField(
        id=data["id"],
        title=data["title"],
        type=data["type"],
        required=bool(data.get("required", False)),
    )


def to_payload(entity: TicketField) -> dict:
    """Convert domain model back to Zendesk's JSON shape."""
    return {
        "ticket_field": {
            "title": entity.title,
            "type": entity.type,
            "required": entity.required,
        }
    }
