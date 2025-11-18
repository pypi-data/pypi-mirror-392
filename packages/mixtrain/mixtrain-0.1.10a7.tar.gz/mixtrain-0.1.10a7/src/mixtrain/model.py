"""Mixtrain Model CLI Commands"""

import json
import subprocess
import tempfile
from typing import Optional

import typer
from rich import print as rprint
from rich.table import Table

from mixtrain import MixClient

app = typer.Typer(help="Manage models.", invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command(name="list")
def list_models(
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Filter by type: 'native', 'provider', or None for all"
    ),
):
    """List all models in the current workspace."""
    try:
        response = MixClient().list_models(provider=provider)
        models = response.get("data", [])

        if not models:
            rprint("[yellow]No models found.[/yellow]")
            rprint("Use 'mixtrain model create' to create a native model or 'mixtrain model register' to register a provider model.")
            return

        rprint("[bold]Models:[/bold]")
        table = Table("Name", "Type", "Provider", "Description", "Created At")
        for model in models:
            model_type = "Native" if model.get("model_type") == "native" else "Provider"
            provider_name = model.get("provider", "-")
            description = model.get("description", "")
            if len(description) > 50:
                description = description[:50] + "..."
            table.add_row(
                model.get("name", ""),
                model_type,
                provider_name,
                description,
                model.get("created_at", ""),
            )
        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="catalog")
def catalog(
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Filter by provider name"
    ),
):
    """Browse available models from provider catalog."""
    try:
        response = MixClient().get_catalog_models(provider=provider)
        models = response.get("data", [])

        if not models:
            rprint("[yellow]No catalog models found.[/yellow]")
            return

        rprint("[bold]Available Provider Models:[/bold]")
        table = Table("Provider", "Model ID", "Description")
        for model in models:
            description = model.get("description", "")
            if len(description) > 60:
                description = description[:60] + "..."
            table.add_row(
                model.get("provider", ""),
                model.get("model_id", ""),
                description,
            )
        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="get")
def get_model(model_name: str = typer.Argument(..., help="Model name")):
    """Get details of a specific model."""
    try:
        result = MixClient().get_model(model_name)
        model = result.get("data", {})

        rprint(f"[bold]Model: {model.get('name')}[/bold]")
        rprint(f"Type: {model.get('model_type')}")
        rprint(f"Description: {model.get('description')}")

        if model.get("model_type") == "provider":
            rprint(f"Provider: {model.get('provider')}")
            rprint(f"Provider Model ID: {model.get('provider_model_id')}")
        else:
            rprint(f"Entrypoint: {model.get('entrypoint', 'N/A')}")

        rprint(f"Created: {model.get('created_at')}")
        rprint(f"Updated: {model.get('updated_at')}")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="create")
def create_model(
    file_paths: list[str] = typer.Argument(..., help="Files or folders to upload"),
    name: str = typer.Option(..., "--name", "-n", help="Model name"),
    description: str = typer.Option("", "--description", "-d", help="Model description"),
    entrypoint: Optional[str] = typer.Option(None, "--entrypoint", "-e", help="Entrypoint file"),
):
    """Create a native model from local files/folders.

    Examples:
      mixtrain model create model.py --name my-model
      mixtrain model create src/ requirements.txt --name my-model --entrypoint src/main.py
    """
    try:
        import os

        # Validate all paths exist
        for path in file_paths:
            if not os.path.exists(path):
                rprint(f"[red]Error:[/red] Path not found: {path}")
                raise typer.Exit(1)

        result = MixClient().create_model(
            name=name,
            file_paths=file_paths,
            description=description,
            entrypoint=entrypoint,
        )
        model_data = result.get("data", {})
        rprint(f"[green]Successfully created model '{model_data.get('name')}'[/green]")
        rprint(f"  Uploaded {len(file_paths)} file(s)/folder(s)")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="register")
def register_model(
    name: str = typer.Option(..., "--name", "-n", help="Model name in workspace"),
    provider: str = typer.Option(..., "--provider", "-p", help="Provider name (e.g., openai, anthropic)"),
    provider_model_id: str = typer.Option(..., "--provider-model-id", "-m", help="Model ID from provider"),
    description: str = typer.Option("", "--description", "-d", help="Model description"),
):
    """Register a provider model.

    Examples:
      mixtrain model register --name gpt4 --provider openai --provider-model-id gpt-4
      mixtrain model register --name claude --provider anthropic --provider-model-id claude-3-opus-20240229
    """
    try:
        result = MixClient().register_model(
            name=name,
            provider=provider,
            provider_model_id=provider_model_id,
            description=description,
        )
        model_data = result.get("data", {})
        rprint(f"[green]Successfully registered model '{model_data.get('name')}'[/green]")
        rprint(f"  Provider: {provider}")
        rprint(f"  Provider Model ID: {provider_model_id}")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="delete")
def delete_model(
    model_name: str = typer.Argument(..., help="Model name"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a model."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete model '{model_name}'?")
            if not confirm:
                rprint("Deletion cancelled.")
                return

        MixClient().delete_model(model_name)
        rprint(f"[green]Successfully deleted model '{model_name}'[/green]")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="code")
