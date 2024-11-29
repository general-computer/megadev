#!/usr/bin/env python3
import asyncio
import click
from rich.console import Console
from rich.table import Table
from typing import Optional

from megadev import AiderSession, load_tasks, save_tasks

console = Console()

@click.group()
def cli():
    """MegaDev CLI - Manage your AI development agents"""
    pass

@cli.command()
@click.argument('repo_url')
@click.argument('task')
def create(repo_url: str, task: str):
    """Create a new agent for a repository"""
    session = AiderSession(repo_url, task)
    session.start()
    console.print(f"[green]Created new agent for {repo_url}[/green]")
    console.print(f"Task: {task}")

@cli.command()
@click.argument('agent_id')
def delete(agent_id: str):
    """Delete an existing agent"""
    tasks = load_tasks()
    if agent_id in tasks:
        del tasks[agent_id]
        save_tasks(tasks)
        console.print(f"[green]Deleted agent {agent_id}[/green]")
    else:
        console.print(f"[red]Agent {agent_id} not found[/red]")

@cli.command()
def list():
    """List all active agents"""
    tasks = load_tasks()
    
    if not tasks:
        console.print("[yellow]No active agents found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent ID")
    table.add_column("Repository")
    table.add_column("Task")
    table.add_column("Status")

    for agent_id, task in tasks.items():
        table.add_row(
            agent_id,
            task['repo_url'],
            task['description'],
            task.get('status', 'Running')
        )
    
    console.print(table)

@cli.command()
@click.option('--agent-id', help='Monitor specific agent')
def monitor(agent_id: Optional[str] = None):
    """Monitor agent output"""
    tasks = load_tasks()
    
    if agent_id and agent_id not in tasks:
        console.print(f"[red]Agent {agent_id} not found[/red]")
        return

    try:
        while True:
            if agent_id:
                # Monitor specific agent
                task = tasks[agent_id]
                console.print(f"Agent {agent_id}: {task.get('last_output', 'No output')}")
            else:
                # Monitor all agents
                for aid, task in tasks.items():
                    console.print(f"Agent {aid}: {task.get('last_output', 'No output')}")
            
            console.print("[dim]Press Ctrl+C to stop monitoring[/dim]")
            asyncio.sleep(5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]")

if __name__ == '__main__':
    cli()
