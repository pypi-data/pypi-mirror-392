"""Mermaid diagram generator for text-based infrastructure diagrams."""

from typing import Dict, List, Set
from .base import DiagramGenerator
from ..models import DiagramData, Component, Connection


class MermaidGenerator(DiagramGenerator):
    """Generator for Mermaid diagrams (text-based, GitHub-friendly)."""

    # Icon mappings for Mermaid (using Font Awesome icons)
    ICON_MAPPINGS = {
        "aws_vpc": "fa:fa-cloud",
        "aws_ec2": "fa:fa-server",
        "aws_ecs": "fa:fa-docker",
        "aws_lambda": "fa:fa-bolt",
        "aws_rds": "fa:fa-database",
        "aws_s3": "fa:fa-hdd",
        "aws_elb": "fa:fa-balance-scale",
        "aws_alb": "fa:fa-balance-scale",
        "database": "fa:fa-database",
        "storage": "fa:fa-hdd",
        "compute": "fa:fa-server",
        "network": "fa:fa-network-wired",
        "load_balancer": "fa:fa-balance-scale",
    }

    # Style mappings for different component types
    STYLE_MAPPINGS = {
        "aws_vpc": "fill:#e3f2fd,stroke:#1976d2,stroke-width:2px",
        "aws_subnet": "fill:#fff3e0,stroke:#f57c00,stroke-width:2px",
        "aws_ec2": "fill:#fff,stroke:#ff9800,stroke-width:2px",
        "aws_ecs": "fill:#fff,stroke:#2196f3,stroke-width:2px",
        "aws_lambda": "fill:#fff,stroke:#ff9800,stroke-width:2px",
        "aws_rds": "fill:#e8f5e9,stroke:#4caf50,stroke-width:3px",
        "aws_dynamodb": "fill:#e8f5e9,stroke:#4caf50,stroke-width:3px",
        "aws_s3": "fill:#e1f5fe,stroke:#0277bd,stroke-width:2px",
        "aws_elb": "fill:#fff,stroke:#ff9800,stroke-width:2px",
        "aws_alb": "fill:#fff,stroke:#ff9800,stroke-width:2px",
        "database": "fill:#e8f5e9,stroke:#4caf50,stroke-width:3px",
        "storage": "fill:#e1f5fe,stroke:#0277bd,stroke-width:2px",
        "compute": "fill:#fff,stroke:#ff9800,stroke-width:2px",
        "load_balancer": "fill:#fff,stroke:#ff9800,stroke-width:2px",
    }

    def __init__(self, diagram_data: DiagramData = None):
        """Initialize Mermaid generator.

        Args:
            diagram_data: DiagramData model
        """
        super().__init__(diagram_data)
        self.clusters: Dict[str, List[Component]] = {}
        self.used_styles: Set[str] = set()

    def get_format(self) -> str:
        """Return format name."""
        return "mermaid"

    def get_file_extension(self) -> str:
        """Return file extension."""
        return ".mmd"

    def generate(self) -> str:
        """Generate Mermaid diagram syntax.

        Returns:
            Mermaid code string
        """
        # Reset state
        self.clusters = {}
        self.used_styles = set()

        # Organize components into clusters
        self._organize_clusters()

        # Build the Mermaid code
        code_parts = []

        # Determine diagram type (graph or flowchart)
        diagram_type = self.diagram_data.metadata.get("diagram_type", "graph")
        direction = self.diagram_data.metadata.get("direction", "TB")

        code_parts.append(f"{diagram_type} {direction}")

        # Generate subgraphs (clusters)
        if self.clusters:
            code_parts.extend(self._generate_clusters())
        else:
            code_parts.extend(self._generate_components())

        # Generate connections
        code_parts.append("")
        code_parts.extend(self._generate_connections())

        # Generate styles
        code_parts.append("")
        code_parts.extend(self._generate_styles())

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
            node_id = self._sanitize_identifier(component.id)
            label = component.name
            shape = self._get_shape_for_component(component)

            # Track style usage
            if component.type.lower() in self.STYLE_MAPPINGS:
                self.used_styles.add(component.type.lower())

            lines.append(f"    {node_id}{shape}")

        return lines

    def _generate_clusters(self) -> List[str]:
        """Generate clusters (subgraphs) with components.

        Returns:
            List of code lines
        """
        lines = []

        # Generate components not in clusters
        unclustered = [
            c for c in self.diagram_data.components
            if not c.properties.get("cluster")
        ]

        for component in unclustered:
            node_id = self._sanitize_identifier(component.id)
            label = component.name
            shape = self._get_shape_for_component(component)

            # Track style usage
            if component.type.lower() in self.STYLE_MAPPINGS:
                self.used_styles.add(component.type.lower())

            lines.append(f"    {node_id}{shape}")

        # Generate clusters
        for cluster_name, components in self.clusters.items():
            cluster_id = self._sanitize_identifier(cluster_name)

            lines.append(f'    subgraph {cluster_id}["{cluster_name}"]')

            for component in components:
                node_id = self._sanitize_identifier(component.id)
                label = component.name
                shape = self._get_shape_for_component(component)

                # Track style usage
                if component.type.lower() in self.STYLE_MAPPINGS:
                    self.used_styles.add(component.type.lower())

                lines.append(f"        {node_id}{shape}")

            lines.append("    end")
            lines.append("")

        return lines

    def _get_shape_for_component(self, component: Component) -> str:
        """Get the Mermaid shape syntax for a component.

        Args:
            component: Component

        Returns:
            Shape syntax string
        """
        label = component.name
        type_lower = component.type.lower()

        # Database components use cylindrical shape
        if "database" in type_lower or "rds" in type_lower or "dynamodb" in type_lower:
            return f"[('{label}')]"

        # Storage components use asymmetric shape
        if "storage" in type_lower or "s3" in type_lower:
            return f"[/'{label}'/]"

        # Lambda/Functions use stadium shape
        if "lambda" in type_lower or "function" in type_lower:
            return f"(['{label}'])"

        # Load balancers use hexagon
        if "load" in type_lower or "elb" in type_lower or "alb" in type_lower:
            return f"{{{{{label}}}}}"

        # VPC/Network use rounded rectangle
        if "vpc" in type_lower or "vnet" in type_lower:
            return f"['{label}']"

        # Default: rectangle
        return f"['{label}']"

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

            source_id = self._sanitize_identifier(connection.source)
            target_id = self._sanitize_identifier(connection.target)

            # Get connection label
            label = connection.properties.get("label", "")

            # Determine arrow style based on connection type
            arrow = self._get_arrow_style(connection.type)

            if label:
                lines.append(f"    {source_id} {arrow}|{label}| {target_id}")
            else:
                lines.append(f"    {source_id} {arrow} {target_id}")

        return lines

    def _get_arrow_style(self, connection_type: str) -> str:
        """Get arrow style for connection type.

        Args:
            connection_type: Connection type

        Returns:
            Arrow style string
        """
        type_lower = connection_type.lower()

        if "data" in type_lower or "flow" in type_lower:
            return "==>"  # Thick arrow for data flow
        elif "dependency" in type_lower:
            return "-..->"  # Dotted arrow for dependencies
        else:
            return "-->"  # Default arrow

    def _generate_styles(self) -> List[str]:
        """Generate style definitions.

        Returns:
            List of code lines
        """
        lines = []

        # Generate styles for used component types
        for component in self.diagram_data.components:
            type_lower = component.type.lower()

            if type_lower in self.STYLE_MAPPINGS:
                node_id = self._sanitize_identifier(component.id)
                style = self.STYLE_MAPPINGS[type_lower]
                lines.append(f"    style {node_id} {style}")

        return lines

    def generate_example(self) -> str:
        """Generate an example 3-tier AWS architecture in Mermaid.

        Returns:
            Mermaid code string
        """
        return '''graph TB
    subgraph VPC["VPC (10.0.0.0/16)"]
        subgraph PublicSubnet["Public Subnet"]
            ALB{{"Application Load Balancer"}}
        end

        subgraph AppTier["Private Subnet - App Tier"]
            App1["App Server 1"]
            App2["App Server 2"]
            App3["App Server 3"]
        end

        subgraph DataTier["Private Subnet - Data Tier"]
            PrimaryDB[("Primary RDS")]
            ReplicaDB[("Read Replica")]
        end
    end

    S3[/"S3 Bucket - Static Assets"/]

    ALB -->|http| App1
    ALB -->|http| App2
    ALB -->|http| App3

    App1 -->|sql| PrimaryDB
    App2 -->|sql| PrimaryDB
    App3 -->|sql| PrimaryDB

    PrimaryDB ==>|replication| ReplicaDB

    App1 -->|s3 api| S3
    App2 -->|s3 api| S3
    App3 -->|s3 api| S3

    style VPC fill:#e3f2fd
    style PublicSubnet fill:#fff3e0
    style AppTier fill:#f3e5f5
    style DataTier fill:#e8f5e9
    style PrimaryDB fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
    style ReplicaDB fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
    style S3 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
'''
