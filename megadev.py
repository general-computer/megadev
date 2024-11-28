import os
import json
import uuid
import subprocess
import tempfile
from pathlib import Path
import shutil
from time import sleep
import threading
import datetime
import queue
import logging

# Basic logging setup
logging.basicConfig(level=logging.INFO)

# Global variables
CONFIG_FILE = Path("config.json")
aider_sessions = {}

class AiderSession:
    def __init__(self, workspace_path, task):
        self.workspace_path = workspace_path
        self.task = task
        self.process = None
        self.output = ""
        self.session_id = str(uuid.uuid4())[:8]

    def start(self):
        try:
            cmd = f'aider --mini --message "{self.task}"'
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=self.workspace_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start output reading thread
            threading.Thread(target=self._read_output, daemon=True).start()
            return True
        except Exception as e:
            logging.error(f"Failed to start aider: {e}")
            return False

    def _read_output(self):
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            self.output += line

    def cleanup(self):
        if self.process:
            self.process.terminate()

def load_tasks():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tasks": [], "agents": {}, "repository_url": ""}

def save_tasks(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def create_agent(repository_url: str, task: str):
    try:
        # Generate agent ID and create workspace
        agent_id = str(uuid.uuid4())
        workspace = Path(tempfile.mkdtemp(prefix=f"agent_{agent_id}_"))
        repo_dir = workspace / "repo"
        repo_dir.mkdir()

        # Clone repository
        os.chdir(repo_dir)
        subprocess.check_call(f"git clone {repository_url} .", shell=True)
        
        # Create and checkout new branch
        branch_name = f"agent-{agent_id[:8]}"
        subprocess.check_call(f"git checkout -b {branch_name}", shell=True)

        # Start aider session
        session = AiderSession(str(repo_dir), task)
        if not session.start():
            shutil.rmtree(workspace)
            return None

        # Store session
        aider_sessions[agent_id] = session

        # Update config
        tasks_data = load_tasks()
        tasks_data['agents'][agent_id] = {
            'workspace': str(workspace),
            'repo_path': str(repo_dir),
            'task': task,
            'status': 'active',
            'created_at': datetime.datetime.now().isoformat()
        }
        save_tasks(tasks_data)

        return agent_id

    except Exception as e:
        logging.error(f"Error creating agent: {e}")
        return None

def delete_agent(agent_id):
    try:
        tasks_data = load_tasks()
        if agent_id in tasks_data['agents']:
            # Cleanup session
            if agent_id in aider_sessions:
                aider_sessions[agent_id].cleanup()
                del aider_sessions[agent_id]

            # Remove workspace
            workspace = tasks_data['agents'][agent_id]['workspace']
            if os.path.exists(workspace):
                shutil.rmtree(workspace)

            # Remove from config
            del tasks_data['agents'][agent_id]
            save_tasks(tasks_data)
            return True
    except Exception as e:
        logging.error(f"Error deleting agent: {e}")
    return False

def main_loop():
    while True:
        try:
            tasks_data = load_tasks()
            
            # Update output for each agent
            for agent_id, session in aider_sessions.items():
                if agent_id in tasks_data['agents']:
                    tasks_data['agents'][agent_id]['aider_output'] = session.output
            
            save_tasks(tasks_data)
            sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            sleep(30)

if __name__ == "__main__":
    main_loop()
