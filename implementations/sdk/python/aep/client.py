"""
AEP Client - High-level API for AEP operations
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from .types import Resource, State, Program, ResourceType, ResourceStatus


class AEPClient:
    """High-level client for AEP operations"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.resources_path = self.base_path / "RESOURCES"
        self.state_path = self.base_path / "KERNEL" / "STATE.md"
        self.loaded_resources: Dict[str, Resource] = {}
        self.state: Optional[State] = None

    def boot(self) -> Dict[str, Any]:
        """Initialize the system"""
        self.state = State()
        return {"status": "OK", "message": "System initialized"}

    def load(self, resource_id: str) -> Dict[str, Any]:
        """Load a resource by ID"""
        file_path = self.resources_path / f"{resource_id}.md"
        if not file_path.exists():
            return {"status": "FAIL", "error": f"Resource '{resource_id}' not found"}

        content = file_path.read_text(encoding="utf-8")
        resource = self._parse_resource(resource_id, content)
        if resource:
            self.loaded_resources[resource_id] = resource
            return {"status": "OK", "resource": resource_id}
        return {"status": "FAIL", "error": f"Failed to parse resource '{resource_id}'"}

    def validate(self, resource_id: str) -> Dict[str, Any]:
        """Validate a resource"""
        if resource_id not in self.loaded_resources:
            result = self.load(resource_id)
            if result["status"] == "FAIL":
                return result

        resource = self.loaded_resources[resource_id]
        errors = []

        if not resource.type:
            errors.append("Missing type")
        if not resource.id:
            errors.append("Missing id")
        if not resource.version:
            errors.append("Missing version")

        return {
            "status": "OK" if not errors else "FAIL",
            "resource": resource_id,
            "valid": len(errors) == 0,
            "errors": errors
        }

    def list_resources(self) -> List[str]:
        """List all available resources"""
        if not self.resources_path.exists():
            return []
        return [f.stem for f in self.resources_path.glob("*.md")]

    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        if self.state:
            return self.state.to_dict()
        return {}

    def _parse_resource(self, resource_id: str, content: str) -> Optional[Resource]:
        """Parse a resource from markdown content"""
        lines = content.split("\n")
        metadata = {}
        content_lines = []
        in_frontmatter = False

        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    metadata[key.strip()] = value.strip()
            else:
                content_lines.append(line)

        try:
            return Resource(
                id=metadata.get("id", resource_id),
                type=ResourceType(metadata.get("type", "project")),
                version=metadata.get("version", "0.0.0"),
                status=ResourceStatus(metadata.get("status", "draft")),
                depends=self._parse_depends(metadata.get("depends", "")),
                content="\n".join(content_lines)
            )
        except Exception:
            return None

    def _parse_depends(self, depends_str: str) -> List[str]:
        """Parse depends field"""
        if depends_str.startswith("[") and depends_str.endswith("]"):
            return [d.strip() for d in depends_str[1:-1].split(",") if d.strip()]
        return []