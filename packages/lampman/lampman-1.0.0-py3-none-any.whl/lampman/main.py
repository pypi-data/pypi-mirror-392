import typer

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import rich

app = typer.Typer()


@app.command("new")
def new(version: str):
    ver = version.split("-")
    if platform.system() == "Windows":
        pip_executable = Path(os.getcwd(), ".lampenv", "Scripts", "pip.exe")
    else:
        pip_executable = Path(os.getcwd(), ".lampenv", "Scripts", "pip")
    if ver[0] == "lamp":
        print("Creating MathLamp environment, please wait...")
        subprocess.run(
            [sys.executable, "-m", "virtualenv", str(Path(os.getcwd(), ".lampenv"))]
        )
        print("Installing MathLamp package")
        subprocess.run([pip_executable, "install", f"MathLamp=={ver[1]}"])

@app.command("remove")
def remove():
    env_path = Path(os.getcwd(), ".lampenv")
    if env_path.is_dir():
        print("Removing MathLamp environment")
        shutil.rmtree(str(env_path))
    else:
        rich.print("[bold red]Failed to remove MathLamp environment, folder does not exist[/bold red]")

if __name__ == "__main__":
    app()
