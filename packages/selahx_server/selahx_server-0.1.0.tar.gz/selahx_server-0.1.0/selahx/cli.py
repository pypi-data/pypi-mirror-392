import typer
from .server import server_cli

app = typer.Typer(
    help="selahx — Remote Access Tool — Fast and lightweight CLI experience.",
    add_completion=False
)

# Server command
@app.command("slx", help="Start the selahx server.")
def run_server(
    host: str = typer.Option("0.0.0.0", "--host", help="Host for the server (default: listen on all interfaces)"),
    key_file: str = typer.Option(..., "--key-file", help="Path to the temporary SSH private key (e.g. ./key.pem)"),
    port: int = typer.Option(..., "--port", help="Local port for the server (e.g. 1221)"),
    ssh_host: str = typer.Option(..., "--ssh-host", help="SSH host (e.g. ubuntu@ec2-xx-xxx-xx-xxx.compute-1.amazonaws.com)")
):
    """
    Launch the selahx server which listens for client connections and establishes
    a reverse SSH tunnel automatically once a client connects.
    """
    typer.secho(f"[SERVER] Starting on {host}:{port}", fg=typer.colors.GREEN)
    typer.secho(f"[SERVER] Using SSH key: {key_file}", fg=typer.colors.YELLOW)
    typer.secho(f"[SERVER] Will connect to SSH host: {ssh_host}", fg=typer.colors.CYAN)
    server_cli(host=host, port=port, key_file=key_file, ssh_host=ssh_host)

# Entry point
if __name__ == "__main__":
    app()