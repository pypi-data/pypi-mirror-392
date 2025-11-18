from libzapi.infrastructure.mappers.shared_mappers.field_definition_mapper import (
    field_definition_mapper,
    short_field_definition_mapper,
)
from libzapi.infrastructure.utils.datetime_utils import parse_dt
from libzapi.domain.models.ticketing.view import View, Execution


def to_domain(data: dict) -> View:
    return View(
        id=int(data["id"]),
        url=data["url"],
        title=data["title"],
        active=data["active"],
        default=data["default"],
        position=data["position"],
        raw_title=data["raw_title"],
        description=data["description"],
        execution=Execution(
            group_by=data["execution"]["group_by_id"],
            group_order=data["execution"]["group_order"],
            sort_by=data["execution"]["sort_by"],
            sort_order=data["execution"]["sort_order"],
            group=field_definition_mapper(data["execution"]["group"]),
            sort=field_definition_mapper(data["execution"]["sort"]),
            columns=[field_definition_mapper(column) for column in data["execution"]["columns"]],
            fields=[short_field_definition_mapper(field) for field in data["execution"]["fields"]],
            custom_fields=[
                field_definition_mapper(custom_field) for custom_field in data["execution"]["custom_fields"]
            ],
        ),
        conditions=data["conditions"],
        restriction=data.get("restriction"),
        created_at=parse_dt(data["created_at"]),
        updated_at=parse_dt(data["updated_at"]),
    )
