import typer
from .client import client_cli
from .save_files import copy_ec2

app = typer.Typer(
    help="selahx — Remote Access Tool — Fast and lightweight CLI experience.",
    add_completion=False
)

# Client command
@app.command("client", help="Start the selahx client.")
def run_client(
    username: str = typer.Option(..., "--username", help="Username for the client session"),
    port: int = typer.Option(..., "--port", help="Server port to connect to")
):
    """
    Launch the selahx client which connects to the server and sets up communication
    over the specified port.
    """
    typer.secho(f"[CLIENT] Starting as user '{username}'", fg=typer.colors.GREEN)
    typer.secho(f"[CLIENT] Connecting to server port {port}", fg=typer.colors.CYAN)
    client_cli(username=username, port=port)

# Save files from EC2 to Local
@app.command("save", help="Copy EC2 home directory to local machine")
def copy_ec2_command(
    key: str = typer.Option(..., "--key-file", help="Path to the temporary SSH private key (e.g. ./key.pem)"),
    host: str = typer.Option(..., "--ssh-host", help="SSH host (e.g. ubuntu@ec2-xx-xxx-xx-xxx.compute-1.amazonaws.com)"),
    dest: str = typer.Option(..., "--dest", help="Local destination directory (e.g. ~/Downloads/test)")
):
    copy_ec2(key_file=key, ec2_host=host, local_dest=dest)


# Entry point
if __name__ == "__main__":
    app()