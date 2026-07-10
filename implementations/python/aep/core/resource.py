"""
Resource management for AEP
"""

import os
import re
from typing import Dict, Any, Optional, List

VALID_TYPES = ['project', 'status', 'skill', 'adr', 'incident', 'rule', 'template']
VALID_STATUS = ['draft', 'review', 'active', 'deprecated', 'archived']

# A resource_id is a plain identifier. Anything else (path separators, "..",
# drive letters, dots) is rejected before it is ever joined into a filesystem
# path, so resolution cannot escape the resources directory (path traversal).
RESOURCE_ID_RE = re.compile(r'^[a-zA-Z0-9_-]+$')


class ResourceManager:
    """Manage AEP Resources"""

    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.resources_path = os.path.join(base_path, "RESOURCES")

    @staticmethod
    def is_valid_resource_id(resource_id: Any) -> bool:
        """True only for plain identifiers safe to resolve to a file path."""
        return isinstance(resource_id, str) and bool(RESOURCE_ID_RE.match(resource_id))

    def load_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Load a resource by ID"""
        # Reject non-identifier ids before building any path (traversal guard).
        if not self.is_valid_resource_id(resource_id):
            return None
        # Try .md first
        file_path = os.path.join(self.resources_path, f"{resource_id}.md")
        if not os.path.exists(file_path):
            # Try .json
            file_path = os.path.join(self.resources_path, f"{resource_id}.json")
            if not os.path.exists(file_path):
                return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self._parse_resource(content)
    
    def _parse_resource(self, content: str) -> Dict[str, Any]:
        """Parse resource from content"""
        resource = {}
        
        # Extract frontmatter
        frontmatter_match = re.search(r'^---\n([\s\S]*?)\n---', content)
        if frontmatter_match:
            fm = frontmatter_match.group(1)
            for line in fm.split('\n'):
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    # Handle arrays
                    if value.startswith('[') and value.endswith(']'):
                        value = [v.strip() for v in value[1:-1].split(',')]
                    resource[key] = value
        
        # Extract content (everything after frontmatter)
        content_match = re.search(r'^---\n[\s\S]*?\n---\n([\s\S]*)$', content)
        if content_match:
            resource['content'] = content_match.group(1).strip()
        
        return resource
    
    def validate_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a resource structure"""
        errors = []
        warnings = []
        
        # Validate type
        if 'type' not in resource:
            errors.append("Missing required field: type")
        elif resource['type'] not in VALID_TYPES:
            errors.append(f"Invalid type: {resource['type']} (expected one of: {', '.join(VALID_TYPES)})")
        
        # Validate id
        if 'id' not in resource:
            errors.append("Missing required field: id")
        elif not re.match(r'^[a-z][a-z0-9-]*$', resource['id']):
            errors.append(f"Invalid id format: {resource['id']} (expected kebab-case)")
        
        # Validate version
        if 'version' not in resource:
            errors.append("Missing required field: version")
        elif not re.match(r'^\d+\.\d+\.\d+$', resource['version']):
            errors.append(f"Invalid version format: {resource['version']} (expected semver)")
        
        # Validate depends
        if 'depends' in resource:
            if not isinstance(resource['depends'], list):
                errors.append("depends must be an array")
        
        # Validate status
        if 'status' not in resource:
            errors.append("Missing required field: status")
        elif resource['status'] not in VALID_STATUS:
            errors.append(f"Invalid status: {resource['status']} (expected one of: {', '.join(VALID_STATUS)})")
        
        # Validate content
        if 'content' not in resource or not resource['content']:
            warnings.append("Resource content is empty")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def list_resources(self) -> List[str]:
        """List all available resources"""
        resources = []
        if os.path.exists(self.resources_path):
            for file in os.listdir(self.resources_path):
                if file.endswith('.md') or file.endswith('.json'):
                    resources.append(os.path.splitext(file)[0])
        return resources