#!/usr/bin/env python3
"""
AEP Indexer - Busca rápida em Resources usando SQLite
"""

import sqlite3
import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class AEPIndexer:
    def __init__(self, db_path: str = "aep-index.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self):
        """Cria schema do índice"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                depends TEXT,
                content_preview TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON resources(type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON resources(status)")
        self.conn.commit()

    def build_index(self, resources_path: str) -> int:
        """Indexa todos os Resources de uma pasta"""
        path = Path(resources_path)
        count = 0

        for file in path.glob("*.md"):
            resource = self.parse_markdown(file)
            if resource and 'id' in resource:
                self.conn.execute("""
                    INSERT OR REPLACE INTO resources
                    (id, type, version, status, depends, content_preview)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    resource.get('id'),
                    resource.get('type', 'unknown'),
                    resource.get('version', '0.0.0'),
                    resource.get('status', 'draft'),
                    json.dumps(resource.get('depends', [])),
                    resource.get('content', '')[:200]
                ))
                count += 1

        self.conn.commit()
        return count

    def search(self, type_filter: str = None, status_filter: str = None,
               text_search: str = None) -> List[Dict]:
        """Busca resources com filtros"""
        query = "SELECT * FROM resources WHERE 1=1"
        params = []

        if type_filter:
            query += " AND type = ?"
            params.append(type_filter)

        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)

        if text_search:
            query += " AND (id LIKE ? OR content_preview LIKE ?)"
            params.extend([f"%{text_search}%", f"%{text_search}%"])

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Retorna estatísticas do índice"""
        stats = {}
        cursor = self.conn.execute("SELECT type, COUNT(*) as count FROM resources GROUP BY type")
        stats['by_type'] = {row['type']: row['count'] for row in cursor}

        cursor = self.conn.execute("SELECT status, COUNT(*) as count FROM resources GROUP BY status")
        stats['by_status'] = {row['status']: row['count'] for row in cursor}

        cursor = self.conn.execute("SELECT COUNT(*) as total FROM resources")
        stats['total'] = cursor.fetchone()['total']

        return stats

    def parse_markdown(self, file_path: Path) -> Optional[Dict]:
        """Extrai frontmatter de um arquivo Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        fm_match = re.search(r'^---\n([\s\S]*?)\n---', content)
        if not fm_match:
            return None

        resource = {}
        for line in fm_match.group(1).split('\n'):
            if ': ' in line:
                key, value = line.split(': ', 1)
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',') if v.strip()]
                resource[key.strip()] = value

        content_match = re.search(r'^---\n[\s\S]*?\n---\n([\s\S]*)$', content)
        if content_match:
            resource['content'] = content_match.group(1).strip()

        return resource

    def close(self):
        """Fecha conexão"""
        self.conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AEP Indexer")
    parser.add_argument('command', choices=['build', 'search', 'stats'])
    parser.add_argument('--path', default='RESOURCES', help='Resources path')
    parser.add_argument('--type', help='Filter by type')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--query', help='Text search')

    args = parser.parse_args()
    indexer = AEPIndexer()

    if args.command == 'build':
        count = indexer.build_index(args.path)
        print(f"Indexed {count} resources from {args.path}")

    elif args.command == 'search':
        results = indexer.search(args.type, args.status, args.query)
        for r in results:
            print(f"  {r['id']} ({r['type']}) v{r['version']} - {r['status']}")

    elif args.command == 'stats':
        stats = indexer.get_stats()
        print(f"Total: {stats['total']} resources")
        print(f"By type: {stats['by_type']}")
        print(f"By status: {stats['by_status']}")

    indexer.close()


if __name__ == "__main__":
    main()