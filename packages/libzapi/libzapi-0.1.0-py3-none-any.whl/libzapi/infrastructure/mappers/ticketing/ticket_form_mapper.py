from libzapi.infrastructure.utils.datetime_utils import parse_dt
from libzapi.domain.models.ticketing.ticket_form import TicketForm


def to_domain(data: dict) -> TicketForm:
    return TicketForm(
        id=int(data["id"]),
        raw_name=data["raw_name"],
        raw_display_name=data["raw_display_name"],
        end_user_visible=bool(data["end_user_visible"]),
        position=int(data["position"]),
        ticket_field_ids=[int(fid) for fid in data.get("ticket_field_ids", [])],
        active=bool(data["active"]),
        default=bool(data["default"]),
        in_all_brands=bool(data["in_all_brands"]),
        restricted_brand_ids=[int(bid) for bid in data.get("restricted_brand_ids", [])],
        end_user_conditions=data.get("end_user_conditions", []),
        agent_conditions=data.get("agent_conditions", []),
        url=data["url"],
        name=data["name"],
        display_name=data["display_name"],
        created_at=parse_dt(data["created_at"]),
        updated_at=parse_dt(data["updated_at"]),
        deleted_at=parse_dt(data["deleted_at"]) if data.get("deleted_at") else None,
    )
