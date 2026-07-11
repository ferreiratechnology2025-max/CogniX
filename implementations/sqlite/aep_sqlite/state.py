"""
State Manager for AEP SQLite
"""

from typing import Dict, Any, Optional
from .database import Database


class StateManager:
    """Manage kernel state in SQLite"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        cursor = self.db.execute("SELECT * FROM kernel_state WHERE id = 1")
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        return dict(row)
    
    def save_state(self, state: Dict[str, Any]):
        """Save state"""
        fields = [
            'active_project', 'active_status', 'session', 'last_run',
            'last_result', 'program', 'r0_session', 'internal_last_action',
            'r2_next_act', 'r3_modified', 'r4_blockers', 'r5_active_sk',
            'r6_health', 'r7_timestamp', 'updated_at'
        ]
        
        # Build update query
        set_clauses = []
        values = []
        for field in fields:
            if field in state:
                set_clauses.append(f"{field} = ?")
                values.append(state[field])
        
        if set_clauses:
            query = f"UPDATE kernel_state SET {', '.join(set_clauses)} WHERE id = 1"
            self.db.execute(query, tuple(values))
            self.db.commit()
    
    def get_register(self, reg: str) -> Optional[str]:
        """Get a register value"""
        state = self.get_state()
        reg_map = {
            'R0': 'r0_session',
            'R1': 'internal_last_action',
            'R2': 'r2_next_act',
            'R3': 'r3_modified',
            'R4': 'r4_blockers',
            'R5': 'r5_active_sk',
            'R6': 'r6_health',
            'R7': 'r7_timestamp'
        }
        return state.get(reg_map.get(reg))
    
    def set_register(self, reg: str, value: str):
        """Set a register value"""
        reg_map = {
            'R0': 'r0_session',
            'R1': 'internal_last_action',
            'R2': 'r2_next_act',
            'R3': 'r3_modified',
            'R4': 'r4_blockers',
            'R5': 'r5_active_sk',
            'R6': 'r6_health',
            'R7': 'r7_timestamp'
        }
        field = reg_map.get(reg)
        if field:
            state = self.get_state()
            state[field] = value
            self.save_state(state)