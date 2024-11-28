import pytest
from megadev.server import MegaDevServer
from megadev.models import Squad, Agent

@pytest.fixture
async def server():
    return MegaDevServer()

@pytest.mark.asyncio
async def test_server_initialization(server):
    assert server.population == []
    assert server.generation == 0
    assert server.engine is not None

@pytest.mark.asyncio
async def test_initialize_population(server):
    result = await server.initialize_population(population_size=5, squad_size=3)
    
    assert result["status"] == "success"
    assert result["population_size"] == 5
    assert result["squad_size"] == 3
    assert result["generation"] == 0
    
    assert len(server.population) == 5
    assert all(len(squad.agents) == 5 for squad in server.population)

@pytest.mark.asyncio
async def test_get_population_empty(server):
    resource = await server.get_population()
    
    assert resource.data["generation"] == 0
    assert resource.data["population_size"] == 0
    assert resource.data["squads"] == []

@pytest.mark.asyncio
async def test_get_population_with_data(server):
    await server.initialize_population(population_size=3, squad_size=2)
    resource = await server.get_population()
    
    assert resource.data["generation"] == 0
    assert resource.data["population_size"] == 3
    assert len(resource.data["squads"]) == 3
    
    squad_data = resource.data["squads"][0]
    assert "id" in squad_data
    assert "name" in squad_data
    assert "fitness" in squad_data
    assert "agents" in squad_data

@pytest.mark.asyncio
async def test_get_best_squad_empty(server):
    resource = await server.get_best_squad()
    assert "error" in resource.error
    assert resource.error == "No population initialized"

@pytest.mark.asyncio
async def test_get_best_squad_with_data(server):
    await server.initialize_population(population_size=3, squad_size=2)
    
    # Set some fitness scores
    for i, squad in enumerate(server.population):
        squad.fitness_score = float(i)
    
    resource = await server.get_best_squad()
    
    assert resource.data["fitness"] == 2.0  # Highest fitness score
    assert len(resource.data["agents"]) == 5
    
    agent_data = resource.data["agents"][0]
    assert "id" in agent_data
    assert "name" in agent_data
    assert "fitness" in agent_data
    assert "config" in agent_data

@pytest.mark.asyncio
async def test_evolve_generation_empty(server):
    result = await server.evolve_generation()
    assert "error" in result
    assert result["error"] == "No population initialized"

@pytest.mark.asyncio
async def test_evolve_generation(server):
    await server.initialize_population(population_size=4, squad_size=3)
    result = await server.evolve_generation()
    
    assert result["status"] == "success"
    assert result["generation"] == 1
    assert "best_fitness" in result
    assert "average_fitness" in result
    
    # Check that population was evolved
    assert len(server.population) == 4
    assert server.generation == 1

@pytest.mark.asyncio
async def test_multiple_evolution_cycles(server):
    await server.initialize_population(population_size=4, squad_size=3)
    
    for i in range(3):
        result = await server.evolve_generation()
        assert result["generation"] == i + 1
        assert server.generation == i + 1 