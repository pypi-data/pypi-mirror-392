from libzapi.infrastructure.utils.datetime_utils import parse_dt
from libzapi.domain.models.ticketing.schedule import Schedule, Holiday


def schedule_to_domain(data: dict) -> Schedule:
    return Schedule(
        id=int(data["id"]),
        intervals=data.get("intervals", []),
        name=data["name"],
        time_zone=data["time_zone"],
        created_at=parse_dt(data["created_at"]),
        updated_at=parse_dt(data["updated_at"]),
    )


def holiday_to_domain(data: dict) -> Holiday:
    return Holiday(
        id=int(data["id"]),
        name=data["name"],
        start_date=data["start_date"],
        end_date=data["end_date"],
    )
