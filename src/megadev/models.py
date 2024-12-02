from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import random
from faker import Faker

fake = Faker()

@dataclass
class HumanNeeds:
    """Physical and psychological needs of an agent"""
    hunger: float = 0.0  # 0-100, 0 is full, 100 is starving
    thirst: float = 0.0  # 0-100
    bathroom: float = 0.0  # 0-100
    energy: float = 100.0  # 0-100, 0 is exhausted
    stress: float = 0.0  # 0-100
    
    def update(self, time_delta: float):
        """Update needs based on time passed (in hours)"""
        self.hunger += 10 * time_delta
        self.thirst += 15 * time_delta
        self.bathroom += 12 * time_delta
        self.energy -= 8 * time_delta
        self.stress += 5 * time_delta * random.uniform(0.8, 1.2)
        
        # Clamp values
        for attr in ['hunger', 'thirst', 'bathroom', 'stress']:
            setattr(self, attr, min(100.0, max(0.0, getattr(self, attr))))
        self.energy = min(100.0, max(0.0, self.energy))

@dataclass
class Background:
    """Agent's simulated life experience"""
    education: str
    years_experience: int
    skills: List[str]
    personality_traits: List[str]
    life_events: List[str]
    
    @classmethod
    def generate_random(cls) -> 'Background':
        """Generate a random background"""
        education_levels = ['High School', "Bachelor's", "Master's", 'PhD']
        skills = ['Writing', 'Analysis', 'Research', 'Communication', 'Leadership', 
                 'Problem Solving', 'Critical Thinking', 'Time Management']
        traits = ['Introvert', 'Extrovert', 'Detail-oriented', 'Creative', 
                 'Analytical', 'Collaborative', 'Independent', 'Ambitious']
        events = ['Career Change', 'Relocation', 'Major Project Success', 
                 'Industry Award', 'Professional Development']
        
        return cls(
            education=random.choice(education_levels),
            years_experience=random.randint(1, 30),
            skills=random.sample(skills, random.randint(2, 5)),
            personality_traits=random.sample(traits, random.randint(2, 4)),
            life_events=random.sample(events, random.randint(1, 3))
        )

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
    """An AI agent with evolved parameters and human characteristics"""
    id: str
    name: str
    config: AgentConfig
    needs: HumanNeeds = field(default_factory=HumanNeeds)
    background: Background = field(default_factory=Background.generate_random)
    fitness_score: float = 0.0
    generation: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    specialization: Optional[str] = None
    supervisor_id: Optional[str] = None
    subordinate_ids: List[str] = field(default_factory=list)
    
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
