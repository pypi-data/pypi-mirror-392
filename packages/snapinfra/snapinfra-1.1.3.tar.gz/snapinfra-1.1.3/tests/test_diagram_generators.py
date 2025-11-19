"""Unit tests for diagram generators."""

import pytest
from snapinfra.diagram.generators import (
    MingrammerGenerator,
    MermaidGenerator,
    D2Generator
)
from snapinfra.diagram.models import DiagramData, Component, Connection


@pytest.fixture
def sample_diagram_data():
    """Create sample diagram data for testing."""
    diagram = DiagramData(metadata={"name": "Test Architecture"})

    # Add components
    alb = Component(
        id="alb_1",
        name="Load Balancer",
        type="aws_alb",
        properties={"cluster": "VPC"}
    )

    app = Component(
        id="app_1",
        name="App Server",
        type="aws_ecs",
        properties={"cluster": "App Tier"}
    )

    db = Component(
        id="db_1",
        name="Database",
        type="aws_rds",
        properties={"cluster": "Data Tier"}
    )

    diagram.components = [alb, app, db]

    # Add connections
    diagram.connections = [
        Connection(source="alb_1", target="app_1", properties={"label": "http"}),
        Connection(source="app_1", target="db_1", properties={"label": "sql"})
    ]

    return diagram


class TestMingrammerGenerator:
    """Tests for MingrammerGenerator."""

    def test_initialization(self):
        """Test generator initialization."""
        generator = MingrammerGenerator()
        assert generator is not None
        assert generator.get_format() == "python-diagrams"
        assert generator.get_file_extension() == ".py"

    def test_generate_with_data(self, sample_diagram_data):
        """Test diagram generation with data."""
        generator = MingrammerGenerator(sample_diagram_data)
        code = generator.generate()

        # Check that code was generated
        assert code is not None
        assert len(code) > 0

        # Check for expected imports
        assert "from diagrams import Diagram" in code
        assert "from diagrams.aws" in code

        # Check for components
        assert "Load_Balancer" in code or "Load Balancer" in code
        assert "App_Server" in code or "App Server" in code
        assert "Database" in code

    def test_generate_example(self):
        """Test example diagram generation."""
        generator = MingrammerGenerator()
        code = generator.generate_example()

        assert code is not None
        assert "3-Tier AWS Architecture" in code
        assert "from diagrams import Diagram" in code
        assert "ECS" in code
        assert "RDS" in code

    def test_validation(self, sample_diagram_data):
        """Test diagram validation."""
        generator = MingrammerGenerator(sample_diagram_data)
        errors = generator.validate()

        # Should have no errors for valid diagram
        assert len(errors) == 0

    def test_validation_empty_diagram(self):
        """Test validation with empty diagram."""
        generator = MingrammerGenerator()
        errors = generator.validate()

        # Should have error for empty diagram
        assert len(errors) > 0
        assert "No components" in errors[0]


class TestMermaidGenerator:
    """Tests for MermaidGenerator."""

    def test_initialization(self):
        """Test generator initialization."""
        generator = MermaidGenerator()
        assert generator is not None
        assert generator.get_format() == "mermaid"
        assert generator.get_file_extension() == ".mmd"

    def test_generate_with_data(self, sample_diagram_data):
        """Test diagram generation with data."""
        generator = MermaidGenerator(sample_diagram_data)
        code = generator.generate()

        # Check that code was generated
        assert code is not None
        assert len(code) > 0

        # Check for Mermaid syntax
        assert "graph" in code.lower()

        # Check for components (sanitized identifiers)
        assert "alb_1" in code or "Load Balancer" in code
        assert "app_1" in code or "App Server" in code
        assert "db_1" in code or "Database" in code

        # Check for connections
        assert "-->" in code or "==>" in code

    def test_generate_example(self):
        """Test example diagram generation."""
        generator = MermaidGenerator()
        code = generator.generate_example()

        assert code is not None
        assert "graph TB" in code
        assert "Load Balancer" in code or "ALB" in code
        assert "RDS" in code or "Database" in code

    def test_shapes(self, sample_diagram_data):
        """Test shape generation for different component types."""
        generator = MermaidGenerator(sample_diagram_data)
        code = generator.generate()

        # Database should use cylinder shape [( )]
        # Storage should use asymmetric shape [/ /]
        # Check that different shapes are used
        assert "[" in code  # Some shape syntax


class TestD2Generator:
    """Tests for D2Generator."""

    def test_initialization(self):
        """Test generator initialization."""
        generator = D2Generator()
        assert generator is not None
        assert generator.get_format() == "d2"
        assert generator.get_file_extension() == ".d2"

    def test_generate_with_data(self, sample_diagram_data):
        """Test diagram generation with data."""
        generator = D2Generator(sample_diagram_data)
        code = generator.generate()

        # Check that code was generated
        assert code is not None
        assert len(code) > 0

        # Check for D2 syntax
        assert "{" in code
        assert "}" in code
        assert ":" in code

        # Check for connections
        assert "->" in code

    def test_generate_example(self):
        """Test example diagram generation."""
        generator = D2Generator()
        code = generator.generate_example()

        assert code is not None
        assert "3-Tier AWS Architecture" in code
        assert "shape:" in code
        assert "style." in code

    def test_shape_mappings(self):
        """Test shape mappings for different component types."""
        # Database component
        db_data = DiagramData()
        db_data.components = [
            Component(id="db1", name="Database", type="aws_rds")
        ]

        generator = D2Generator(db_data)
        code = generator.generate()

        # Should have cylinder shape for database
        assert "cylinder" in code

    def test_color_mappings(self):
        """Test color mappings for different providers."""
        aws_data = DiagramData()
        aws_data.components = [
            Component(id="ec2", name="EC2", type="aws_ec2")
        ]

        generator = D2Generator(aws_data)
        code = generator.generate()

        # Should have AWS colors
        assert "style.fill" in code or "fill:" in code


class TestBaseGenerator:
    """Tests for base generator functionality."""

    def test_sanitize_identifier(self, sample_diagram_data):
        """Test identifier sanitization."""
        generator = MingrammerGenerator(sample_diagram_data)

        # Test sanitization
        assert generator._sanitize_identifier("My Component") == "My_Component"
        assert generator._sanitize_identifier("app-server-1") == "app_server_1"
        assert generator._sanitize_identifier("server@123") == "server_123"

    def test_get_cloud_provider(self, sample_diagram_data):
        """Test cloud provider detection."""
        generator = MingrammerGenerator(sample_diagram_data)

        assert generator._get_cloud_provider("aws_ec2") == "aws"
        assert generator._get_cloud_provider("azure_vm") == "azure"
        assert generator._get_cloud_provider("gcp_compute") == "gcp"
        assert generator._get_cloud_provider("k8s_pod") == "k8s"
        assert generator._get_cloud_provider("generic") is None

    def test_component_operations(self, sample_diagram_data):
        """Test component add/get operations."""
        generator = MingrammerGenerator(sample_diagram_data)

        # Get component by ID
        component = generator.get_component_by_id("alb_1")
        assert component is not None
        assert component.name == "Load Balancer"

        # Get components by type
        aws_components = generator.get_components_by_type("aws_ecs")
        assert len(aws_components) == 1
        assert aws_components[0].name == "App Server"

    def test_connection_operations(self, sample_diagram_data):
        """Test connection operations."""
        generator = MingrammerGenerator(sample_diagram_data)

        # Get connections for component
        connections = generator.get_connections_for_component("app_1")
        assert len(connections) == 2  # Connected to ALB and DB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
