"""Architecture as Code methods for interactive chat - to be integrated."""

async def _generate_architecture_diagram_new(self, plan: Dict, project_description: str) -> Optional[Dict]:
    """Generate Architecture as Code diagrams (Python, Mermaid, D2) using AI and new generators."""
    from pathlib import Path
    import json
    from rich.prompt import Confirm

    console.print("\n[bold cyan]Generating Architecture as Code (Python + Mermaid + D2)...[/bold cyan]")

    try:
        # Import new AaC generators
        from ..diagram.generators import MingrammerGenerator, MermaidGenerator, D2Generator
        from ..diagram.models import DiagramData, Component, Connection
        from ..prompts.system_prompts import ARCHITECTURE_AS_CODE_PROMPT

        # Get backend
        if not self.config or not hasattr(self.config, 'backends') or 'groq' not in self.config.backends:
            console.print("Groq backend not configured. Skipping architecture diagram.", style="yellow")
            return None

        groq_config = self.config.backends['groq']
        if not groq_config.api_key or groq_config.api_key.startswith('$'):
            console.print("Groq API key not set. Skipping architecture diagram.", style="yellow")
            return None

        # Import and configure Groq backend
        from ..backends.groq import GroqBackend
        from ..types.models import Message

        groq_backend = GroqBackend(api_key=groq_config.api_key)

        # Create Architecture as Code prompt
        tech_stack = ", ".join(plan.get('tech_stack', []))
        project_type = plan.get('project_type', 'application')
        database = plan.get('database', 'none')

        aac_prompt = f"""
{ARCHITECTURE_AS_CODE_PROMPT}

PROJECT DETAILS:
Description: {project_description}
Type: {project_type}
Technology Stack: {tech_stack}
Database: {database}
Number of Files: {len(plan.get('files', []))}

Generate a comprehensive Architecture as Code for this project with:
1. DiagramData JSON model
2. Python code (mingrammer/diagrams)
3. Mermaid diagram code
4. D2 diagram code

Return the response in this format:

## DiagramData JSON
```json
{{...}}
```

## Python (mingrammer/diagrams)
```python
...
```

## Mermaid
```mermaid
...
```

## D2
```d2
...
```
"""

        # Generate using AI
        system_message = Message(
            role="system",
            content="You are an expert in Architecture as Code generation. Generate comprehensive diagrams in multiple formats."
        )
        conversation = groq_backend.chat(
            groq_config.default_model or "llama-3.1-70b-versatile",
            system_message
        )

        console.print("AI is generating architecture diagrams in 3 formats...", style="dim cyan")
        response = await conversation.send(aac_prompt)

        if not response or not response.full_output:
            console.print("Failed to generate architecture diagrams", style="red")
            return None

        # Parse the response to extract different sections
        import re
        full_response = response.full_output

        # Extract DiagramData JSON
        json_match = re.search(r'```json\s*(.*?)```', full_response, re.DOTALL)
        diagram_data_json = None
        if json_match:
            try:
                diagram_data_json = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                console.print("Failed to parse DiagramData JSON", style="yellow")

        # Extract Python code
        python_match = re.search(r'```python\s*(.*?)```', full_response, re.DOTALL)
        python_code = python_match.group(1).strip() if python_match else None

        # Extract Mermaid code
        mermaid_match = re.search(r'```mermaid\s*(.*?)```', full_response, re.DOTALL)
        mermaid_code = mermaid_match.group(1).strip() if mermaid_match else None

        # Extract D2 code
        d2_match = re.search(r'```d2\s*(.*?)```', full_response, re.DOTALL)
        d2_code = d2_match.group(1).strip() if d2_match else None

        # Save generated diagrams
        diagrams_saved = 0
        project_name = plan.get('name', 'architecture')

        if python_code:
            python_file = Path(f"{project_name}_architecture.py")
            python_file.write_text(python_code, encoding='utf-8')
            console.print(f"✓ Saved Python diagram: {python_file}", style="green")
            diagrams_saved += 1

        if mermaid_code:
            mermaid_file = Path(f"{project_name}_architecture.mmd")
            mermaid_file.write_text(mermaid_code, encoding='utf-8')
            console.print(f"✓ Saved Mermaid diagram: {mermaid_file}", style="green")
            diagrams_saved += 1

        if d2_code:
            d2_file = Path(f"{project_name}_architecture.d2")
            d2_file.write_text(d2_code, encoding='utf-8')
            console.print(f"✓ Saved D2 diagram: {d2_file}", style="green")
            diagrams_saved += 1

        if diagrams_saved > 0:
            console.print(f"\n[bold green]Architecture as Code generated successfully![/bold green]")
            console.print(f"Generated {diagrams_saved} diagram format(s)")

            # Ask if user wants to view diagrams
            if Confirm.ask("\nView diagrams in interactive viewer?", default=True):
                await self._open_diagram_viewer([
                    (f"{project_name}_architecture.mmd", "mermaid"),
                    (f"{project_name}_architecture.d2", "d2")
                ])

        # Return diagram data for compatibility
        return {
            "diagram_data_json": diagram_data_json,
            "python_code": python_code,
            "mermaid_code": mermaid_code,
            "d2_code": d2_code,
            "files_saved": diagrams_saved
        }

    except Exception as e:
        console.print(f"Error generating architecture diagrams: {e}", style="red")
        import traceback
        traceback.print_exc()
        return None


async def _open_diagram_viewer(self, diagram_files: list):
    """Open diagram files in the interactive viewer.

    Args:
        diagram_files: List of (file_path, diagram_type) tuples
    """
    try:
        from ..diagram.viewer_server import start_viewer, DiagramData as ViewerDiagramData
        from pathlib import Path
        import uuid

        viewer_diagrams = []

        for file_path, diagram_type in diagram_files:
            file_path = Path(file_path)
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')

                viewer_diagram = ViewerDiagramData(
                    id=str(uuid.uuid4()),
                    name=file_path.stem,
                    type=diagram_type,
                    source=content,
                    metadata={"file_path": str(file_path)}
                )

                viewer_diagrams.append(viewer_diagram)

        if viewer_diagrams:
            console.print(f"\n[cyan]Starting diagram viewer with {len(viewer_diagrams)} diagram(s)...[/cyan]")
            start_viewer(viewer_diagrams, port=8080, open_browser=True)
        else:
            console.print("[yellow]No diagram files found to view[/yellow]")

    except Exception as e:
        console.print(f"Error opening diagram viewer: {e}", style="red")


def _create_architecture_diagram_prompt_new(self, plan: Dict, project_description: str) -> str:
    """Create prompt for Architecture as Code generation using the new system prompts."""
    from ..prompts.system_prompts import ARCHITECTURE_AS_CODE_PROMPT

    tech_stack = ", ".join(plan.get('tech_stack', []))
    project_type = plan.get('project_type', 'application')
    database = plan.get('database', 'none')

    return f"""
{ARCHITECTURE_AS_CODE_PROMPT}

PROJECT DETAILS:
Description: {project_description}
Type: {project_type}
Technology Stack: {tech_stack}
Database: {database}
Docker Needed: {plan.get('docker_needed', False)}
Number of Components: {len(plan.get('files', []))}

Generate a comprehensive architecture diagram for this {project_type} using Architecture as Code.

Provide ALL of the following:
1. DiagramData JSON model with components and connections
2. Python code using mingrammer/diagrams (with AWS/Azure/GCP icons if applicable)
3. Mermaid diagram code (for GitHub/documentation)
4. D2 diagram code (modern format)

Make sure all component types use exact strings from the component type reference (aws_*, azure_*, gcp_*, k8s_*, etc.).
"""
