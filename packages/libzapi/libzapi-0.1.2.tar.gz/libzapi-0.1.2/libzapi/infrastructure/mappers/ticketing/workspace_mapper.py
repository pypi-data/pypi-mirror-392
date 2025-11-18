from libzapi.domain.shared_objects.condition import Condition
from libzapi.infrastructure.utils.datetime_utils import parse_dt
from libzapi.domain.models.ticketing.workspace import Workspace, App, AllAnyCondition, SelectedMacro


def to_domain(data: dict) -> Workspace:
    return Workspace(
        id=int(data["id"]),
        url=data["url"],
        title=data["title"],
        description=data.get("description", ""),
        macro_ids=[int(mid) for mid in data.get("macro_ids", [])],
        ticket_form_id=int(data["ticket_form_id"]) if data.get("ticket_form_id") else None,
        layout_uuid=data.get("layout_uuid"),
        apps=[App(app["id"], app.get("expand", False), app.get("position", 0)) for app in data.get("apps")],
        position=int(data.get("position", 0)),
        activated=bool(data.get("activated", False)),
        conditions=AllAnyCondition(
            all=[
                Condition(field=cond["field"], operator=cond["operator"], value=cond["value"])
                for cond in data.get("conditions", {}).get("all", [])
            ],
            any=[
                Condition(field=cond["field"], operator=cond["operator"], value=cond["value"])
                for cond in data.get("conditions", {}).get("any", [])
            ],
        ),
        updated_at=parse_dt(data["updated_at"]),
        created_at=parse_dt(data["created_at"]),
        knowledge_settings=data.get("knowledge_settings", {}),  # type: ignore
        selected_macros=[
            SelectedMacro(
                id=macro["id"],
                title=macro["title"],
                active=macro["active"],
                usage_7d=macro["usage_7d"],
                restriction=macro["restriction"],
            )
            for macro in data.get("selected_macros", [])
        ],
    )
