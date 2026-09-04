import typer

from gkh_cli import context_of

app = typer.Typer(help="Demo group.")


@app.callback()
def main() -> None:
    """Demo group."""


@app.command()
def show(ctx: typer.Context) -> None:
    """Print the shared context this plugin received."""
    shared = context_of(ctx)

    typer.echo(f"url={shared.url} token={shared.token} output={shared.output.value}")


@app.command()
def fail() -> None:
    """Exit with a non-default status."""

    raise typer.Exit(code=7)
