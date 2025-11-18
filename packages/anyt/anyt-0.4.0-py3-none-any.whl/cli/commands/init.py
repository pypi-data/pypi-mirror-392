"""Initialize AnyTask workspace in current directory."""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from cli.config import WorkspaceConfig
from cli.utils.shell import detect_shell
from cli.utils.api_key import (
    validate_api_key_format,
    get_api_key_setup_message,
    get_invalid_api_key_message,
)
from cli.utils.prompts import select_workspace, select_project

console = Console()


def display_completion_summary(
    workspace_name: str,
    workspace_identifier: str | None,
    project_name: str | None,
    config_path: Path,
    api_url: str,
) -> None:
    """Display completion summary after successful init.

    Args:
        workspace_name: Name of the selected workspace
        workspace_identifier: Workspace identifier (e.g., DEV, PROJ)
        project_name: Name of the selected project (if any)
        config_path: Path to saved config file
        api_url: API URL being used
    """
    console.print()
    console.print("━" * 70)
    console.print("[green]✓ Initialization Complete![/green]")
    console.print("━" * 70)
    console.print()

    console.print(f"Configuration saved to: [cyan]{config_path}[/cyan]")
    console.print()

    # Setup summary table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value", style="white")

    # Format workspace display
    workspace_display = workspace_name
    if workspace_identifier:
        workspace_display = f"{workspace_name} ({workspace_identifier})"

    table.add_row("Workspace:", workspace_display)
    if project_name:
        table.add_row("Project:", project_name)
    table.add_row("API URL:", api_url)
    table.add_row("Config directory:", str(config_path.parent))

    console.print(table)
    console.print()

    # Next steps
    console.print("[bold]Next Steps:[/bold]")
    console.print()
    console.print("  1. View your tasks:       [cyan]anyt task list[/cyan]")
    console.print("  2. View your board:       [cyan]anyt board[/cyan]")
    console.print('  3. Create a task:         [cyan]anyt task add "Task title"[/cyan]')
    console.print(
        f"  4. Pick a task to work:   [cyan]anyt task pick {workspace_identifier or 'WORK'}-1[/cyan]"
    )
    console.print()
    console.print(
        "Need help? Run [cyan]anyt --help[/cyan] or visit [dim]https://docs.anyt.dev[/dim]"
    )
    console.print()


