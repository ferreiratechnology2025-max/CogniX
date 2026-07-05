"""
SQLite Database Manager for AEP
"""

import sqlite3
import os
from typing import Optional


class Database:
    """SQLite database connection and operations"""
    
    def __init__(self, db_path: str = "aep.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def initialize(self):
        """Initialize database schema"""
        conn = self.connect()
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
        else:
            # Inline schema
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS resource_dependencies (
                    resource_id TEXT NOT NULL,
                    depends_on TEXT NOT NULL,
                    FOREIGN KEY (resource_id) REFERENCES resources(id),
                    FOREIGN KEY (depends_on) REFERENCES resources(id),
                    PRIMARY KEY (resource_id, depends_on)
                );
                CREATE TABLE IF NOT EXISTS kernel_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    active_project TEXT,
                    active_status TEXT,
                    session TEXT,
                    last_run TEXT,
                    last_result TEXT,
                    program TEXT DEFAULT 'padrao',
                    r0_session TEXT,
                    r1_last_act TEXT,
                    r2_next_act TEXT,
                    r3_modified TEXT,
                    r4_blockers TEXT,
                    r5_active_sk TEXT,
                    r6_health TEXT DEFAULT 'OK',
                    r7_timestamp TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
        
        # Insert default state if not exists
        cursor = conn.execute("SELECT COUNT(*) FROM kernel_state")
        if cursor.fetchone()[0] == 0:
            conn.execute("INSERT INTO kernel_state (id) VALUES (1)")
        
        conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        conn = self.connect()
        return conn.execute(query, params)
    
    def commit(self):
        """Commit changes"""
        if self.conn:
            self.conn.commit()
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
            self.conn = None