from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_serializer

from .rbac import Role


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class SessionEnvelope(BaseModel):
    session_token: str = Field(alias="sessionToken")
    user_id: str = Field(alias="userId")
    organization_id: str = Field(alias="organizationId")
    role: Role
    expires_at: datetime = Field(alias="expiresAt")

    model_config = {
        "populate_by_name": True,
    }

    @field_serializer("role")
    def serialize_role(self, value: Role) -> str:
        return value.value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    organization_name: str = Field(alias="organizationName", min_length=1)
    organization_slug: str = Field(alias="organizationSlug", min_length=1)

    model_config = {"populate_by_name": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    organization_id: str | None = Field(default=None, alias="organizationId")

    model_config = {"populate_by_name": True}


class MagicLinkRequest(BaseModel):
    email: EmailStr
    organization_id: str | None = Field(default=None, alias="organizationId")

    model_config = {"populate_by_name": True}


class MagicLinkResponse(BaseModel):
    token: str
    expires_at: datetime = Field(alias="expiresAt")
    organization_id: str = Field(alias="organizationId")

    model_config = {"populate_by_name": True}


class MagicLinkVerifyRequest(BaseModel):
    token: str


class InvitationCreateRequest(BaseModel):
    email: EmailStr
    role: Role


class InvitationResponse(BaseModel):
    token: str
    email: EmailStr
    role: Role
    expires_at: datetime = Field(alias="expiresAt")
    organization_id: str = Field(alias="organizationId")

    model_config = {"populate_by_name": True}


class InvitationAcceptRequest(BaseModel):
    token: str
    email: EmailStr
    password: str = Field(min_length=8)


class SwitchOrganisationRequest(BaseModel):
    organization_id: str = Field(alias="organizationId")

    model_config = {"populate_by_name": True}
