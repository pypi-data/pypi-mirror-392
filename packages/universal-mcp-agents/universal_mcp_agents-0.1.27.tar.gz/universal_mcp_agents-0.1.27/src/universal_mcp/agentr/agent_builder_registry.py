from __future__ import annotations

from typing import Any, Optional
from universal_mcp.agentr.client import AgentrClient
from universal_mcp.agentr.types import AgentResponse, TemplateResponse


class AgentBuilderRegistry:
    """
    HTTP client wrapper for Agent Builder operations.
    """

    def __init__(
        self,
        *,
        client: AgentrClient,
        default_agent_id: Optional[str] = None,
        default_template_id: Optional[str] = None,
    ):
        if not client:
            raise ValueError("AgentBuilderRegistry requires a valid AgentrClient")
        self.client = client
        self.default_agent_id = default_agent_id
        self.default_template_id = default_template_id

    def get_agent(
        self, agent_id: Optional[str] = None
    ) -> AgentResponse | TemplateResponse | None:
        # agent_id takes precedence, then default_agent_id, else template
        use_agent_id = agent_id or self.default_agent_id
        if use_agent_id:
            return self.client.get_agent(agent_id=str(use_agent_id))
        if self.default_template_id:
            return self.client.get_template(template_id=str(self.default_template_id))
        return None

    def create_agent(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[dict[str, Any]] = None,
        tools: Optional[dict[str, list[str]]] = None,
    ) -> AgentResponse:
        return self.client.create_agent(
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
        )

    def update_agent(
        self,
        *,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[dict[str, Any]] = None,
        tools: Optional[dict[str, list[str]]] = None,
    ) -> AgentResponse:
        use_agent_id = agent_id or self.default_agent_id
        if not use_agent_id:
            raise ValueError("agent_id not provided and no default_agent_id set")

        return self.client.update_agent(
            agent_id=str(use_agent_id),
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
        )

    def upsert_agent(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[dict[str, Any]] = None,
        tools: Optional[dict[str, list[str]]] = None,
    ) -> AgentResponse:
        if self.default_agent_id:
            return self.update_agent(
                agent_id=self.default_agent_id,
                name=name,
                description=description,
                instructions=instructions,
                tools=tools,
            )
        return self.create_agent(
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
        )


