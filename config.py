"""
Bridge MCP - Configuration Management
=====================================
Handles persistent configuration and agent storage.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Default paths
def get_config_dir() -> Path:
    """Get the configuration directory for Bridge MCP."""
    # Use user's home directory for cross-platform compatibility
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('APPDATA', Path.home()))
    else:  # Linux/Mac
        base = Path.home() / '.config'
    
    config_dir = base / 'bridge-mcp'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_agents_file() -> Path:
    """Get the path to the agents storage file."""
    return get_config_dir() / 'agents.json'

def get_config_file() -> Path:
    """Get the path to the main config file."""
    return get_config_dir() / 'config.json'


class AgentStorage:
    """Persistent storage for registered agents."""
    
    def __init__(self):
        self.agents_file = get_agents_file()
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _load(self):
        """Load agents from file."""
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r') as f:
                    self._agents = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._agents = {}
        else:
            self._agents = {}
            self._save()
    
    def _save(self):
        """Save agents to file."""
        try:
            with open(self.agents_file, 'w') as f:
                json.dump(self._agents, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save agents: {e}")
    
    def register(self, agent_id: str, callback_url: str, agent_name: str = "My PC", token: str = None) -> dict:
        """Register an agent (persists to file)."""
        
        # specific imports for token generation
        import secrets
        import string
        
        # Generate token if not provided and not existing
        if not token:
            existing = self._agents.get(agent_id)
            if existing and "token" in existing:
                token = existing["token"]
            else:
                alphabet = string.ascii_letters + string.digits
                token = ''.join(secrets.choice(alphabet) for i in range(32))
        
        self._agents[agent_id] = {
            "callback_url": callback_url,
            "name": agent_name,
            "status": "registered",
            "token": token
        }
        self._save()
        return {
            "status": "registered",
            "agent_id": agent_id,
            "message": f"Agent '{agent_name}' registered and saved permanently",
            "token": token
        }
    
    def unregister(self, agent_id: str) -> dict:
        """Remove an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._save()
            return {"status": "removed", "agent_id": agent_id}
        return {"error": f"Agent {agent_id} not found"}
    
    def get(self, agent_id: str) -> Optional[dict]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
    
    def get_all(self) -> Dict[str, dict]:
        """Get all registered agents."""
        return self._agents.copy()
    
    def get_first(self) -> Optional[tuple]:
        """Get the first available agent."""
        if self._agents:
            agent_id = list(self._agents.keys())[0]
            return agent_id, self._agents[agent_id]
        return None
    
    def update_status(self, agent_id: str, status: str):
        """Update agent status (connected/disconnected)."""
        if agent_id in self._agents:
            self._agents[agent_id]["status"] = status
            self._save()
    
    def set_default(self, agent_id: str) -> dict:
        """Set an agent as the default."""
        if agent_id not in self._agents:
            return {"error": f"Agent {agent_id} not found"}
        
        # Move to front by recreating dict
        agent = self._agents.pop(agent_id)
        self._agents = {agent_id: agent, **self._agents}
        self._save()
        return {"status": "default_set", "agent_id": agent_id}


class Config:
    """Main configuration manager."""
    
    DEFAULT_CONFIG = {
        "local_agent_port": 8006,
        "auto_connect_localhost": True,
        "connection_timeout": 30,
        "default_agent_id": "local"
    }
    
    def __init__(self):
        self.config_file = get_config_file()
        self._config = self.DEFAULT_CONFIG.copy()
        self._load()
    
    def _load(self):
        """Load config from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                    self._config.update(saved)
            except (json.JSONDecodeError, IOError):
                pass
        self._save()
    
    def _save(self):
        """Save config to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError:
            pass
    
    def get(self, key: str, default=None):
        """Get a config value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        """Set a config value."""
        self._config[key] = value
        self._save()


# Global instances
agent_storage = AgentStorage()
config = Config()
