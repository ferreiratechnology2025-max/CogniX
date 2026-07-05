"""
AEP Type Definitions
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ResourceType(str, Enum):
    PROJECT = "project"
    STATUS = "status"
    SKILL = "skill"
    ADR = "adr"
    INCIDENT = "incident"
    RULE = "rule"
    TEMPLATE = "template"


class ResourceStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class Resource:
    id: str
    type: ResourceType
    version: str
    status: ResourceStatus
    depends: List[str] = field(default_factory=list)
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "version": self.version,
            "status": self.status.value,
            "depends": self.depends,
            "content": self.content,
            **self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        return cls(
            id=data["id"],
            type=ResourceType(data["type"]),
            version=data["version"],
            status=ResourceStatus(data["status"]),
            depends=data.get("depends", []),
            content=data.get("content", ""),
            metadata={k: v for k, v in data.items() 
                     if k not in ["id", "type", "version", "status", "depends", "content"]}
        )


@dataclass
class State:
    r0_session: Optional[str] = None
    r1_last_act: Optional[str] = None
    r2_next_act: Optional[str] = None
    r3_modified: Optional[str] = None
    r4_blockers: Optional[str] = None
    r5_active_sk: Optional[str] = None
    r6_health: str = "OK"
    r7_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "r0_session": self.r0_session,
            "r1_last_act": self.r1_last_act,
            "r2_next_act": self.r2_next_act,
            "r3_modified": self.r3_modified,
            "r4_blockers": self.r4_blockers,
            "r5_active_sk": self.r5_active_sk,
            "r6_health": self.r6_health,
            "r7_timestamp": self.r7_timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State':
        return cls(**{k: v for k, v in data.items() if k.startswith("r")})


@dataclass
class Program:
    name: str
    steps: List[str]
    description: str = ""

    @classmethod
    def default(cls) -> 'Program':
        return cls(
            name="default",
            steps=[
                "BOOT",
                "LOAD [ACTIVE_PROJECT]",
                "VALIDATE [ACTIVE_PROJECT]",
                "EXEC",
                "COMMIT",
                "EXIT"
            ],
            description="Default AEP program"
        )