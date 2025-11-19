import click
import subprocess

# Parámetros específicos de mi VM
VM_NAME = "bootcamp-davisdev"
ZONE = "northamerica-south1-b"
USER = "davidmurcia001"
IP = "34.51.124.248"
REMOTE_PATH = f"/home/{USER}/code/IngDavidMurcia"

@click.command()
def start():
    """Start your VM"""
    subprocess.run(["gcloud", "compute", "instances", "start", "--zone", ZONE, VM_NAME])

@click.command()
def stop():
    """Stop your VM"""
    subprocess.run(["gcloud", "compute", "instances", "stop", "--zone", ZONE, VM_NAME])

@click.command()
def connect():
    """Connect to your VM in VSCode"""
    subprocess.run([
        "code",
        "--folder-uri",
        f"vscode-remote://ssh-remote+{USER}@{IP}{REMOTE_PATH}"
    ])
