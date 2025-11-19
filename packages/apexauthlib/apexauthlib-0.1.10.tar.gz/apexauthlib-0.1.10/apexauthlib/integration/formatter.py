from dataclasses import dataclass
from typing import Any, Mapping

from apexauthlib.entities.auth import FieldType, ServicePermission


@dataclass(frozen=True)
class ServicePermissionFormatter:
    def dump(self, permission: ServicePermission) -> Mapping[str, Any]:
        raw = {
            "name": permission.name,
            "description": permission.description,
            "label": permission.label,
            "type": permission.type.value,
            "values": permission.values,
            "default": permission.default,
        }

        if permission.id.isdigit():
            raw["id"] = permission.id

        return raw

    def load(self, raw: Mapping[str, Any]) -> ServicePermission:
        permission_type = FieldType[str(raw["type"])]

        return ServicePermission(
            id=str(raw["id"]),
            name=str(raw["name"]),
            label=str(raw["label"]),
            description=str(raw["description"]),
            type=permission_type,
            values=self._load_combos(permission_type, raw),
            default=self._load_default(permission_type, raw),
        )

    def _load_combos(
        self, permission_type: FieldType, raw: Mapping[str, Any]
    ) -> list[str] | list[int]:
        if permission_type == FieldType.boolean:
            return []
        if permission_type == FieldType.string:
            return [str(item) for item in list(raw["values"])]
        if permission_type == FieldType.integer:
            return [int(item) for item in list(raw["values"])]

        raise ValueError(f"Unexpected type: {permission_type}")

    def _load_default(
        self, permission_type: FieldType, raw: Mapping[str, Any]
    ) -> str | int | bool:
        if permission_type == FieldType.string:
            return str(raw["default"])
        if permission_type == FieldType.integer:
            return int(raw["default"])
        if permission_type == FieldType.boolean:
            return bool(raw["default"])
        raise ValueError(f"Unexpected type: {permission_type}")
