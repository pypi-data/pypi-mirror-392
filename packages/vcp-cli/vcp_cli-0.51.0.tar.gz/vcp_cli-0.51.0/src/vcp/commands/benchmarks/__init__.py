# src/vcp/commands/benchmarks/__init__.py
import click


class LazyGroup(click.Group):
    """A click Group that imports subcommands lazily."""

    def get_command(self, ctx, name):
        """Import and return command only when requested."""
        if name == "list":
            from .list import list_command  # noqa: PLC0415

            return list_command
        elif name == "run":
            from .run import run_command  # noqa: PLC0415

            return run_command
        elif name == "get":
            from .get import get_command  # noqa: PLC0415

            return get_command
        elif name == "system-check":
            from .system_check import system_check_command  # noqa: PLC0415

            return system_check_command

        return None

    def list_commands(self, ctx):
        """List available commands without importing them."""
        return ["list", "run", "get", "system-check"]


@click.group(cls=LazyGroup)
def benchmarks_command():
    """View and run benchmarks available on the Virtual Cells Platform"""
    pass