def init(
    workspace_id: Annotated[
        int | None,
        typer.Option("--workspace-id", "-w", help="Workspace ID to link to"),
    ] = None,
    workspace_name: Annotated[
        str | None,
        typer.Option("--workspace-name", "-n", help="Workspace name (optional)"),
    ] = None,
    identifier: Annotated[
        str | None,
        typer.Option(
            "--identifier", "-i", help="Workspace identifier (e.g., DEV, PROJ)"
        ),
    ] = None,
    project_id: Annotated[
        int | None,
        typer.Option("--project-id", "-p", help="Project ID to use"),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option("--dir", "-d", help="Directory to initialize (default: current)"),
    ] = None,
    dev: Annotated[
        bool,
        typer.Option("--dev", help="Use development API (http://localhost:8000)"),
    ] = False,
    non_interactive: Annotated[
        bool,
        typer.Option(
            "--non-interactive",
            "-y",
            help="Non-interactive mode: auto-select first workspace/project",
        ),
    ] = False,
) -> None:
    """Initialize AnyTask in the current directory.

    Requires ANYT_API_KEY environment variable to be set.
    Creates .anyt/ directory structure and anyt.json configuration.

    Examples:
        # Interactive mode (default)
        anyt init

        # Non-interactive with auto-selection
        anyt init --non-interactive
        anyt init -y

        # Specify workspace and project explicitly
        anyt init --workspace-id 101 --project-id 5

        # Non-interactive with explicit workspace
        anyt init -y --workspace-id 101

        # CI/CD usage
        export ANYT_API_KEY=anyt_agent_...
        anyt init --non-interactive --workspace-id 101 --project-id 5

        # Development API
        anyt init --dev
    """
    try:
        # Show welcome message
        console.print()
        console.print(
            Panel(
                "[bold cyan]Welcome to AnyTask CLI![/bold cyan]\n\n"
                "Let's get you set up with a workspace.",
                border_style="cyan",
            )
        )
        console.print()

        # Determine target directory
        target_dir = directory or Path.cwd()
        target_dir = target_dir.resolve()

        # Create .anyt directory if it doesn't exist
        anyt_dir = target_dir / ".anyt"
        if not anyt_dir.exists():
            anyt_dir.mkdir(parents=True)
            console.print("[green]✓[/green] Created .anyt/ directory")
        else:
            console.print("[dim].anyt/ directory already exists[/dim]")

        # Create subdirectories
        subdirs = ["workflows", "tasks"]
        for subdir in subdirs:
            subdir_path = anyt_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True)
                console.print(f"[green]✓[/green] Created .anyt/{subdir}/ directory")

        # Check if workspace config already exists
        existing_config = WorkspaceConfig.load(target_dir)
        if existing_config:
            console.print(
                f"[yellow]Warning:[/yellow] Workspace config already exists: {existing_config.name}"
            )
            console.print(f"Workspace ID: {existing_config.workspace_id}")
            if existing_config.workspace_identifier:
                console.print(f"Identifier: {existing_config.workspace_identifier}")

            if non_interactive:
                console.print(
                    "[yellow]Non-interactive mode: Skipping existing configuration[/yellow]"
                )
                console.print("[green]✓[/green] Using existing workspace configuration")
                raise typer.Exit(0)

            reset = Prompt.ask(
                "Do you want to reset it?", choices=["y", "N"], default="N"
            )

            if reset.lower() != "y":
                console.print("[green]✓[/green] Using existing workspace configuration")
                raise typer.Exit(0)

        # Check for ANYT_API_KEY environment variable
        api_key = os.getenv("ANYT_API_KEY")

        # Check for ANYT_API_KEY environment variable first
        if not api_key:
            console.print()
            console.print(
                Panel(
                    "[bold yellow]Step 1: Authentication[/bold yellow]",
                    border_style="yellow",
                )
            )
            console.print()

            # Detect shell and get setup instructions
            shell_name, config_path = detect_shell()
            setup_message = get_api_key_setup_message(shell_name, str(config_path))
            console.print(setup_message)
            console.print()
            raise typer.Exit(1)

        # Validate API key format
        if not validate_api_key_format(api_key):
            console.print()
            error_message = get_invalid_api_key_message(api_key)
            console.print(error_message)
            console.print()
            raise typer.Exit(1)

        # Determine API URL
        # Priority: ANYT_API_URL env var > --dev flag > production default
        api_url = os.getenv("ANYT_API_URL")
        if not api_url:
            api_url = "http://localhost:8000" if dev else "https://api.anyt.dev"

        # If workspace_id is provided, create workspace config manually
        if workspace_id:
            ws_config = WorkspaceConfig(
                workspace_id=workspace_id,
                name=workspace_name or f"Workspace {workspace_id}",
                api_url=api_url,
                workspace_identifier=identifier,
                current_project_id=None,
                last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            ws_config.save(target_dir)

            console.print(f"[green]✓[/green] Linked to workspace ID {workspace_id}")
            console.print(
                f"[green]✓[/green] Saved config to {target_dir}/.anyt/anyt.json"
            )

            # Display completion summary
            display_completion_summary(
                workspace_name=ws_config.name,
                workspace_identifier=ws_config.workspace_identifier,
                project_name=None,  # No project when using manual workspace_id
                config_path=target_dir / ".anyt" / "anyt.json",
                api_url=api_url,
            )
        else:
            # API key is set - automatically fetch and setup workspace
            console.print(
                "[cyan]ANYT_API_KEY detected - setting up workspace...[/cyan]"
            )

            async def setup_workspace() -> None:
                try:
                    # Initialize API clients directly
                    from cli.client.workspaces import WorkspacesAPIClient
                    from cli.client.projects import ProjectsAPIClient

                    ws_client = WorkspacesAPIClient(base_url=api_url, api_key=api_key)
                    proj_client = ProjectsAPIClient(base_url=api_url, api_key=api_key)

                    # Fetch available workspaces
                    console.print()
                    console.print("[green]✓[/green] Authenticated successfully")
                    console.print("Fetching accessible workspaces...")
                    workspaces = await ws_client.list_workspaces()

                    if not workspaces:
                        console.print(
                            "[red]Error:[/red] No accessible workspaces found for this API key"
                        )
                        console.print(
                            "\nAPI keys require at least one workspace to be created first."
                        )
                        console.print(
                            "Please create a workspace using the web interface at [cyan]https://anyt.dev[/cyan]"
                        )
                        raise typer.Exit(1)

                    # Interactive workspace selection
                    workspace = select_workspace(
                        workspaces,
                        preselected_id=None,  # workspace_id already handled above
                        non_interactive=non_interactive,
                    )

                    # Interactive project selection
                    console.print("Fetching projects...")
                    try:
                        # Fetch existing projects
                        projects = await proj_client.list_projects(workspace.id)

                        # Interactive project selection
                        selected_project = select_project(
                            projects,
                            preselected_id=project_id,
                            non_interactive=non_interactive,
                        )

                        # Create default project if none exist
                        if selected_project is None:
                            console.print(
                                "[yellow]No projects found in workspace.[/yellow]"
                            )
                            console.print(
                                f"Creating default project: [cyan]{workspace.name}[/cyan]..."
                            )

                            from cli.models.project import ProjectCreate

                            selected_project = await proj_client.create_project(
                                workspace.id,
                                ProjectCreate(
                                    name=workspace.name,
                                    description="Default project",
                                ),
                            )
                            console.print(
                                f"[green]✓[/green] Created project: {selected_project.name}"
                            )

                        current_project_id = selected_project.id

                    except Exception as e:
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not fetch or create project: {e}"
                        )
                        current_project_id = None

                    # Create and save workspace config (no api_key stored)
                    ws_config = WorkspaceConfig(
                        workspace_id=workspace.id,
                        name=workspace.name,
                        api_url=api_url,
                        workspace_identifier=workspace.identifier,
                        current_project_id=current_project_id,
                        last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    ws_config.save(target_dir)

                    console.print(
                        f"[green]✓[/green] Saved config to {target_dir}/.anyt/anyt.json"
                    )

                    # Display completion summary
                    display_completion_summary(
                        workspace_name=workspace.name,
                        workspace_identifier=workspace.identifier,
                        project_name=selected_project.name
                        if selected_project
                        else None,
                        config_path=target_dir / ".anyt" / "anyt.json",
                        api_url=api_url,
                    )

                except Exception as e:
                    if not isinstance(e, typer.Exit):
                        console.print(
                            f"[red]Error:[/red] Failed to setup workspace: {e}"
                        )
                        raise typer.Exit(1)
                    raise

            asyncio.run(setup_workspace())

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        raise  # Re-raise typer.Exit to preserve exit code
