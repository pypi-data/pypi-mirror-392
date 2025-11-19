from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Iterable, Mapping

from apexdevkit.formatter import DataclassFormatter, Formatter
from apexdevkit.http import FluentHttp, JsonDict

from apexauthlib.entities import User
from apexauthlib.entities.auth import ItemT, ServicePermission, ServiceUserInfo
from apexauthlib.integration.formatter import ServicePermissionFormatter


@dataclass(frozen=True)
class AuthApiProvider(Generic[ItemT]):
    http: FluentHttp
    service_name: str
    formatter: Formatter[Mapping[str, Any], ItemT]

    def login(self, username: str, password: str) -> str:
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "string",
            "client_secret": "string",
        }

        return str(
            (
                self.http.with_data(JsonDict(data))
                .post()
                .on_endpoint("/auth/login")
                .on_failure(raises=RuntimeError)
                .json()
            )["access_token"]
        )

    def for_token(self, token: str) -> AuthApi[ItemT]:
        return AuthApi(self.http, self.service_name, self.formatter, token)


@dataclass(frozen=True)
class AuthApi(Generic[ItemT]):
    http: FluentHttp
    service_name: str
    formatter: Formatter[Mapping[str, Any], ItemT]
    token: str

    user_formatter: Formatter[Mapping[str, Any], User] = field(
        default_factory=lambda: DataclassFormatter(User)
    )

    def user(self) -> User:
        return DataclassFormatter(User).load(
            (
                self.http.with_header("Authorization", f"Bearer {self.token}")
                .get()
                .on_endpoint("/auth/user")
                .on_failure(raises=RuntimeError)
                .json()
            )
        )

    def metadata_for(self, user_id: str) -> ItemT:
        result = JsonDict(
            (
                self.http.with_header("Authorization", f"Bearer {self.token}")
                .get()
                .on_endpoint(f"/services/{self.service_name}/metadata/{user_id}")
                .on_failure(raises=RuntimeError)
                .json()
            )
        )

        return self.formatter.load(JsonDict(result["data"]["metadata"]["metadata"]))

    def full_metadata_for(self, user_id: str) -> ServiceUserInfo[ItemT]:
        result = JsonDict(
            (
                self.http.with_header("Authorization", f"Bearer {self.token}")
                .get()
                .on_endpoint(f"/services/{self.service_name}/users/{user_id}")
                .on_failure(raises=RuntimeError)
                .json()
            )
        )["data"]["user"]

        user = dict(result["user"])
        user["hashed_password"] = "unknown"

        return ServiceUserInfo[ItemT](
            user=self.user_formatter.load(user),
            is_service_admin=bool(result["is_service_admin"]),
            metadata=self.formatter.load(result["metadata"]),
        )

    def users_for_service(self) -> Iterable[ServiceUserInfo[ItemT]]:
        result = list(
            JsonDict(
                (
                    self.http.with_header("Authorization", f"Bearer {self.token}")
                    .get()
                    .on_endpoint(f"/services/{self.service_name}/users")
                    .on_failure(raises=RuntimeError)
                    .json()
                )
            )["data"]["users"]
        )

        for raw_user in result:
            user = dict(raw_user["user"])
            user["hashed_password"] = "unknown"

            yield ServiceUserInfo[ItemT](
                user=self.user_formatter.load(user),
                is_service_admin=bool(raw_user["is_service_admin"]),
                metadata=self.formatter.load(raw_user["metadata"]),
            )

    def update_permissions(
        self, permissions: list[ServicePermission]
    ) -> list[ServicePermission]:
        existing = {
            permission.name: permission
            for permission in self._retrieve_existing_permissions()
        }
        new = {new_permission.name: new_permission for new_permission in permissions}

        for current, current_permission in existing.items():
            if current not in new.keys():
                self._delete_permission(current_permission.id)

        for current, current_permission in new.items():
            if current not in existing.keys():
                self._create_permission(current_permission)

        return self._retrieve_existing_permissions()

    def _retrieve_existing_permissions(self) -> list[ServicePermission]:
        existing = list(
            JsonDict(
                (
                    self.http.with_header("Authorization", f"Bearer {self.token}")
                    .get()
                    .on_endpoint(f"/services/{self.service_name}/permissions")
                    .on_failure(raises=RuntimeError)
                    .json()
                )
            )["data"]["permissions"]
        )

        return [ServicePermissionFormatter().load(item) for item in existing]

    def _delete_permission(self, permission_id: str) -> None:
        (
            self.http.with_header("Authorization", f"Bearer {self.token}")
            .delete()
            .on_endpoint(f"/services/{self.service_name}/permissions/{permission_id}")
            .on_failure(raises=RuntimeError)
            .json()
        )

    def _create_permission(self, permission: ServicePermission) -> None:
        (
            self.http.with_header("Authorization", f"Bearer {self.token}")
            .with_json(JsonDict(ServicePermissionFormatter().dump(permission)))
            .post()
            .on_endpoint(f"/services/{self.service_name}/permissions")
            .on_failure(raises=RuntimeError)
            .json()
        )


@dataclass
class AuthCodeApi:
    http: FluentHttp
    client_id: str
    client_secret: str

    def token_for(self, code: str) -> str:
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        return str(
            (
                self.http.with_data(JsonDict(data))
                .post()
                .on_endpoint("/auth/oauth/token")
                .on_failure(raises=RuntimeError)
                .json()
            )["access_token"]
        )
