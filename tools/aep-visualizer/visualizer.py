#!/usr/bin/env python3
"""
AEP Visualizer - Generate HTML visualization of resources
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


def parse_resource(file_path: str) -> Dict:
    """Parse a resource file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    parsed = {}
    for line in match.group(1).split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip() for v in value[1:-1].split(',')]
            parsed[key.strip()] = value

    return parsed


def generate_html(resources_path: str, output_path: str):
    """Generate HTML visualization"""
    resources = []
    for file in Path(resources_path).glob("*.md"):
        res = parse_resource(str(file))
        if res:
            res['file'] = file.name
            resources.append(res)

    html = """<!DOCTYPE html>
<html>
<head>
    <title>AEP Resource Graph</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        .resource { border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .resource h3 { margin: 0 0 5px 0; }
        .type { color: #666; font-size: 0.9em; }
        .depends { color: #0066cc; font-size: 0.85em; }
        .status { padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
        .active { background: #d4edda; color: #155724; }
        .draft { background: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <h1>AEP Resource Graph</h1>
    <p>Total resources: """ + str(len(resources)) + """</p>
"""

    for res in resources:
        status_class = res.get('status', 'draft')
        html += f"""
    <div class="resource">
        <h3>{res.get('id', 'unknown')}</h3>
        <span class="type">{res.get('type', 'unknown')}</span>
        <span class="status {status_class}">{res.get('status', 'unknown')}</span>
        <span class="type">v{res.get('version', '?')}</span>
        <div class="depends">Depends: {res.get('depends', [])}</div>
    </div>"""

    html += """
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")
    print(f"Resources: {len(resources)}")


if __name__ == "__main__":
    import sys
    resources_path = sys.argv[1] if len(sys.argv) > 1 else "RESOURCES"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "graph.html"
    generate_html(resources_path, output_path)