from typing import Any, Dict, Optional
import asyncio
from mcp import Server, Resource, Tool
from .models import Squad
from .evolution import EvolutionEngine

class MegaDevServer(Server):
    def __init__(self):
        super().__init__()
        self.engine = EvolutionEngine()
        self.population: List[Squad] = []
        self.generation = 0
        
        # Register resources
        self.register_resource("population", self.get_population)
        self.register_resource("best_squad", self.get_best_squad)
        
        # Register tools
        self.register_tool(
            Tool(
                name="initialize_population",
                description="Create initial population of AI agent squads",
                parameters={
                    "population_size": {
                        "type": "integer",
                        "description": "Number of squads to create",
                        "minimum": 2,
                        "maximum": 100
                    },
                    "squad_size": {
                        "type": "integer",
                        "description": "Number of agents per squad",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                handler=self.initialize_population
            )
        )
        
        self.register_tool(
            Tool(
                name="evolve_generation",
                description="Evolve the current population to create a new generation",
                parameters={},
                handler=self.evolve_generation
            )
        )

    async def get_population(self, params: Optional[Dict[str, Any]] = None) -> Resource:
        """Resource handler for current population state"""
        return Resource(
            data={
                "generation": self.generation,
                "population_size": len(self.population),
                "squads": [
                    {
                        "id": squad.id,
                        "name": squad.name,
                        "fitness": squad.fitness_score,
                        "agents": len(squad.agents)
                    }
                    for squad in self.population
                ]
            }
        )

    async def get_best_squad(self, params: Optional[Dict[str, Any]] = None) -> Resource:
        """Resource handler for best performing squad"""
        if not self.population:
            return Resource(error="No population initialized")
            
        best_squad = max(self.population, key=lambda s: s.fitness_score)
        return Resource(
            data={
                "id": best_squad.id,
                "name": best_squad.name,
                "fitness": best_squad.fitness_score,
                "generation": best_squad.generation,
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "fitness": agent.fitness_score,
                        "config": vars(agent.config)
                    }
                    for agent in best_squad.agents
                ]
            }
        )

    async def initialize_population(self, population_size: int, squad_size: int) -> Dict[str, Any]:
        """Tool handler to initialize population"""
        self.engine = EvolutionEngine(population_size=population_size)
        self.population = self.engine.create_initial_population()
        self.generation = 0
        
        return {
            "status": "success",
            "population_size": len(self.population),
            "squad_size": squad_size,
            "generation": self.generation
        }

    async def evolve_generation(self) -> Dict[str, Any]:
        """Tool handler to evolve population"""
        if not self.population:
            return {"error": "No population initialized"}
            
        # Simulate fitness evaluation
        for squad in self.population:
            squad.fitness_score = sum(random.random() for _ in range(len(squad.agents)))
            for agent in squad.agents:
                agent.fitness_score = random.random()
        
        self.population = self.engine.evolve_population(self.population)
        self.generation = self.engine.generation
        
        best_squad = max(self.population, key=lambda s: s.fitness_score)
        return {
            "status": "success",
            "generation": self.generation,
            "best_fitness": best_squad.fitness_score,
            "average_fitness": sum(s.fitness_score for s in self.population) / len(self.population)
        } 