from google.genai import types
import subprocess,os
import os
import subprocess
from pathlib import Path

def execute_network_commands(command: str):
    # Locate this file’s directory → agenticai/functions
    base_dir = Path(__file__).resolve().parent.parent.parent  # root of package
    shell_path = base_dir / "shell.py"

    if not shell_path.exists():
        return f"❌ Error: shell.py not found at {shell_path}"

    # user’s working dir (where their project files live)
    user_dir = os.getcwd()

    output = subprocess.run(
        ['python', str(shell_path), command, '1'],
        cwd=user_dir,  # user workspace for file access
        timeout=30,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    return f"STDOUT:\n{output.stdout}\nSTDERR:\n{output.stderr}"


schema_execute_network_commands=types.FunctionDeclaration(
    name="execute_network_commands",
    description="Executes VALLAIPALLAM(VNAS) network commands",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            'command':types.Schema(
                type=types.Type.STRING,
                description='The VNAS COMMAND to be executed.'
            )
        }
    )
)