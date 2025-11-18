from libzapi.infrastructure.utils.datetime_utils import parse_dt
from libzapi.domain.models.ticketing.group import Group
from libzapi.application.commands.ticketing.group_cmds import CreateGroupCmd, UpdateGroupCmd


def to_domain(data: dict) -> Group:
    return Group(
        id=int(data["id"]),
        name=data["name"],
        description=data.get("description", ""),
        is_public=bool(data.get("is_public", True)),
        default=bool(data.get("default", False)),
        deleted=bool(data.get("deleted", False)),
        url=data["url"],
        created_at=parse_dt(data.get("created_at")),
        updated_at=parse_dt(data.get("updated_at")),
    )


def to_payload_create(cmd: CreateGroupCmd) -> dict:
    return {
        "group": {
            "name": cmd.name,
            "description": cmd.description,
            "is_public": cmd.is_public,
            "default": cmd.default,
        }
    }


def to_payload_update(cmd: UpdateGroupCmd) -> dict:
    patch = {}
    if cmd.name is not None:
        patch["name"] = cmd.name
    if cmd.description is not None:
        patch["description"] = cmd.description
    if cmd.is_public is not None:
        patch["is_public"] = cmd.is_public
    if cmd.default is not None:
        patch["default"] = cmd.default
    return {"group": patch}
