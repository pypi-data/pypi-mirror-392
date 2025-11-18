"""Enhanced diagram generation CLI with Architecture as Code support."""

import asyncio
import json
from pathlib import Path
from typing import Optional, List
import uuid

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..diagram.generators import MingrammerGenerator, MermaidGenerator, D2Generator
from ..diagram.models import DiagramData, Component, Connection
from ..diagram.renderers import KrokiClient, KrokiServerManager
from ..diagram.viewer_server import start_viewer, DiagramData as ViewerDiagramData

console = Console()


@click.group(name='diagram')
def diagram_group():
    """Generate architecture diagrams with Architecture as Code."""
    pass


@diagram_group.command('generate')
@click.argument('description', nargs=-1)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output directory for generated diagrams'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['all', 'python', 'mermaid', 'd2']),
    default='all',
    help='Diagram format to generate'
)
@click.option(
    '--view', '-v',
    is_flag=True,
    help='Open in interactive viewer after generation'
)
@click.option(
    '--name', '-n',
    help='Diagram name'
)
def generate_diagram(
    description: tuple,
    output: Optional[Path],
    format: str,
    view: bool,
    name: Optional[str]
):
    """Generate architecture diagrams from description.

    Examples:
        snapinfra diagram generate "3-tier AWS architecture" --view
        snapinfra diagram generate "k8s microservices" --format mermaid
        snapinfra diagram generate "AWS VPC with ECS and RDS" --output ./diagrams
    """
    if not description:
        console.print("[red]Please provide a diagram description[/red]")
        return

    description_text = ' '.join(description)
    diagram_name = name or description_text[:50]

    console.print(Panel(
        f"[bold cyan]Generating Architecture Diagram[/bold cyan]\n\n"
        f"Description: {description_text}\n"
        f"Format: {format}",
        expand=False
    ))

    # Create example diagram data
    diagram_data = create_example_diagram_data(diagram_name, description_text)

    # Output directory
    output_dir = output or Path(f"./diagrams/{diagram_name.replace(' ', '_')}")
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    try:
        # Generate diagrams
        if format in ['all', 'python']:
            console.print("\n[cyan]Generating Python (mingrammer/diagrams)...[/cyan]")
            python_file = generate_mingrammer(diagram_data, output_dir)
            generated_files.append(python_file)
            console.print(f"[green]✓[/green] Generated: {python_file}")

        if format in ['all', 'mermaid']:
            console.print("\n[cyan]Generating Mermaid...[/cyan]")
            mermaid_file = generate_mermaid(diagram_data, output_dir)
            generated_files.append(mermaid_file)
            console.print(f"[green]✓[/green] Generated: {mermaid_file}")

        if format in ['all', 'd2']:
            console.print("\n[cyan]Generating D2...[/cyan]")
            d2_file = generate_d2(diagram_data, output_dir)
            generated_files.append(d2_file)
            console.print(f"[green]✓[/green] Generated: {d2_file}")

        # Display summary
        console.print("\n[bold green]Generation Complete![/bold green]")
        console.print(f"\nGenerated {len(generated_files)} file(s) in: {output_dir}")

        for file in generated_files:
            console.print(f"  • {file.name}")

        # Open viewer if requested
        if view:
            console.print("\n[cyan]Starting diagram viewer...[/cyan]")
            asyncio.run(open_viewer(diagram_data, diagram_name, generated_files))

    except Exception as e:
        console.print(f"\n[red]Error generating diagrams: {e}[/red]")
        raise


