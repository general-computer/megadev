from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from .models import Agent, Squad, Division, Department
from .organization import Division, Department

@dataclass
class SimulationClock:
    """Manages simulation time progression"""
    current_time: datetime
    time_scale: float = 1.0  # 1.0 means real-time, 2.0 means twice as fast
    tick_interval: timedelta = timedelta(minutes=15)
    
    def tick(self):
        """Advance simulation time by one tick interval"""
        self.current_time += self.tick_interval * self.time_scale
        return self.current_time

class SimulationEngine:
    """Manages the simulation state and progression"""
    def __init__(self):
        self.clock = SimulationClock(current_time=datetime.now())
        self.departments: List[Department] = []
        self.paused: bool = False
        
    def add_department(self, department: Department):
        self.departments.append(department)
        
    def tick(self):
        """Process one simulation tick"""
        if self.paused:
            return
            
        current_time = self.clock.tick()
        
        # Update all agents in the organization
        for department in self.departments:
            for division in department.divisions:
                for squad in division.squads:
                    for agent in squad.agents:
                        # Update human needs based on time delta
                        time_delta = self.clock.tick_interval.total_seconds() / 3600  # Convert to hours
                        agent.needs.update(time_delta)
                        
    def pause(self):
        """Pause the simulation"""
        self.paused = True
        
    def resume(self):
        """Resume the simulation"""
        self.paused = False
