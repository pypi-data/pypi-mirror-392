"""Data Visualization skill implementation for agno runtime."""
from agno.tools import Toolkit


class DataVisualizationTools(Toolkit):
    """
    Data visualization and diagramming tools.

    Provides Mermaid diagram generation capabilities.
    """

    def __init__(
        self,
        enable_flowchart: bool = True,
        enable_sequence: bool = True,
        enable_class_diagram: bool = True,
        enable_er_diagram: bool = True,
        enable_gantt: bool = True,
        enable_pie_chart: bool = True,
        enable_state_diagram: bool = True,
        enable_git_graph: bool = True,
        enable_user_journey: bool = True,
        enable_quadrant_chart: bool = True,
        max_diagram_size: int = 50000,
        theme: str = "default",
        **kwargs
    ):
        """
        Initialize data visualization tools.

        Args:
            enable_*: Enable various diagram types
            max_diagram_size: Maximum diagram size in characters
            theme: Mermaid theme
            **kwargs: Additional configuration
        """
        super().__init__(name="data-visualization")
        self.config = {
            "flowchart": enable_flowchart,
            "sequence": enable_sequence,
            "class": enable_class_diagram,
            "er": enable_er_diagram,
            "gantt": enable_gantt,
            "pie": enable_pie_chart,
            "state": enable_state_diagram,
            "git": enable_git_graph,
            "journey": enable_user_journey,
            "quadrant": enable_quadrant_chart,
            "max_size": max_diagram_size,
            "theme": theme,
        }

        # Register diagram generation function
        self.register(self.create_diagram)

    def create_diagram(self, diagram_type: str, diagram_code: str) -> str:
        """
        Create a Mermaid diagram.

        Args:
            diagram_type: Type of diagram (flowchart, sequence, etc.)
            diagram_code: Mermaid diagram code

        Returns:
            Formatted Mermaid diagram
        """
        if len(diagram_code) > self.config["max_size"]:
            return f"Error: Diagram exceeds maximum size of {self.config['max_size']} characters"

        if diagram_type not in self.config or not self.config[diagram_type]:
            return f"Error: Diagram type '{diagram_type}' is not enabled"

        # Return Mermaid-formatted diagram
        return f"```mermaid\\n{diagram_code}\\n```"
