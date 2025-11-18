"""Python skill implementation for agno runtime."""
from agno.tools.python import PythonTools as AgnoPythonTools


class PythonTools(AgnoPythonTools):
    """
    Python code execution using agno PythonTools.

    Wraps agno's PythonTools to provide Python execution.
    """

    def __init__(self, **kwargs):
        """
        Initialize Python tools.

        Args:
            **kwargs: Configuration (enable_code_execution, blocked_imports, etc.)
        """
        super().__init__()
        self.config = kwargs
