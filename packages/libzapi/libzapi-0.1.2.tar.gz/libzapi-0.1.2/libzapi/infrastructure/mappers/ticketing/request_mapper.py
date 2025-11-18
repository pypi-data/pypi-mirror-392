from libzapi.infrastructure.utils.datetime_utils import parse_dt
from libzapi.domain.models.ticketing.request import Request


def to_domain(data: dict) -> Request:
    return Request(
        id=int(data["id"]),
        subject=data["subject"],
        description=data["description"],
        status=data["status"],
        priority=data.get("priority"),
        requester_id=int(data["requester_id"]),
        assignee_id=int(data["assignee_id"]) if data.get("assignee_id") else None,
        created_at=parse_dt(data["created_at"]),
        updated_at=parse_dt(data["updated_at"]),
        due_at=parse_dt(data["due_at"]) if data.get("due_at") else None,
        ticket_form_id=int(data["ticket_form_id"]) if data.get("ticket_form_id") else None,
        type=data.get("type"),
        url=data["url"],
        can_be_solved_by_me=bool(data["can_be_solved_by_me"]),
        collaborator_ids=[int(cid) for cid in data.get("collaborator_ids", [])],
        custom_fields=data.get("custom_fields", []),
        custom_status_id=int(data["custom_status_id"]) if data.get("custom_status_id") else None,
        email_cc_ids=[int(eid) for eid in data.get("email_cc_ids", [])],
        followup_source_id=int(data["followup_source_id"]) if data.get("followup_source_id") else None,
        group_id=int(data["group_id"]) if data.get("group_id") else None,
        is_public=bool(data["is_public"]),
        organization_id=int(data["organization_id"]) if data.get("organization_id") else None,
        recipient=data.get("recipient"),
        solved=bool(data["solved"]),
        via=data["via"],
    )
