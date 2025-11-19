import sys


class PrintCommandMixin:
    """Provides the print facility."""

    def print(self, style: str, msg: str, exit_code: int = None) -> str:
        """Print a message using a management command style."""
        self.stdout.write(getattr(self.style, style)(msg))
        if exit_code is not None:
            sys.exit(exit_code)
