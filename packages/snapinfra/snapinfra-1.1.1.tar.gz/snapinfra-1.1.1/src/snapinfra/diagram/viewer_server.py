"""FastAPI server for interactive diagram viewing."""

import asyncio
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from .renderers import KrokiClient
from rich.console import Console

console = Console()


# Pydantic models
class DiagramData(BaseModel):
    """Diagram data model."""
    id: str
    name: str
    type: str  # mermaid, d2, plantuml, etc.
    source: str
    metadata: Dict[str, Any] = {}


class DiagramCreate(BaseModel):
    """Create diagram request model."""
    name: str
    type: str
    source: str
    metadata: Dict[str, Any] = {}


class DiagramUpdate(BaseModel):
    """Update diagram request model."""
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Global diagram store
diagram_store: Dict[str, DiagramData] = {}

# Global Kroki client
kroki_client: Optional[KrokiClient] = None


def create_viewer_app() -> FastAPI:
    """Create FastAPI application for diagram viewer.

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="SnapInfra Diagram Viewer",
        description="Interactive diagram viewer for infrastructure diagrams",
        version="1.0.0"
    )

    # Get templates directory
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    templates = Jinja2Templates(directory=str(templates_dir))

    # Static files directory
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)

    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Initialize Kroki client
    global kroki_client
    kroki_client = KrokiClient(auto_start=True)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Serve main viewer page."""
        diagrams_list = [
            {"id": d.id, "name": d.name, "type": d.type}
            for d in diagram_store.values()
        ]

        return templates.TemplateResponse(
            "viewer.html",
            {
                "request": request,
                "diagrams": diagrams_list
            }
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        kroki_healthy = await kroki_client.health_check() if kroki_client else False

        return {
            "status": "healthy",
            "kroki": "running" if kroki_healthy else "not running",
            "diagrams_count": len(diagram_store)
        }

    @app.get("/diagrams")
    async def list_diagrams():
        """List all diagrams."""
        return {
            "diagrams": [
                {
                    "id": d.id,
                    "name": d.name,
                    "type": d.type,
                    "created_at": d.metadata.get("created_at", "")
                }
                for d in diagram_store.values()
            ]
        }

    @app.get("/diagram/{diagram_id}")
    async def get_diagram(diagram_id: str):
        """Get diagram data."""
        if diagram_id not in diagram_store:
            raise HTTPException(status_code=404, detail="Diagram not found")

        diagram = diagram_store[diagram_id]
        return diagram.dict()

    @app.post("/diagram")
    async def create_diagram(diagram: DiagramCreate):
        """Create/update diagram."""
        import uuid

        # Generate ID if not provided
        diagram_id = str(uuid.uuid4())

        # Add metadata
        metadata = diagram.metadata or {}
        metadata["created_at"] = datetime.now().isoformat()

        diagram_data = DiagramData(
            id=diagram_id,
            name=diagram.name,
            type=diagram.type,
            source=diagram.source,
            metadata=metadata
        )

        diagram_store[diagram_id] = diagram_data

        return {
            "id": diagram_id,
            "status": "created",
            "url": f"/diagram/{diagram_id}"
        }

    @app.put("/diagram/{diagram_id}")
    async def update_diagram(diagram_id: str, update: DiagramUpdate):
        """Update diagram."""
        if diagram_id not in diagram_store:
            raise HTTPException(status_code=404, detail="Diagram not found")

        diagram = diagram_store[diagram_id]

        if update.source is not None:
            diagram.source = update.source

        if update.metadata is not None:
            diagram.metadata.update(update.metadata)

        diagram.metadata["updated_at"] = datetime.now().isoformat()

        return {"status": "updated", "id": diagram_id}

    @app.delete("/diagram/{diagram_id}")
    async def delete_diagram(diagram_id: str):
        """Delete diagram."""
        if diagram_id not in diagram_store:
            raise HTTPException(status_code=404, detail="Diagram not found")

        del diagram_store[diagram_id]
        return {"status": "deleted", "id": diagram_id}

    @app.get("/render/{diagram_id}/{format}")
    async def render_diagram(diagram_id: str, format: str):
        """Render diagram in specified format using Kroki."""
        if diagram_id not in diagram_store:
            raise HTTPException(status_code=404, detail="Diagram not found")

        diagram = diagram_store[diagram_id]

        if not kroki_client:
            raise HTTPException(
                status_code=503,
                detail="Kroki client not available"
            )

        try:
            # Render using Kroki
            rendered = await kroki_client.render(
                diagram.source,
                diagram.type,
                format
            )

            # Determine content type
            content_types = {
                "svg": "image/svg+xml",
                "png": "image/png",
                "pdf": "application/pdf",
                "jpeg": "image/jpeg"
            }

            content_type = content_types.get(format, "image/svg+xml")

            return Response(content=rendered, media_type=content_type)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Rendering failed: {str(e)}"
            )

    @app.websocket("/ws/{diagram_id}")
    async def websocket_endpoint(websocket: WebSocket, diagram_id: str):
        """WebSocket for live diagram updates."""
        await websocket.accept()

        try:
            while True:
                data = await websocket.receive_json()

                # Update diagram source
                if diagram_id in diagram_store:
                    diagram = diagram_store[diagram_id]
                    diagram.source = data.get("source", diagram.source)
                    diagram.metadata["updated_at"] = datetime.now().isoformat()

                    # Send acknowledgment
                    await websocket.send_json({
                        "status": "updated",
                        "timestamp": diagram.metadata["updated_at"]
                    })

        except Exception as e:
            console.print(f"WebSocket error: {e}", style="red")
        finally:
            await websocket.close()

    @app.get("/export/{diagram_id}/{format}")
    async def export_diagram(diagram_id: str, format: str):
        """Export diagram as downloadable file."""
        if diagram_id not in diagram_store:
            raise HTTPException(status_code=404, detail="Diagram not found")

        diagram = diagram_store[diagram_id]

        if not kroki_client:
            raise HTTPException(
                status_code=503,
                detail="Kroki client not available"
            )

        try:
            # Render using Kroki
            rendered = await kroki_client.render(
                diagram.source,
                diagram.type,
                format
            )

            # Determine content type and filename
            content_types = {
                "svg": "image/svg+xml",
                "png": "image/png",
                "pdf": "application/pdf",
                "jpeg": "image/jpeg"
            }

            content_type = content_types.get(format, "image/svg+xml")
            filename = f"{diagram.name}.{format}"

            return Response(
                content=rendered,
                media_type=content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Export failed: {str(e)}"
            )

    return app


def start_viewer(
    diagrams: List[DiagramData],
    port: int = 8080,
    open_browser: bool = True,
    auto_reload: bool = False
) -> None:
    """Start the diagram viewer server.

    Args:
        diagrams: List of diagrams to load
        port: Port to bind to
        open_browser: Automatically open browser
        auto_reload: Enable auto-reload for development
    """
    # Load diagrams into store
    global diagram_store
    for diagram in diagrams:
        diagram_store[diagram.id] = diagram

    # Create app
    app = create_viewer_app()

    # Open browser
    if open_browser:
        def open_browser_delayed():
            import time
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f"http://localhost:{port}")

        import threading
        threading.Thread(target=open_browser_delayed, daemon=True).start()

    console.print(f"\n[bold green]SnapInfra Diagram Viewer[/bold green]")
    console.print(f"Server starting on http://localhost:{port}")
    console.print("Press CTRL+C to stop\n")

    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=auto_reload
    )


async def start_viewer_async(
    diagrams: List[DiagramData],
    port: int = 8080
) -> None:
    """Start the diagram viewer server (async version).

    Args:
        diagrams: List of diagrams to load
        port: Port to bind to
    """
    # Load diagrams into store
    global diagram_store
    for diagram in diagrams:
        diagram_store[diagram.id] = diagram

    # Create app
    app = create_viewer_app()

    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

    server = uvicorn.Server(config)
    await server.serve()
