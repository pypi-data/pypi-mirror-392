from libzapi.domain.models.ticketing.ticket_metric import TicketMetric
from libzapi.infrastructure.utils.datetime_utils import parse_dt


def to_domain(data: dict) -> TicketMetric:
    return TicketMetric(
        id=data["id"],
        ticket_id=data["ticket_id"],
        agent_wait_time_in_minutes=data["agent_wait_time_in_minutes"],
        requester_wait_time_in_minutes=data["requester_wait_time_in_minutes"],
        on_hold_time_in_minutes=data["on_hold_time_in_minutes"],
        first_resolution_time_in_minutes=data["first_resolution_time_in_minutes"],
        full_resolution_time_in_minutes=data["full_resolution_time_in_minutes"],
        created_at=parse_dt(data["created_at"]),
        updated_at=parse_dt(data["updated_at"]),
        url=data["url"],
        assigned_at=parse_dt(data.get("assigned_at")),
        assignee_stations=data["assignee_stations"],
        assignee_update_at=parse_dt(data.get("assignee_update_at")),
        custom_status_update_at=parse_dt(data["custom_status_update_at"]),
        group_stations=data["group_stations"],
        initially_assigned_at=parse_dt(data.get("initially_assigned_at")),
        latest_comment_added_at=parse_dt(data.get("latest_comment_added_at")),
        reopens=data["reopens"],
        replies=data["replies"],
        reply_time_in_minutes=data["reply_time_in_minutes"],
        reply_time_in_seconds=data["reply_time_in_seconds"],
        request_updated_at=data["request_updated_at"],
        solved_at=parse_dt(data.get("solved_at")),
        status_updated_at=parse_dt(data.get("status_updated_at")),
    )
