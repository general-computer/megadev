from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid
from .models import Agent, Squad

@dataclass
class Division:
    """A division of 10,000 employees"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    squads: List[Squad] = field(default_factory=list)
    leader: Optional[Agent] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def size(self) -> int:
        return sum(len(squad.agents) for squad in self.squads)

@dataclass
class Department:
    """A department of 100,000 employees"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    divisions: List[Division] = field(default_factory=list)
    leader: Optional[Agent] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def size(self) -> int:
        return sum(division.size for division in self.divisions)