@diagram_group.command('view')
@click.argument('diagram_files', nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option('--port', '-p', default=8080, help='Server port')
def view_diagrams(diagram_files: tuple, port: int):
    """View diagram files in interactive viewer.

    Examples:
        snapinfra diagram view diagram.mmd
        snapinfra diagram view diagram.mmd diagram.d2 --port 8081
    """
    if not diagram_files:
        console.print("[red]Please provide at least one diagram file[/red]")
        return

    console.print(f"[cyan]Loading {len(diagram_files)} diagram(s)...[/cyan]")

    viewer_diagrams = []

    for file_path in diagram_files:
        file_path = Path(file_path)

        try:
            content = file_path.read_text(encoding='utf-8')

            # Determine diagram type from extension
            ext = file_path.suffix.lower()
            diagram_type = {
                '.mmd': 'mermaid',
                '.d2': 'd2',
                '.puml': 'plantuml',
                '.py': 'python-diagrams'
            }.get(ext, 'mermaid')

            viewer_diagram = ViewerDiagramData(
                id=str(uuid.uuid4()),
                name=file_path.stem,
                type=diagram_type,
                source=content,
                metadata={"file_path": str(file_path)}
            )

            viewer_diagrams.append(viewer_diagram)
            console.print(f"[green]✓[/green] Loaded: {file_path.name}")

        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Failed to load {file_path.name}: {e}")

    if not viewer_diagrams:
        console.print("[red]No diagrams loaded[/red]")
        return

    console.print(f"\n[bold green]Starting viewer on port {port}...[/bold green]")

    try:
        start_viewer(viewer_diagrams, port=port, open_browser=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]Viewer stopped[/yellow]")


@diagram_group.command('kroki')
@click.argument('action', type=click.Choice(['start', 'stop', 'status']))
@click.option('--port', '-p', default=8000, help='Kroki server port')
def manage_kroki(action: str, port: int):
    """Manage Kroki diagram rendering server.

    Examples:
        snapinfra diagram kroki start
        snapinfra diagram kroki status
        snapinfra diagram kroki stop
    """
    if action == 'start':
        console.print(f"[cyan]Starting Kroki server on port {port}...[/cyan]")
        success = KrokiServerManager.start_kroki(port)

        if success:
            console.print("[green]✓ Kroki server started successfully[/green]")
        else:
            console.print("[red]✗ Failed to start Kroki server[/red]")

    elif action == 'stop':
        console.print("[cyan]Stopping Kroki server...[/cyan]")
        success = KrokiServerManager.stop_kroki()

        if success:
            console.print("[green]✓ Kroki server stopped[/green]")
        else:
            console.print("[yellow]Kroki server was not running[/yellow]")

    elif action == 'status':
        docker_available = KrokiServerManager.is_docker_available()
        kroki_running = KrokiServerManager.is_kroki_running(port)

        table = Table(title="Kroki Server Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        table.add_row("Docker", "✓ Available" if docker_available else "✗ Not available")
        table.add_row("Kroki Server", f"✓ Running on port {port}" if kroki_running else "✗ Not running")

        console.print(table)


@diagram_group.command('example')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output directory')
def generate_example(output: Optional[Path]):
    """Generate example diagrams for all formats.

    Examples:
        snapinfra diagram example
        snapinfra diagram example --output ./examples
    """
    output_dir = output or Path("./example_diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print("[bold cyan]Generating Example Diagrams[/bold cyan]\n")

    # Generate Python example
    python_gen = MingrammerGenerator()
    python_code = python_gen.generate_example()
    python_file = output_dir / "example_aws_3tier.py"
    python_file.write_text(python_code, encoding='utf-8')
    console.print(f"[green]✓[/green] Python (mingrammer): {python_file}")

    # Generate Mermaid example
    mermaid_gen = MermaidGenerator()
    mermaid_code = mermaid_gen.generate_example()
    mermaid_file = output_dir / "example_aws_3tier.mmd"
    mermaid_file.write_text(mermaid_code, encoding='utf-8')
    console.print(f"[green]✓[/green] Mermaid: {mermaid_file}")

    # Generate D2 example
    d2_gen = D2Generator()
    d2_code = d2_gen.generate_example()
    d2_file = output_dir / "example_aws_3tier.d2"
    d2_file.write_text(d2_code, encoding='utf-8')
    console.print(f"[green]✓[/green] D2: {d2_file}")

    console.print(f"\n[bold green]Examples generated in: {output_dir}[/bold green]")


# Helper functions

def create_example_diagram_data(name: str, description: str) -> DiagramData:
    """Create example diagram data for demonstration."""
    diagram = DiagramData(metadata={"name": name, "description": description})

    # Create example components (3-tier architecture)
    alb = Component(
        id="alb_1",
        name="Application Load Balancer",
        type="aws_alb",
        properties={"cluster": "VPC"}
    )

    app1 = Component(
        id="app_1",
        name="App Server 1",
        type="aws_ecs",
        properties={"cluster": "App Tier"}
    )

    app2 = Component(
        id="app_2",
        name="App Server 2",
        type="aws_ecs",
        properties={"cluster": "App Tier"}
    )

    db = Component(
        id="db_1",
        name="Primary RDS",
        type="aws_rds",
        properties={"cluster": "Data Tier"}
    )

    s3 = Component(
        id="s3_1",
        name="S3 Storage",
        type="aws_s3",
        properties={}
    )

    diagram.components = [alb, app1, app2, db, s3]

    # Create connections
    diagram.connections = [
        Connection(source="alb_1", target="app_1", properties={"label": "http"}),
        Connection(source="alb_1", target="app_2", properties={"label": "http"}),
        Connection(source="app_1", target="db_1", properties={"label": "sql"}),
        Connection(source="app_2", target="db_1", properties={"label": "sql"}),
        Connection(source="app_1", target="s3_1", properties={"label": "s3 api"}),
        Connection(source="app_2", target="s3_1", properties={"label": "s3 api"}),
    ]

    return diagram


def generate_mingrammer(diagram_data: DiagramData, output_dir: Path) -> Path:
    """Generate Python code using mingrammer/diagrams."""
    generator = MingrammerGenerator(diagram_data)
    code = generator.generate()

    output_file = output_dir / "architecture.py"
    output_file.write_text(code, encoding='utf-8')

    return output_file


def generate_mermaid(diagram_data: DiagramData, output_dir: Path) -> Path:
    """Generate Mermaid diagram."""
    generator = MermaidGenerator(diagram_data)
    code = generator.generate()

    output_file = output_dir / "architecture.mmd"
    output_file.write_text(code, encoding='utf-8')

    return output_file


def generate_d2(diagram_data: DiagramData, output_dir: Path) -> Path:
    """Generate D2 diagram."""
    generator = D2Generator(diagram_data)
    code = generator.generate()

    output_file = output_dir / "architecture.d2"
    output_file.write_text(code, encoding='utf-8')

    return output_file


async def open_viewer(
    diagram_data: DiagramData,
    diagram_name: str,
    generated_files: List[Path]
):
    """Open diagram viewer with generated files."""
    viewer_diagrams = []

    for file_path in generated_files:
        try:
            content = file_path.read_text(encoding='utf-8')

            # Determine diagram type from extension
            ext = file_path.suffix.lower()
            diagram_type = {
                '.py': 'python-diagrams',
                '.mmd': 'mermaid',
                '.d2': 'd2',
                '.puml': 'plantuml'
            }.get(ext, 'mermaid')

            viewer_diagram = ViewerDiagramData(
                id=str(uuid.uuid4()),
                name=f"{diagram_name} ({ext[1:].upper()})",
                type=diagram_type,
                source=content,
                metadata={"file_path": str(file_path)}
            )

            viewer_diagrams.append(viewer_diagram)

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load {file_path.name}: {e}[/yellow]")

    if viewer_diagrams:
        start_viewer(viewer_diagrams, port=8080, open_browser=True)


def add_diagram_commands(cli_group):
    """Add diagram commands to main CLI group."""
    cli_group.add_command(diagram_group)
