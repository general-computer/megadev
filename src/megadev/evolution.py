from typing import List, Tuple
import random
import numpy as np
from .models import Squad, Agent, AgentConfig

class EvolutionEngine:
    def __init__(self, population_size: int = 10, elite_size: int = 2):
        self.population_size = population_size
        self.elite_size = elite_size
        self.generation = 0
        
    def create_initial_population(self) -> List[Squad]:
        """Create initial population of squads"""
        return [
            Squad.create_random(f"Squad-{i}")
            for i in range(self.population_size)
        ]
    
    def mutate_config(self, config: AgentConfig) -> AgentConfig:
        """Apply random mutations to agent config"""
        mutation_rate = 0.1
        
        def mutate_value(value: float) -> float:
            if random.random() < mutation_rate:
                return max(0.1, min(1.0, value + random.gauss(0, 0.1)))
            return value
        
        return AgentConfig(
            learning_rate=mutate_value(config.learning_rate),
            attention_span=max(1, int(mutate_value(config.attention_span))),
            memory_capacity=max(1, int(mutate_value(config.memory_capacity))),
            creativity_factor=mutate_value(config.creativity_factor),
            risk_tolerance=mutate_value(config.risk_tolerance),
            cooperation_bias=mutate_value(config.cooperation_bias),
            energy_efficiency=mutate_value(config.energy_efficiency),
            adaptation_speed=mutate_value(config.adaptation_speed)
        )
    
    def crossover(self, parent1: Agent, parent2: Agent) -> Agent:
        """Create new agent by combining parameters from parents"""
        child_config = AgentConfig(
            learning_rate=(parent1.config.learning_rate + parent2.config.learning_rate) / 2,
            attention_span=(parent1.config.attention_span + parent2.config.attention_span) // 2,
            memory_capacity=(parent1.config.memory_capacity + parent2.config.memory_capacity) // 2,
            creativity_factor=(parent1.config.creativity_factor + parent2.config.creativity_factor) / 2,
            risk_tolerance=(parent1.config.risk_tolerance + parent2.config.risk_tolerance) / 2,
            cooperation_bias=(parent1.config.cooperation_bias + parent2.config.cooperation_bias) / 2,
            energy_efficiency=(parent1.config.energy_efficiency + parent2.config.energy_efficiency) / 2,
            adaptation_speed=(parent1.config.adaptation_speed + parent2.config.adaptation_speed) / 2
        )
        
        return Agent(
            id=str(uuid.uuid4()),
            name=f"Gen{self.generation}-{parent1.name}-{parent2.name}",
            config=self.mutate_config(child_config),
            generation=self.generation
        )
    
    def evolve_population(self, squads: List[Squad]) -> List[Squad]:
        """Evolve population through selection, crossover and mutation"""
        self.generation += 1
        
        # Sort squads by fitness
        sorted_squads = sorted(squads, key=lambda s: s.fitness_score, reverse=True)
        
        # Keep elite squads
        new_population = sorted_squads[:self.elite_size]
        
        # Create new squads through crossover
        while len(new_population) < self.population_size:
            parent_squad1 = random.choice(sorted_squads[:len(sorted_squads)//2])
            parent_squad2 = random.choice(sorted_squads[:len(sorted_squads)//2])
            
            new_agents = []
            for i in range(len(parent_squad1.agents)):
                parent1 = random.choice(parent_squad1.agents)
                parent2 = random.choice(parent_squad2.agents)
                new_agents.append(self.crossover(parent1, parent2))
            
            new_squad = Squad(
                id=str(uuid.uuid4()),
                name=f"Squad-Gen{self.generation}-{len(new_population)}",
                agents=new_agents,
                generation=self.generation
            )
            new_population.append(new_squad)
        
        return new_population 