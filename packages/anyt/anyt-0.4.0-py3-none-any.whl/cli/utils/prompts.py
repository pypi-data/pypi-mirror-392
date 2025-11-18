"""Interactive prompt utilities for CLI commands."""

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from cli.models.workspace import Workspace
from cli.models.project import Project

console = Console()


def select_workspace(
    workspaces: list[Workspace],
    preselected_id: int | None = None,
    non_interactive: bool = False,
) -> Workspace:
    """Interactive workspace selection.

    Args:
        workspaces: List of available workspaces
        preselected_id: Optional workspace ID to pre-select
        non_interactive: If True, auto-select first workspace

    Returns:
        Selected workspace

    Raises:
        typer.Exit: If user cancels or no workspaces available
        ValueError: If preselected_id not found
    """
    if not workspaces:
        console.print("[red]Error:[/red] No accessible workspaces found")
        raise typer.Exit(1)

    # Handle preselection
    if preselected_id:
        for ws in workspaces:
            if ws.id == preselected_id:
                console.print(
                    f"[green]✓[/green] Using workspace: {ws.name} ({ws.identifier})"
                )
                return ws
        raise ValueError(f"Workspace {preselected_id} not found")

    # Handle non-interactive mode
    if non_interactive:
        workspace = workspaces[0]
        console.print(
            f"[green]✓[/green] Using workspace: {workspace.name} ({workspace.identifier})"
        )
        return workspace

    # Handle single workspace case
    if len(workspaces) == 1:
        workspace = workspaces[0]
        console.print(
            f"\nFound 1 workspace: [cyan]{workspace.name}[/cyan] ([yellow]{workspace.identifier}[/yellow])"
        )
        confirm = Prompt.ask("Use this workspace?", choices=["Y", "n"], default="Y")
        if confirm.lower() != "y":
            console.print("[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(1)
        return workspace

    # Interactive selection for multiple workspaces
    console.print()
    console.print("[bold cyan]Step 2: Workspace Selection[/bold cyan]")
    console.print()

    table = Table(title="Available Workspaces", show_header=True, header_style="bold")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Name", style="green")
    table.add_column("Identifier", style="yellow", width=12)
    table.add_column("ID", style="dim", width=8)

    for idx, ws in enumerate(workspaces, 1):
        table.add_row(str(idx), ws.name, ws.identifier, str(ws.id))

    console.print(table)
    console.print()

    # Prompt for selection
    choice = Prompt.ask(
        "Which workspace would you like to use?",
        choices=[str(i) for i in range(1, len(workspaces) + 1)],
        default="1",
    )

    selected = workspaces[int(choice) - 1]

    # Show selected workspace and confirm
    console.print()
    console.print(
        f"Selected: [cyan]{selected.name}[/cyan] ([yellow]{selected.identifier}[/yellow])"
    )
    confirm = Prompt.ask("Confirm this workspace?", choices=["Y", "n"], default="Y")

    if confirm.lower() != "y":
        console.print("[yellow]Initialization cancelled[/yellow]")
        raise typer.Exit(1)

    return selected


def select_project(
    projects: list[Project],
    preselected_id: int | None = None,
    non_interactive: bool = False,
) -> Project | None:
    """Interactive project selection.

    Args:
        projects: List of available projects
        preselected_id: Optional project ID to pre-select
        non_interactive: If True, auto-select first project

    Returns:
        Selected project, or None if no projects available

    Raises:
        typer.Exit: If user cancels
        ValueError: If preselected_id not found
    """
    # Handle no projects - return None to signal that default should be created
    if not projects:
        return None

    # Handle preselection
    if preselected_id:
        for proj in projects:
            if proj.id == preselected_id:
                console.print(f"[green]✓[/green] Using project: {proj.name}")
                return proj
        raise ValueError(f"Project {preselected_id} not found")

    # Handle non-interactive mode
    if non_interactive:
        project = projects[0]
        console.print(f"[green]✓[/green] Using project: {project.name}")
        return project

    # Handle single project case
    if len(projects) == 1:
        project = projects[0]
        console.print(f"\nFound 1 project: [cyan]{project.name}[/cyan]")
        if project.description:
            console.print(f"  [dim]{project.description}[/dim]")
        confirm = Prompt.ask("Use this project?", choices=["Y", "n"], default="Y")
        if confirm.lower() != "y":
            console.print("[yellow]Initialization cancelled[/yellow]")
            raise typer.Exit(1)
        return project

    # Interactive selection for multiple projects
    console.print()
    console.print("[bold cyan]Step 3: Project Selection[/bold cyan]")
    console.print()

    table = Table(title="Available Projects", show_header=True, header_style="bold")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Name", style="green")
    table.add_column("Description", style="dim")

    for idx, proj in enumerate(projects, 1):
        desc = proj.description or ""
        # Truncate long descriptions
        if len(desc) > 50:
            desc = desc[:47] + "..."
        table.add_row(str(idx), proj.name, desc)

    console.print(table)
    console.print()

    # Prompt for selection
    choice = Prompt.ask(
        "Which project would you like to use?",
        choices=[str(i) for i in range(1, len(projects) + 1)],
        default="1",
    )

    selected = projects[int(choice) - 1]

    # Show selected project and confirm
    console.print()
    console.print(f"Selected: [cyan]{selected.name}[/cyan]")
    if selected.description:
        console.print(f"  [dim]{selected.description}[/dim]")
    confirm = Prompt.ask("Confirm this project?", choices=["Y", "n"], default="Y")

    if confirm.lower() != "y":
        console.print("[yellow]Initialization cancelled[/yellow]")
        raise typer.Exit(1)

    return selected
