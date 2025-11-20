from __future__ import annotations

from typing import Any, Literal, TypedDict, Dict, List, Optional


class VersionedEntry(TypedDict, total=False):
    plan: Any
    script: Optional[str]
    params: Optional[List[Dict[str, Any]]]
    meta: Dict[str, Any]


class VersionedInstructions(TypedDict):
    currentVersion: int
    data: Dict[str, VersionedEntry]


class ResolvedInstructions(TypedDict, total=False):
    currentVersion: int
    plan: Any
    script: Optional[str]
    params: Optional[List[Dict[str, Any]]]
    meta: Dict[str, Any]


class AgentResponse(TypedDict, total=False):
    id: str
    name: str | None
    description: str | None
    user_id: str
    org_id: str
    instructions: Optional[ResolvedInstructions]
    tools: dict[str, list[str]] | None
    visibility: Literal["private", "readonly", "public"] | None
    job_id: str | None
    job_cron: str | None
    job_enabled: bool | None
    created_at: str
    updated_at: str


class TemplateResponse(TypedDict, total=False):
    id: str
    name: str | None
    description: str | None
    categories: list[str] | None
    user_id: str
    user_name: str | None
    instructions: Optional[VersionedInstructions]
    tools: dict[str, list[str]] | None
    visibility: Literal["private", "readonly", "public"] | None
    job_cron: str | None
    created_at: str
    updated_at: str


