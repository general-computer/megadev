import pytest
from megadev.models import AgentConfig, Agent, Squad

def test_agent_config_creation():
    config = AgentConfig(
        learning_rate=0.5,
        attention_span=5,
        memory_capacity=50,
        creativity_factor=0.7,
        risk_tolerance=0.3,
        cooperation_bias=0.8,
        energy_efficiency=0.6,
        adaptation_speed=0.4
    )
    
    assert 0 <= config.learning_rate <= 1
    assert 1 <= config.attention_span <= 10
    assert 1 <= config.memory_capacity <= 100
    assert 0 <= config.creativity_factor <= 1

def test_agent_random_creation():
    agent = Agent.create_random("TestAgent")
    
    assert agent.name == "TestAgent"
    assert agent.id is not None
    assert isinstance(agent.config, AgentConfig)
    assert agent.fitness_score == 0.0
    assert agent.generation == 0
    assert agent.created_at is not None

def test_squad_random_creation():
    squad = Squad.create_random("TestSquad", size=3)
    
    assert squad.name == "TestSquad"
    assert squad.id is not None
    assert len(squad.agents) == 3
    assert squad.fitness_score == 0.0
    assert squad.generation == 0
    assert squad.created_at is not None
    
    # Check that all agents are unique
    agent_ids = [agent.id for agent in squad.agents]
    assert len(set(agent_ids)) == len(agent_ids) 