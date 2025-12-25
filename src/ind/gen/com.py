''' 
Module: com.py
Author: Marc Zepeda
Created: 2025-4-01
Description: Command Line Interaction

Usage:
[Common commands for fastq files]
- access(): make all files and subdirectories accessible on Harvard FASRC

[Environment variable management]
- detect_shell(): Attempt to detect the user's shell from the SHELL environment variable (i.e., 'bash' or 'zsh').
- create_export_var(): create a persistent export variable by adding it to the user's shell config.
- view_export_vars(): View the current export variables in the user's shell config.
'''

# Import packages
import subprocess
import os
from pathlib import Path
from typing import Literal

# Environment variable management
home = Path.home()
shell_configs = {
    'bash': home / '.bashrc',
    'zsh': home / '.zshrc'
}

def detect_shell():
    """
    detect_shell(): Attempt to detect the user's shell from the SHELL environment variable (i.e., 'bash' or 'zsh').
    """
    shell_path = os.environ.get("SHELL", "")
    shell_name = Path(shell_path).name.lower()
    if shell_name in {"bash", "zsh"}:
        return shell_name
    raise ValueError(f"Unsupported or undetected shell: {shell_path}")            

def create_export_var(name: str, pt: str, shell: Literal['bash','zsh']=None):
    """
    create_export_var(): create a persistent export variable by adding it to the user's shell config.
    
    Parameters:
    name (str): The name of the environment variable (e.g. "MYPROJ").
    path (str): The full path the variable should point to.
    shell (str, optional): The shell config to use ('bash' or 'zsh'). If None, auto-detects the shell.
    """
    shell = shell or detect_shell()

    config_file = shell_configs.get(shell)
    if config_file is None:
        raise ValueError(f"Unsupported shell: {shell}")

    # Clean path and environment variable name
    pt = os.path.abspath(os.path.expanduser(pt))
    name = name.upper()

    export_line = f'export {name}="{pt}"\n'

    # Prevent duplicate entries
    if config_file.exists():
        with open(config_file, 'r') as f:
            if export_line.strip() in f.read():
                print(f"Environment variable {name} already exists in {config_file}")
                return

    # Append the new variable
    with open(config_file, 'a') as f:
        f.write(f'\n# Added by script\n{export_line}')

    print(f"Added environment variable: {name}={pt}")
    print(f"Run `source {config_file}` or restart your terminal to apply it.")

def view_export_vars(shell: Literal['bash','zsh']=None):
    """
    view_export_vars(): View the current export variables in the user's shell config.
    
    Parameters:
    shell (str, optional): The shell config to check ('bash' or 'zsh'). If None, auto-detects the shell.
    """
    shell = shell or detect_shell()

    config_file = shell_configs.get(shell)
    if not config_file or not config_file.exists():
        print(f"Shell config file not found for {shell}")
        return

    print(f"Exported environment variables in {config_file}:\n")

    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("export "):
                print(line)