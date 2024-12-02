import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .models import Agent, Squad, HumanNeeds, Background, AgentConfig
from .organization import Division, Department

class SimulationSerializer:
    """Handles serialization of simulation state"""
    
    @staticmethod
    def serialize_datetime(dt: datetime) -> str:
        return dt.isoformat()
        
    @staticmethod
    def deserialize_datetime(dt_str: str) -> datetime:
        return datetime.fromisoformat(dt_str)
    
    def serialize_agent(self, agent: Agent) -> Dict[str, Any]:
        return {
            "id": agent.id,
            "name": agent.name,
            "config": {
                "learning_rate": agent.config.learning_rate,
                "attention_span": agent.config.attention_span,
                "memory_capacity": agent.config.memory_capacity,
                "creativity_factor": agent.config.creativity_factor,
                "risk_tolerance": agent.config.risk_tolerance,
                "cooperation_bias": agent.config.cooperation_bias,
                "energy_efficiency": agent.config.energy_efficiency,
                "adaptation_speed": agent.config.adaptation_speed
            },
            "needs": {
                "hunger": agent.needs.hunger,
                "thirst": agent.needs.thirst,
                "bathroom": agent.needs.bathroom,
                "energy": agent.needs.energy,
                "stress": agent.needs.stress
            },
            "background": {
                "education": agent.background.education,
                "years_experience": agent.background.years_experience,
                "skills": agent.background.skills,
                "personality_traits": agent.background.personality_traits,
                "life_events": agent.background.life_events
            },
            "fitness_score": agent.fitness_score,
            "generation": agent.generation,
            "created_at": self.serialize_datetime(agent.created_at),
            "specialization": agent.specialization,
            "supervisor_id": agent.supervisor_id,
            "subordinate_ids": agent.subordinate_ids
        }
        
    def deserialize_agent(self, data: Dict[str, Any]) -> Agent:
        config = AgentConfig(**data["config"])
        needs = HumanNeeds(**data["needs"])
        background = Background(**data["background"])
        
        agent = Agent(
            id=data["id"],
            name=data["name"],
            config=config,
            needs=needs,
            background=background,
            fitness_score=data["fitness_score"],
            generation=data["generation"],
            created_at=self.deserialize_datetime(data["created_at"]),
            specialization=data["specialization"],
            supervisor_id=data["supervisor_id"],
            subordinate_ids=data["subordinate_ids"]
        )
        return agent

class SimulationPersistence:
    """Handles saving and loading simulation state"""
    
    def __init__(self, save_dir: Path):
        self.save_dir = save_dir
        self.serializer = SimulationSerializer()
        
    def save_state(self, departments: List[Department], timestamp: datetime):
        """Save current simulation state"""
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        state = {
            "timestamp": self.serializer.serialize_datetime(timestamp),
            "departments": []
        }
        
        for dept in departments:
            dept_data = {
                "id": dept.id,
                "name": dept.name,
                "created_at": self.serializer.serialize_datetime(dept.created_at),
                "divisions": []
            }
            
            for div in dept.divisions:
                div_data = {
                    "id": div.id,
                    "name": div.name,
                    "created_at": self.serializer.serialize_datetime(div.created_at),
                    "squads": []
                }
                
                for squad in div.squads:
                    squad_data = {
                        "id": squad.id,
                        "name": squad.name,
                        "fitness_score": squad.fitness_score,
                        "generation": squad.generation,
                        "created_at": self.serializer.serialize_datetime(squad.created_at),
                        "agents": [self.serializer.serialize_agent(agent) for agent in squad.agents]
                    }
                    div_data["squads"].append(squad_data)
                    
                dept_data["divisions"].append(div_data)
            state["departments"].append(dept_data)
            
        save_path = self.save_dir / f"simulation_state_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(save_path, 'w') as f:
            json.dump(state, f, indent=2)
