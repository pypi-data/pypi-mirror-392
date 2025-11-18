"""D2 diagram generator for modern diagram scripting."""

from typing import Dict, List
from .base import DiagramGenerator
from ..models import DiagramData, Component, Connection


class D2Generator(DiagramGenerator):
    """Generator for D2 diagrams (modern diagram scripting language)."""

    # Shape mappings for D2
    SHAPE_MAPPINGS = {
        "database": "cylinder",
        "aws_rds": "cylinder",
        "aws_dynamodb": "cylinder",
        "azure_sql": "cylinder",
        "gcp_cloud_sql": "cylinder",
        "storage": "cloud",
        "aws_s3": "cloud",
        "azure_storage": "cloud",
        "gcp_storage": "cloud",
        "lambda": "hexagon",
        "aws_lambda": "hexagon",
        "azure_functions": "hexagon",
        "gcp_functions": "hexagon",
        "queue": "queue",
        "aws_sqs": "queue",
        "load_balancer": "rectangle",
        "compute": "rectangle",
    }

    # Color mappings for different providers
    COLOR_MAPPINGS = {
        "aws": {"fill": "#FF9900", "stroke": "#232F3E"},
        "azure": {"fill": "#0078D4", "stroke": "#002050"},
        "gcp": {"fill": "#4285F4", "stroke": "#1A73E8"},
        "k8s": {"fill": "#326CE5", "stroke": "#1A4D99"},
        "database": {"fill": "#4CAF50", "stroke": "#2E7D32"},
        "storage": {"fill": "#2196F3", "stroke": "#1565C0"},
        "compute": {"fill": "#FF9800", "stroke": "#E65100"},
        "network": {"fill": "#9C27B0", "stroke": "#6A1B9A"},
    }

    def __init__(self, diagram_data: DiagramData = None):
        """Initialize D2 generator.

        Args:
            diagram_data: DiagramData model
        """
        super().__init__(diagram_data)
        self.clusters: Dict[str, List[Component]] = {}
        self.indent_level = 0

    def get_format(self) -> str:
        """Return format name."""
        return "d2"

    def get_file_extension(self) -> str:
        """Return file extension."""
        return ".d2"

    def generate(self) -> str:
        """Generate D2 diagram syntax.

        Returns:
            D2 code string
        """
        # Reset state
        self.clusters = {}
        self.indent_level = 0

        # Organize components into clusters
        self._organize_clusters()

        # Build the D2 code
        code_parts = []

        # Add title if present
        title = self.diagram_data.metadata.get("name", "")
        if title:
            code_parts.append(f'title: "{title}" {{')
            code_parts.append('  near: top-center')
            code_parts.append('}')
            code_parts.append('')

        # Generate clusters and components
        if self.clusters:
            code_parts.extend(self._generate_clusters())
        else:
            code_parts.extend(self._generate_components())

        # Generate connections
        code_parts.append("")
        code_parts.append("# Connections")
        code_parts.extend(self._generate_connections())

        return "\n".join(code_parts)

    def _organize_clusters(self) -> None:
        """Organize components into logical clusters."""
        for component in self.diagram_data.components:
            cluster_name = component.properties.get("cluster", None)

            if cluster_name:
                if cluster_name not in self.clusters:
                    self.clusters[cluster_name] = []
                self.clusters[cluster_name].append(component)

    def _generate_components(self) -> List[str]:
        """Generate component definitions without clusters.

        Returns:
            List of code lines
        """
        lines = []

        for component in self.diagram_data.components:
            component_def = self._format_component(component, indent=0)
            lines.append(component_def)

        return lines

    def _generate_clusters(self) -> List[str]:
        """Generate clusters with components.

        Returns:
            List of code lines
        """
        lines = []

        # Generate unclustered components first
        unclustered = [
            c for c in self.diagram_data.components
            if not c.properties.get("cluster")
        ]

        for component in unclustered:
            component_def = self._format_component(component, indent=0)
            lines.append(component_def)

        if unclustered:
            lines.append("")

        # Generate clusters
        for cluster_name, components in self.clusters.items():
            cluster_id = self._sanitize_identifier(cluster_name)

            lines.append(f'{cluster_id}: {{')
            lines.append(f'  label: "{cluster_name}"')
            lines.append('')

            for component in components:
                component_def = self._format_component(component, indent=2)
                lines.append(component_def)

            lines.append('}')
            lines.append('')

        return lines

    def _format_component(self, component: Component, indent: int = 0) -> str:
        """Format a component definition.

        Args:
            component: Component to format
            indent: Indentation level (spaces)

        Returns:
            Formatted component string
        """
        indent_str = " " * indent
        comp_id = self._sanitize_identifier(component.id)
        label = component.name

        # Get shape
        shape = self._get_shape_for_component(component)

        # Get style
        style = self._get_style_for_component(component)

        # Build component definition
        parts = [f'{indent_str}{comp_id}: "{label}" {{']

        if shape != "rectangle":
            parts.append(f'{indent_str}  shape: {shape}')

        if style:
            for key, value in style.items():
                parts.append(f'{indent_str}  style.{key}: "{value}"')

        parts.append(f'{indent_str}}}')

        return "\n".join(parts)

    def _get_shape_for_component(self, component: Component) -> str:
        """Get the D2 shape for a component.

        Args:
            component: Component

        Returns:
            Shape name
        """
        type_lower = component.type.lower()

        # Check direct mappings
        for key, shape in self.SHAPE_MAPPINGS.items():
            if key in type_lower:
                return shape

        # Default shape
        return "rectangle"

    def _get_style_for_component(self, component: Component) -> Dict[str, str]:
        """Get style properties for a component.

        Args:
            component: Component

        Returns:
            Dictionary of style properties
        """
        style = {}
        type_lower = component.type.lower()

        # Determine provider or category
        provider = self._get_cloud_provider(component.type)

        if provider and provider in self.COLOR_MAPPINGS:
            colors = self.COLOR_MAPPINGS[provider]
            style.update(colors)
        else:
            # Categorize by type
            if "database" in type_lower or "rds" in type_lower:
                style.update(self.COLOR_MAPPINGS["database"])
            elif "storage" in type_lower or "s3" in type_lower:
                style.update(self.COLOR_MAPPINGS["storage"])
            elif "compute" in type_lower or "ec2" in type_lower or "vm" in type_lower:
                style.update(self.COLOR_MAPPINGS["compute"])
            elif "network" in type_lower or "vpc" in type_lower or "vnet" in type_lower:
                style.update(self.COLOR_MAPPINGS["network"])

        return style

    def _generate_connections(self) -> List[str]:
        """Generate connection statements.

        Returns:
            List of code lines
        """
        lines = []

        for connection in self.diagram_data.connections:
            source_component = self.get_component_by_id(connection.source)
            target_component = self.get_component_by_id(connection.target)

            if not source_component or not target_component:
                continue

            # Build connection path considering clusters
            source_path = self._get_component_path(source_component)
            target_path = self._get_component_path(target_component)

            # Get connection label
            label = connection.properties.get("label", "")

            if label:
                lines.append(f'{source_path} -> {target_path}: "{label}"')
            else:
                lines.append(f'{source_path} -> {target_path}')

        return lines

    def _get_component_path(self, component: Component) -> str:
        """Get the full path to a component (including cluster).

        Args:
            component: Component

        Returns:
            Full path string
        """
        comp_id = self._sanitize_identifier(component.id)
        cluster_name = component.properties.get("cluster", None)

        if cluster_name:
            cluster_id = self._sanitize_identifier(cluster_name)
            return f"{cluster_id}.{comp_id}"
        else:
            return comp_id

    def generate_example(self) -> str:
        """Generate an example 3-tier AWS architecture in D2.

        Returns:
            D2 code string
        """
        return '''title: "3-Tier AWS Architecture" {
  near: top-center
}

VPC: {
  label: "VPC (10.0.0.0/16)"

  PublicSubnet: {
    label: "Public Subnet"

    ALB: "Application Load Balancer" {
      shape: rectangle
      style.fill: "#FF9900"
      style.stroke: "#232F3E"
    }
  }

  AppTier: {
    label: "Private Subnet - App Tier"

    App1: "App Server 1" {
      shape: rectangle
      style.fill: "#FF9900"
    }
    App2: "App Server 2" {
      shape: rectangle
      style.fill: "#FF9900"
    }
    App3: "App Server 3" {
      shape: rectangle
      style.fill: "#FF9900"
    }
  }

  DataTier: {
    label: "Private Subnet - Data Tier"

    PrimaryDB: "Primary RDS" {
      shape: cylinder
      style.fill: "#4CAF50"
      style.stroke: "#2E7D32"
    }
    ReplicaDB: "Read Replica" {
      shape: cylinder
      style.fill: "#4CAF50"
      style.stroke: "#2E7D32"
    }
  }
}

S3: "S3 Bucket - Static Assets" {
  shape: cloud
  style.fill: "#2196F3"
  style.stroke: "#1565C0"
}

# Connections
VPC.PublicSubnet.ALB -> VPC.AppTier.App1: "http"
VPC.PublicSubnet.ALB -> VPC.AppTier.App2: "http"
VPC.PublicSubnet.ALB -> VPC.AppTier.App3: "http"

VPC.AppTier.App1 -> VPC.DataTier.PrimaryDB: "sql"
VPC.AppTier.App2 -> VPC.DataTier.PrimaryDB: "sql"
VPC.AppTier.App3 -> VPC.DataTier.PrimaryDB: "sql"

VPC.DataTier.PrimaryDB -> VPC.DataTier.ReplicaDB: "replication"

VPC.AppTier.App1 -> S3: "s3 api"
VPC.AppTier.App2 -> S3: "s3 api"
VPC.AppTier.App3 -> S3: "s3 api"
'''
