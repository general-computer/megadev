import pytest
from datetime import datetime, timedelta
from src.megadev.simulation import SimulationClock, SimulationEngine
from src.megadev.models import Agent, Squad
from src.megadev.organization import Division, Department

def test_simulation_clock():
    clock = SimulationClock(current_time=datetime(2024, 1, 1, 9, 0))
    
    # Test normal tick
    new_time = clock.tick()
    assert new_time == datetime(2024, 1, 1, 9, 15)
    
    # Test time scaling
    clock.time_scale = 2.0
    new_time = clock.tick()
    assert new_time == datetime(2024, 1, 1, 9, 45)

def test_simulation_engine():
    engine = SimulationEngine()
    
    # Create test organization structure
    agent = Agent.create_random("Test Agent")
    squad = Squad.create_random("Test Squad", size=1)
    squad.agents = [agent]
    
    division = Division(name="Test Division")
    division.squads.append(squad)
    
    department = Department(name="Test Department")
    department.divisions.append(division)
    
    engine.add_department(department)
    
    # Test initial state
    assert not engine.paused
    initial_hunger = agent.needs.hunger
    
    # Test tick updates needs
    engine.tick()
    assert agent.needs.hunger > initial_hunger
    
    # Test pause/resume
    engine.pause()
    current_hunger = agent.needs.hunger
    engine.tick()
    assert agent.needs.hunger == current_hunger  # Should not change while paused
    
    engine.resume()
    engine.tick()
    assert agent.needs.hunger > current_hunger  # Should change after resume
