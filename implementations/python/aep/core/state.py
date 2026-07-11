"""
State management for AEP
"""

import os
import re
import tempfile
from typing import Dict, Any, Optional


class StateManager:
    """Manage AEP runtime state (R0-R7).

    The AEP runtime stores its state under ``AEP/runtime_state/state.md``,
    completely isolated from the KOS meta-kernel state (``KERNEL/STATE.md``).
    Override with the ``AEP_STATE_PATH`` environment variable for CI/CD
    sandboxing.
    """

    DEFAULT_STATE_PATH = "AEP/runtime_state/state.md"

    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.state_path = os.environ.get(
            "AEP_STATE_PATH",
            os.path.join(base_path, self.DEFAULT_STATE_PATH),
        )
        self.program_path = os.path.join(base_path, "KERNEL", "PROGRAM.md")
    
    def load_state(self) -> 'State':
        """Load state from file"""
        if not os.path.exists(self.state_path):
            return State()
        
        with open(self.state_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return State.from_markdown(content)
    
    def save_state(self, state: 'State') -> bool:
        """Save state to file atomically (write to a temp file in the same
        directory, then os.replace) so the state file is never left empty or
        partially written if the process dies mid-write."""
        content = state.to_markdown()
        target_dir = os.path.dirname(self.state_path)
        os.makedirs(target_dir, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=target_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(tmp_path, self.state_path)
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
        return True
    
    def load_program(self) -> list:
        """Load program from file"""
        if not os.path.exists(self.program_path):
            return ["BOOT", "LOAD", "VALIDATE", "EXEC", "COMMIT", "EXIT"]
        
        with open(self.program_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract opcode sequence
        lines = content.split('\n')
        opcodes = []
        in_flow = False
        for line in lines:
            line = line.strip()
            if line == "BOOT":
                in_flow = True
            if in_flow and line and not line.startswith('#') and not line.startswith('├') and not line.startswith('└'):
                opcodes.append(line)
            if line.startswith('EXIT'):
                in_flow = False
        
        return opcodes if opcodes else ["BOOT", "LOAD project-cognix", "LOAD status-cognix", "VALIDATE project-cognix", "VALIDATE status-cognix", "EXEC", "COMMIT", "EXIT"]


class State:
    """State object with R0-R7 registers"""
    
    def __init__(self):
        self.registers = {}
        self.type = "state"
        self.id = "kernel-state"
        self.version = "1.0.0"
        self.status = "active"
    
    def set_register(self, reg: str, value: str):
        """Set a register value"""
        if not re.match(r'^R[0-7]$', reg):
            raise ValueError(f"Invalid register: {reg}")
        self.registers[reg] = value
    
    def get_register(self, reg: str) -> Optional[str]:
        """Get a register value"""
        return self.registers.get(reg)
    
    def get_all_registers(self) -> Dict[str, str]:
        """Get all registers"""
        return self.registers.copy()
    
    def to_markdown(self) -> str:
        """Convert state to Markdown format"""
        lines = [
            "---",
            f"type: {self.type}",
            f"id: {self.id}",
            f"version: {self.version}",
            f"status: {self.status}",
            "---",
            "# ESTADO GLOBAL DO KERNEL",
            "",
        ]
        
        for reg in ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']:
            if reg in self.registers:
                lines.append(f"{reg} [{self._get_reg_name(reg)}] = {self.registers[reg]}")
        
        return "\n".join(lines)
    
    def _get_reg_name(self, reg: str) -> str:
        """Get register name"""
        names = {
            'R0': 'SESSION',
            'R1': 'LAST_ACT',
            'R2': 'NEXT_ACT',
            'R3': 'MODIFIED',
            'R4': 'BLOCKERS',
            'R5': 'ACTIVE_SK',
            'R6': 'HEALTH',
            'R7': 'TIMESTAMP'
        }
        return names.get(reg, 'UNKNOWN')
    
    @classmethod
    def from_markdown(cls, content: str) -> 'State':
        """Parse state from Markdown content"""
        state = cls()
        
        # Extract frontmatter
        frontmatter_match = re.search(r'^---\n([\s\S]*?)\n---', content)
        if frontmatter_match:
            fm = frontmatter_match.group(1)
            for line in fm.split('\n'):
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    if hasattr(state, key):
                        setattr(state, key, value.strip())
        
        # Extract registers
        for line in content.split('\n'):
            match = re.match(r'^(R[0-7])\s*\[([^\]]*)\]\s*=\s*(.*)$', line.strip())
            if match:
                state.registers[match.group(1)] = match.group(3)
        
        return state