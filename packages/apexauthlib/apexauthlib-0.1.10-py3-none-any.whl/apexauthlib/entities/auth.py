from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

ItemT = TypeVar("ItemT")


@dataclass(frozen=True)
class User:
    username: str
    hashed_password: str
    first_name: str
    last_name: str
    email: str
    phone_number: str

    is_admin: bool

    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Service:
    service: str
    admins: list[str]


@dataclass(frozen=True)
class ServiceMetadata:
    user_id: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class UserMetadata:
    service: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Client:
    client_id: str
    hashed_secret: str


@dataclass(frozen=True)
class ServiceUserInfo(Generic[ItemT]):
    user: User
    is_service_admin: bool
    metadata: ItemT


@dataclass(frozen=True)
class ServicePermission:
    name: str
    label: str
    description: str
    type: FieldType
    default: str | int | bool

    values: list[str] | list[int] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


class FieldType(str, Enum):
    string = "string"
    integer = "integer"
    boolean = "boolean"

    def valid_type(self) -> type:
        if self.value == FieldType.string:
            return str
        if self.value == FieldType.integer:
            return int
        if self.value == FieldType.boolean:
            return bool
        raise ValueError(f"Invalid type {self.value}")
