from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import uuid

@dataclass
class AgentConfig:
    """Configuration parameters for an AI agent"""
    learning_rate: float
    attention_span: int
    memory_capacity: int
    creativity_factor: float
    risk_tolerance: float
    cooperation_bias: float
    energy_efficiency: float
    adaptation_speed: float

@dataclass
class Agent:
    """An AI agent with evolved parameters"""
    id: str
    name: str
    config: AgentConfig
    fitness_score: float = 0.0
    generation: int = 0
    created_at: datetime = datetime.now()
    specialization: Optional[str] = None
    
    @classmethod
    def create_random(cls, name: str) -> 'Agent':
        """Create an agent with randomized parameters"""
        import random
        
        config = AgentConfig(
            learning_rate=random.uniform(0.1, 1.0),
            attention_span=random.randint(1, 10),
            memory_capacity=random.randint(1, 100),
            creativity_factor=random.uniform(0.1, 1.0),
            risk_tolerance=random.uniform(0.1, 1.0),
            cooperation_bias=random.uniform(0.1, 1.0),
            energy_efficiency=random.uniform(0.1, 1.0),
            adaptation_speed=random.uniform(0.1, 1.0)
        )
        
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            config=config
        )

@dataclass
class Squad:
    """A group of agents working together"""
    id: str
    name: str
    agents: List[Agent]
    fitness_score: float = 0.0
    generation: int = 0
    created_at: datetime = datetime.now()
    
    @classmethod
    def create_random(cls, name: str, size: int = 5) -> 'Squad':
        """Create a squad with random agents"""
        agents = [
            Agent.create_random(f"{name}-Agent-{i}") 
            for i in range(size)
        ]
        
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            agents=agents
        ) 