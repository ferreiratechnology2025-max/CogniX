"""
Resource Manager for AEP SQLite
"""

import json
import re
from typing import Dict, Any, List, Optional
from .database import Database


class ResourceManager:
    """Manage Resources in SQLite"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_resource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a resource to the database"""
        resource_id = data.get('id')
        resource_type = data.get('type')
        version = data.get('version', '1.0.0')
        status = data.get('status', 'active')
        depends = data.get('depends', [])
        content = data.get('content', '')
        
        if not resource_id or not resource_type:
            raise ValueError("Resource must have 'id' and 'type'")
        
        # Insert resource
        self.db.execute(
            "INSERT OR REPLACE INTO resources (id, type, version, status, content) VALUES (?, ?, ?, ?, ?)",
            (resource_id, resource_type, version, status, content)
        )
        
        # Insert dependencies
        if depends:
            self.db.execute(
                "DELETE FROM resource_dependencies WHERE resource_id = ?",
                (resource_id,)
            )
            for dep in depends:
                if isinstance(dep, str):
                    self.db.execute(
                        "INSERT OR IGNORE INTO resource_dependencies (resource_id, depends_on) VALUES (?, ?)",
                        (resource_id, dep)
                    )
        
        self.db.commit()
        
        return {
            "id": resource_id,
            "type": resource_type,
            "version": version,
            "status": status,
            "depends": depends
        }
    
    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a resource by ID"""
        cursor = self.db.execute(
            "SELECT id, type, version, status, content FROM resources WHERE id = ?",
            (resource_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Get dependencies
        dep_cursor = self.db.execute(
            "SELECT depends_on FROM resource_dependencies WHERE resource_id = ?",
            (resource_id,)
        )
        depends = [r[0] for r in dep_cursor.fetchall()]
        
        return {
            "id": row['id'],
            "type": row['type'],
            "version": row['version'],
            "status": row['status'],
            "content": row['content'],
            "depends": depends
        }
    
    def get_dependencies(self, resource_id: str) -> List[str]:
        """Get dependencies of a resource"""
        cursor = self.db.execute(
            "SELECT depends_on FROM resource_dependencies WHERE resource_id = ?",
            (resource_id,)
        )
        return [r[0] for r in cursor.fetchall()]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all resources"""
        cursor = self.db.execute("SELECT id, type, version, status FROM resources")
        return [dict(row) for row in cursor.fetchall()]
    
    def validate_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a resource structure"""
        errors = []
        warnings = []
        
        valid_types = ['project', 'status', 'skill', 'adr', 'incident', 'rule', 'template']
        valid_status = ['draft', 'review', 'active', 'deprecated', 'archived']
        
        # Validate type
        if 'type' not in resource:
            errors.append("Missing required field: type")
        elif resource['type'] not in valid_types:
            errors.append(f"Invalid type: {resource['type']}")
        
        # Validate id
        if 'id' not in resource:
            errors.append("Missing required field: id")
        elif not re.match(r'^[a-z][a-z0-9-]*$', resource['id']):
            errors.append(f"Invalid id format: {resource['id']}")
        
        # Validate version
        if 'version' not in resource:
            errors.append("Missing required field: version")
        elif not re.match(r'^\d+\.\d+\.\d+$', resource['version']):
            errors.append(f"Invalid version: {resource['version']}")
        
        # Validate status
        if 'status' not in resource:
            errors.append("Missing required field: status")
        elif resource['status'] not in valid_status:
            errors.append(f"Invalid status: {resource['status']}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }