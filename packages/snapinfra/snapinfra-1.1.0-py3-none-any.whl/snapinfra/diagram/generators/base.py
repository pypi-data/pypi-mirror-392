"""Base diagram generator abstract class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..models import DiagramData, Component, Connection


class DiagramGenerator(ABC):
    """Abstract base class for diagram generators."""

    def __init__(self, diagram_data: Optional[DiagramData] = None):
        """Initialize diagram generator.

        Args:
            diagram_data: DiagramData model containing components and connections
        """
        self.diagram_data = diagram_data or DiagramData()

    @abstractmethod
    def generate(self) -> str:
        """Generate diagram code from DiagramData model.

        Returns:
            String containing the diagram code in the specific format
        """
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Return the diagram format name.

        Returns:
            Format name (e.g., 'mermaid', 'd2', 'python-diagrams')
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this format.

        Returns:
            File extension (e.g., '.mmd', '.d2', '.py')
        """
        pass

    def set_diagram_data(self, diagram_data: DiagramData) -> None:
        """Set the diagram data.

        Args:
            diagram_data: DiagramData model
        """
        self.diagram_data = diagram_data

    def add_component(self, component: Component) -> None:
        """Add a component to the diagram.

        Args:
            component: Component to add
        """
        self.diagram_data.components.append(component)

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the diagram.

        Args:
            connection: Connection to add
        """
        self.diagram_data.connections.append(connection)

    def get_component_by_id(self, component_id: str) -> Optional[Component]:
        """Get component by ID.

        Args:
            component_id: Component ID

        Returns:
            Component if found, None otherwise
        """
        for component in self.diagram_data.components:
            if component.id == component_id:
                return component
        return None

    def get_components_by_type(self, component_type: str) -> List[Component]:
        """Get all components of a specific type.

        Args:
            component_type: Component type

        Returns:
            List of components matching the type
        """
        return [c for c in self.diagram_data.components if c.type == component_type]

    def get_connections_for_component(self, component_id: str) -> List[Connection]:
        """Get all connections involving a component.

        Args:
            component_id: Component ID

        Returns:
            List of connections
        """
        return [
            c for c in self.diagram_data.connections
            if c.source == component_id or c.target == component_id
        ]

    def _sanitize_identifier(self, text: str) -> str:
        """Sanitize text to be used as an identifier.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        # Replace spaces and special characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized

    def _get_cloud_provider(self, component_type: str) -> Optional[str]:
        """Determine cloud provider from component type.

        Args:
            component_type: Component type

        Returns:
            Cloud provider name ('aws', 'azure', 'gcp') or None
        """
        type_lower = component_type.lower()
        if type_lower.startswith('aws_') or 'aws' in type_lower:
            return 'aws'
        elif type_lower.startswith('azure_') or 'azure' in type_lower:
            return 'azure'
        elif type_lower.startswith('gcp_') or 'google' in type_lower:
            return 'gcp'
        elif type_lower.startswith('k8s_') or 'kubernetes' in type_lower:
            return 'k8s'
        return None

    def validate(self) -> List[str]:
        """Validate the diagram data.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if there are components
        if not self.diagram_data.components:
            errors.append("No components in diagram")

        # Check for duplicate component IDs
        component_ids = [c.id for c in self.diagram_data.components]
        if len(component_ids) != len(set(component_ids)):
            errors.append("Duplicate component IDs found")

        # Validate connections reference existing components
        for conn in self.diagram_data.connections:
            if not self.get_component_by_id(conn.source):
                errors.append(f"Connection references non-existent source: {conn.source}")
            if not self.get_component_by_id(conn.target):
                errors.append(f"Connection references non-existent target: {conn.target}")

        return errors
