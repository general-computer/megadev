import pytest
from megadev.evolution import EvolutionEngine
from megadev.models import AgentConfig, Agent, Squad

@pytest.fixture
def evolution_engine():
    return EvolutionEngine(population_size=4, elite_size=1)

@pytest.fixture
def sample_population(evolution_engine):
    return evolution_engine.create_initial_population()

def test_initial_population_creation(evolution_engine):
    population = evolution_engine.create_initial_population()
    
    assert len(population) == evolution_engine.population_size
    assert all(isinstance(squad, Squad) for squad in population)
    assert all(len(squad.agents) == 5 for squad in population)  # Default squad size

def test_mutation(evolution_engine):
    original_config = AgentConfig(
        learning_rate=0.5,
        attention_span=5,
        memory_capacity=50,
        creativity_factor=0.7,
        risk_tolerance=0.3,
        cooperation_bias=0.8,
        energy_efficiency=0.6,
        adaptation_speed=0.4
    )
    
    mutated_config = evolution_engine.mutate_config(original_config)
    
    # Check bounds
    assert 0.1 <= mutated_config.learning_rate <= 1.0
    assert 1 <= mutated_config.attention_span <= 10
    assert 1 <= mutated_config.memory_capacity <= 100
    assert 0.1 <= mutated_config.creativity_factor <= 1.0

def test_crossover(evolution_engine):
    parent1 = Agent.create_random("Parent1")
    parent2 = Agent.create_random("Parent2")
    
    child = evolution_engine.crossover(parent1, parent2)
    
    assert child.generation == evolution_engine.generation
    assert "Parent1" in child.name and "Parent2" in child.name
    
    # Check that child parameters are between parents
    assert min(parent1.config.learning_rate, parent2.config.learning_rate) <= child.config.learning_rate <= max(parent1.config.learning_rate, parent2.config.learning_rate)

def test_evolution(evolution_engine, sample_population):
    # Set some fitness scores
    for i, squad in enumerate(sample_population):
        squad.fitness_score = float(i)
        for agent in squad.agents:
            agent.fitness_score = float(i)
    
    new_population = evolution_engine.evolve_population(sample_population)
    
    assert len(new_population) == evolution_engine.population_size
    assert evolution_engine.generation == 1
    
    # Check that elite squad was preserved
    best_old_squad = max(sample_population, key=lambda s: s.fitness_score)
    best_new_squad = max(new_population, key=lambda s: s.fitness_score)
    assert best_old_squad.fitness_score <= best_new_squad.fitness_score

def test_multiple_generations(evolution_engine):
    population = evolution_engine.create_initial_population()
    
    for gen in range(3):
        # Set random fitness scores
        for squad in population:
            squad.fitness_score = float(len(squad.agents))
        
        population = evolution_engine.evolve_population(population)
        assert evolution_engine.generation == gen + 1 