def get_code(model_name: str = typer.Argument(..., help="Model name")):
    """View model source code."""
    try:
        result = MixClient().get_model_code(model_name)
        code_data = result.get("data", {})
        code = code_data.get("code", "")

        if not code:
            rprint("[yellow]No code found for this model.[/yellow]")
            return

        rprint(f"[bold]Code for model '{model_name}':[/bold]\n")
        rprint(code)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="edit")
def edit_code(model_name: str = typer.Argument(..., help="Model name")):
    """Edit model source code interactively."""
    try:
        # Get current code
        result = MixClient().get_model_code(model_name)
        code_data = result.get("data", {})
        current_code = code_data.get("code", "")

        if not current_code:
            rprint("[yellow]No code found for this model.[/yellow]")
            return

        # Create temporary file with current code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(current_code)
            tmp_path = tmp.name

        # Open editor
        editor = subprocess.os.environ.get("EDITOR", "vim")
        subprocess.call([editor, tmp_path])

        # Read edited code
        with open(tmp_path, "r") as f:
            new_code = f.read()

        # Clean up
        subprocess.os.unlink(tmp_path)

        # Check if code changed
        if new_code == current_code:
            rprint("[yellow]No changes made.[/yellow]")
            return

        # Update model code
        MixClient().update_model_code(model_name, new_code)
        rprint(f"[green]Successfully updated code for model '{model_name}'[/green]")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="run")
def run_model(
    model_name: str = typer.Argument(..., help="Model name"),
    inputs: Optional[str] = typer.Option(None, "--inputs", "-i", help="JSON input data"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="JSON config data"),
):
    """Run model inference.

    Examples:
      mixtrain model run my-model --inputs '{"text": "Hello world"}'
      mixtrain model run my-model --inputs '{"prompt": "Tell me a joke"}' --config '{"temperature": 0.8}'
    """
    try:
        # Parse JSON inputs and config
        input_data = json.loads(inputs) if inputs else {}
        config_data = json.loads(config) if config else {}

        result = MixClient().run_model(model_name, inputs=input_data, config=config_data)
        run_data = result.get("data", {})

        rprint(f"[green]Model run started (Run #{run_data.get('run_number')})[/green]")
        rprint(f"Status: {run_data.get('status')}")

        # Display outputs if available
        outputs = run_data.get("outputs")
        if outputs:
            rprint(f"\nOutputs:")
            rprint(json.dumps(outputs, indent=2))

    except json.JSONDecodeError as e:
        rprint(f"[red]Error:[/red] Invalid JSON: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="runs")
def list_runs(model_name: str = typer.Argument(..., help="Model name")):
    """List all runs for a model."""
    try:
        response = MixClient().list_model_runs(model_name)
        runs = response.get("data", [])

        if not runs:
            rprint("[yellow]No runs found for this model.[/yellow]")
            return

        rprint(f"[bold]Model Runs (Total: {len(runs)}):[/bold]")
        table = Table("Run #", "Status", "Started", "Completed")
        for run in runs:
            table.add_row(
                str(run.get("run_number", "")),
                run.get("status", ""),
                run.get("started_at", "N/A"),
                run.get("completed_at", "N/A"),
            )
        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="run-status")
def update_run_status(
    model_name: str = typer.Argument(..., help="Model name"),
    run_number: int = typer.Argument(..., help="Run number"),
    status: str = typer.Option(..., "--status", "-s", help="New status (pending, running, completed, failed)"),
    outputs: Optional[str] = typer.Option(None, "--outputs", "-o", help="JSON outputs"),
    error: Optional[str] = typer.Option(None, "--error", "-e", help="Error message"),
):
    """Update model run status.

    Examples:
      mixtrain model run-status my-model 1 --status completed --outputs '{"result": "success"}'
      mixtrain model run-status my-model 2 --status failed --error "Out of memory"
    """
    try:
        # Parse JSON outputs
        outputs_data = json.loads(outputs) if outputs else None

        result = MixClient().update_model_run_status(
            model_name, run_number, status, outputs=outputs_data, error=error
        )
        run_data = result.get("data", {})
        rprint(f"[green]Updated run #{run_number} status to '{run_data.get('status')}'[/green]")

    except json.JSONDecodeError as e:
        rprint(f"[red]Error:[/red] Invalid JSON: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="logs")
def get_logs(
    model_name: str = typer.Argument(..., help="Model name"),
    run_number: Optional[int] = typer.Argument(None, help="Run number (defaults to latest)"),
):
    """View model run logs.

    Examples:
      mixtrain model logs my-model         # View latest run logs
      mixtrain model logs my-model 5       # View logs for run #5
    """
    try:
        result = MixClient().get_model_run_logs(model_name, run_number)
        logs_data = result.get("data", {})
        logs = logs_data.get("logs", "")

        if not logs:
            rprint("[yellow]No logs found.[/yellow]")
            return

        rprint(f"[bold]Logs for model '{model_name}' (Run #{run_number or 'latest'}):[/bold]\n")
        rprint(logs)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
