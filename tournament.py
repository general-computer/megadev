import asyncio
import random
import time
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from dataclasses import dataclass
from typing import List
import random
import numpy as np

console = Console()

@dataclass
class Agent:
    name: str
    learning_rate: float
    memory_capacity: float
    attention_span: float
    creativity_factor: float
    cooperation_bias: float
    risk_tolerance: float
    adaptation_speed: float
    energy_efficiency: float

    @classmethod
    def create_random(cls, name: str):
        return cls(
            name=name,
            learning_rate=random.random(),
            memory_capacity=random.random(),
            attention_span=random.random(),
            creativity_factor=random.random(),
            cooperation_bias=random.random(),
            risk_tolerance=random.random(),
            adaptation_speed=random.random(),
            energy_efficiency=random.random()
        )

@dataclass
class Squad:
    name: str
    agents: List[Agent]
    fitness_score: float = 0.0

    @classmethod
    def create_random(cls, name: str, size: int = 5):
        return cls(
            name=name,
            agents=[Agent.create_random(f"{name}-Agent{i}") for i in range(size)]
        )

class CodingTournament:
    def __init__(self, initial_devs: int = 100):
        self.initial_devs = initial_devs
        self.round = 0
        self.squads: List[Squad] = []
        self.hall_of_fame: List[Dict] = []
        
    def calculate_challenge_score(self, squad: Squad) -> float:
        """Calculate squad performance in current challenge"""
        base_score = 0
        
        for agent in squad.agents:
            # Different challenges favor different attributes
            if self.round % 3 == 0:  # Algorithm challenges
                score = (agent.config.learning_rate * 0.4 +
                        agent.config.memory_capacity * 0.4 +
                        agent.config.attention_span * 0.2)
            elif self.round % 3 == 1:  # System design challenges
                score = (agent.config.creativity_factor * 0.3 +
                        agent.config.cooperation_bias * 0.4 +
                        agent.config.risk_tolerance * 0.3)
            else:  # Debug challenges
                score = (agent.config.adaptation_speed * 0.5 +
                        agent.config.energy_efficiency * 0.3 +
                        agent.config.attention_span * 0.2)
            
            # Add some randomness
            score *= random.uniform(0.8, 1.2)
            base_score += score
        
        return base_score / len(squad.agents)

    async def initialize_tournament(self):
        """Set up initial population of dev squads"""
        squad_size = 5
        num_squads = self.initial_devs // squad_size
        
        with console.status("[bold green]Gathering developers worldwide..."):
            squad_names = [f"Squad-{i}" for i in range(num_squads)]
            self.squads = [Squad.create_random(name, squad_size) for name in squad_names]
            await asyncio.sleep(1)  # For dramatic effect

    async def run_challenge_round(self) -> List[Squad]:
        """Run one round of the tournament"""
        self.round += 1
        challenge_types = ["Algorithm Battle", "System Design Showdown", "Debug Death Match"]
        challenge = challenge_types[self.round % 3]
        
        console.print(f"\n[bold red]Round {self.round}: {challenge}")
        console.print(f"[bold yellow]{len(self.squads)} squads remaining")
        
        # Evaluate all squads
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            console=console
        ) as progress:
            task = progress.add_task("Evaluating squads...", total=len(self.squads))
            
            for squad in self.squads:
                squad.fitness_score = self.calculate_challenge_score(squad)
                progress.advance(task)
                await asyncio.sleep(0.01)  # For dramatic effect
        
        # Sort and eliminate bottom 50%
        self.squads.sort(key=lambda s: s.fitness_score, reverse=True)
        eliminated = len(self.squads) // 2
        self.squads = self.squads[:-eliminated]
        
        # Record top performers
        if len(self.squads) <= 100:
            top_squad = self.squads[0]
            self.hall_of_fame.append({
                "round": self.round,
                "name": top_squad.name,
                "score": top_squad.fitness_score,
                "challenge": challenge
            })
        
        return self.squads

    def display_leaderboard(self):
        """Show current top performers"""
        table = Table(title=f"Top Squads - Round {self.round}")
        table.add_column("Rank", justify="right", style="cyan")
        table.add_column("Squad", style="magenta")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Agents", justify="right", style="yellow")
        
        for i, squad in enumerate(self.squads[:10], 1):
            table.add_row(
                str(i),
                squad.name,
                f"{squad.fitness_score:.3f}",
                str(len(squad.agents))
            )
        
        console.print(table)

    def display_hall_of_fame(self):
        """Display tournament highlights"""
        table = Table(title="Tournament Hall of Fame")
        table.add_column("Round", justify="right", style="cyan")
        table.add_column("Challenge", style="red")
        table.add_column("Squad", style="magenta")
        table.add_column("Score", justify="right", style="green")
        
        for entry in self.hall_of_fame:
            table.add_row(
                str(entry["round"]),
                entry["challenge"],
                entry["name"],
                f"{entry['score']:.3f}"
            )
        
        console.print(Panel(table, title="[bold yellow]Hall of Fame"))

async def main():
    console.clear()
    console.print("[bold red]MEGADEV TOURNAMENT[/bold red]", justify="center")
    console.print("[bold yellow]Million Developer Challenge[/bold yellow]\n", justify="center")
    
    tournament = CodingTournament()
    await tournament.initialize_tournament()
    
    while len(tournament.squads) > 1:
        await tournament.run_challenge_round()
        tournament.display_leaderboard()
        
        if len(tournament.squads) <= 100:
            console.print(f"\n[bold red]!!! FINAL STAGES !!![/bold red]")
        
        # Dramatic pause between rounds
        await asyncio.sleep(2)
    
    # Tournament complete
    console.print("\n[bold green]Tournament Complete![/bold green]")
    console.print(f"[bold yellow]Winner: {tournament.squads[0].name}")
    console.print(f"Final Score: {tournament.squads[0].fitness_score:.3f}\n")
    
    tournament.display_hall_of_fame()

if __name__ == "__main__":
    asyncio.run(main()) 
