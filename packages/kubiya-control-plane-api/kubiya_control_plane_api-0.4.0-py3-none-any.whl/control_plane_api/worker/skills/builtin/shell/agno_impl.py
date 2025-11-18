"""Shell skill implementation for agno runtime."""
from agno.tools.shell import ShellTools as AgnoShellTools


class ShellTools(AgnoShellTools):
    """
    Shell command execution using agno ShellTools.

    Wraps agno's ShellTools to provide shell access.
    """

    def __init__(self, **kwargs):
        """
        Initialize shell tools.

        Args:
            **kwargs: Configuration (allowed_commands, blocked_commands, timeout, etc.)
        """
        super().__init__()
        self.config = kwargs
