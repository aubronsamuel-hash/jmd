from __future__ import annotations

from datetime import date, datetime, time
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


class VenueBase(BaseModel):
    name: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = Field(default=None, alias="postalCode")
    capacity: int | None = None
    notes: str | None = None

    model_config = {"populate_by_name": True}


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    postal_code: str | None = Field(default=None, alias="postalCode")
    capacity: int | None = None
    notes: str | None = None

    model_config = {"populate_by_name": True}


class VenueResponse(VenueBase):
    id: str
    organization_id: str = Field(alias="organizationId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    budget_cents: int | None = Field(default=None, alias="budgetCents")
    team_type: str | None = Field(default=None, alias="teamType")

    model_config = {"populate_by_name": True}


class ProjectCreate(ProjectBase):
    venue_ids: list[str] = Field(default_factory=list, alias="venueIds")


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    budget_cents: int | None = Field(default=None, alias="budgetCents")
    team_type: str | None = Field(default=None, alias="teamType")
    venue_ids: list[str] | None = Field(default=None, alias="venueIds")

    model_config = {"populate_by_name": True}


class ProjectResponse(ProjectBase):
    id: str
    organization_id: str = Field(alias="organizationId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    venues: list[VenueResponse] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class MissionTagCreate(BaseModel):
    slug: str
    label: str


class MissionTagUpdate(BaseModel):
    slug: str | None = None
    label: str | None = None


class MissionTagResponse(BaseModel):
    id: str
    slug: str
    label: str
    organization_id: str = Field(alias="organizationId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class MissionTemplateBase(BaseModel):
    name: str
    description: str | None = None
    team_size: int = Field(alias="teamSize")
    required_skills: list[str] = Field(default_factory=list, alias="requiredSkills")
    default_start_time: time | None = Field(default=None, alias="defaultStartTime")
    default_end_time: time | None = Field(default=None, alias="defaultEndTime")
    default_venue_id: str | None = Field(default=None, alias="defaultVenueId")

    model_config = {"populate_by_name": True}


class MissionTemplateCreate(MissionTemplateBase):
    tag_ids: list[str] = Field(default_factory=list, alias="tagIds")


class MissionTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    team_size: int | None = Field(default=None, alias="teamSize")
    required_skills: list[str] | None = Field(default=None, alias="requiredSkills")
    default_start_time: time | None = Field(default=None, alias="defaultStartTime")
    default_end_time: time | None = Field(default=None, alias="defaultEndTime")
    default_venue_id: str | None = Field(default=None, alias="defaultVenueId")
    tag_ids: list[str] | None = Field(default=None, alias="tagIds")

    model_config = {"populate_by_name": True}


class MissionTemplateResponse(MissionTemplateBase):
    id: str
    organization_id: str = Field(alias="organizationId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    default_venue: VenueResponse | None = Field(default=None, alias="defaultVenue")
    tags: list[MissionTagResponse] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }
