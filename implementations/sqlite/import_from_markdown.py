#!/usr/bin/env python3
"""
Import Resources from Markdown KOS into SQLite AEP
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from aep_sqlite.database import Database
from aep_sqlite.resource import ResourceManager

VALID_TYPES = ['project', 'status', 'skill', 'adr', 'incident', 'rule', 'template']


def parse_markdown_resource(file_path):
    """Parse a markdown resource file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    fm_match = re.search(r'^---\n([\s\S]*?)\n---', content)
    if not fm_match:
        return None
    
    resource = {}
    for line in fm_match.group(1).split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip() for v in value[1:-1].split(',')]
            resource[key] = value
    
    # Extract content
    content_match = re.search(r'^---\n[\s\S]*?\n---\n([\s\S]*)$', content)
    if content_match:
        resource['content'] = content_match.group(1).strip()
    
    return resource


def main():
    base_path = Path(__file__).parent.parent.parent
    resources_path = base_path / "RESOURCES"
    db_path = "aep.db"
    
    print(f"Importing from {resources_path} to SQLite ({db_path})")
    
    db = Database(db_path)
    db.initialize()
    rm = ResourceManager(db)
    
    # Disable foreign key checks for import
    db.execute("PRAGMA foreign_keys = OFF")
    
    # First pass: collect all resources
    resources = []
    for file in resources_path.glob("*.md"):
        resource = parse_markdown_resource(file)
        if resource:
            # Map unknown types to 'template'
            if resource.get('type') not in VALID_TYPES:
                print(f"  {file.name}: Mapping type '{resource.get('type')}' to 'template'")
                resource['type'] = 'template'
            resources.append(resource)
    
    # Import all resources
    count = 0
    for resource in resources:
        resource_id = resource.get('id', 'unknown')
        print(f"  {resource_id}")
        try:
            rm.add_resource(resource)
            count += 1
        except Exception as e:
            print(f"    Error: {e}")
    
    # Re-enable foreign key checks
    db.execute("PRAGMA foreign_keys = ON")
    
    print(f"Imported {count} resources from Markdown to SQLite")


if __name__ == "__main__":
    main()