"""Custom Click extensions for VCP CLI.

This module provides custom Click components for improved command discoverability
and user experience, particularly for handling optional dependencies.
"""

import io
import sys
from typing import Any, Callable

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from .dependencies import get_extra_requirements, get_install_command

# Width for Rich panels to prevent wrapping on standard terminals
PANEL_WIDTH = 85


class VCPCommandGroup(click.Group):
    """Custom Click Group that displays commands in sections based on availability.

    This group separates available commands from unavailable (stub) commands,
    displaying them in distinct sections in the help output. This improves
    discoverability by showing users all possible commands, even those that
    require additional installation.
    """

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Format commands into 'Uninstalled Commands' and 'Commands' sections.

        Args:
            ctx: Click context
            formatter: Help formatter instance
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue

            # Get help text
            help_text = cmd.get_short_help_str(limit=60)

            # Categorize as available or stub
            is_stub = is_stub_command(cmd)
            commands.append((subcommand, cmd, help_text, is_stub))

        if not commands:
            return

        # Separate into available and unavailable
        available = [
            (name, help_text) for name, _, help_text, stub in commands if not stub
        ]
        unavailable = [
            (name, help_text, getattr(cmd, "__extra_name__", name))
            for name, cmd, help_text, stub in commands
            if stub
        ]

        # Format available commands section FIRST
        if available:
            with formatter.section("Commands"):
                self.format_commands_list(formatter, available)

        # Format unavailable commands section AFTER regular commands
        if unavailable:
            self.format_uninstalled_commands_panel(formatter, unavailable)

    def format_commands_list(
        self, formatter: click.HelpFormatter, commands: list[tuple[str, str]]
    ) -> None:
        """Format a list of commands as rows.

        Args:
            formatter: Help formatter instance
            commands: List of (name, help_text) tuples
        """
        rows = []
        for name, help_text in commands:
            rows.append((name, help_text))

        if rows:
            formatter.write_dl(rows)

    def format_uninstalled_commands_panel(
        self, formatter: click.HelpFormatter, commands: list[tuple[str, str, str]]
    ) -> None:
        """Format uninstalled commands in a Rich Panel for high visibility.

        Args:
            formatter: Help formatter instance
            commands: List of (name, help_text, extra_name) tuples
        """
        # Build the panel content
        lines = []
        for name, help_text, extra_name in commands:
            install_cmd = escape(
                get_install_command(extra_name)
            )  # Escape square brackets

            # Format with command name, description, and install instruction
            lines.append(f"[cyan]{name:12}[/cyan] {help_text}")
            lines.append(f"{'':12} [dim]→ {install_cmd}[/dim]")
            lines.append("")  # Blank line between commands

        # Add tip for installing all features
        all_install_cmd = escape(get_install_command("all"))
        lines.append(f"[dim]Install all features: [bold]{all_install_cmd}[/bold][/dim]")

        panel_content = "\n".join(lines)

        # Create Rich panel
        panel = Panel(
            panel_content,
            title="[yellow]Additional Commands (require installation)[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

        # Capture panel output using a string buffer with wider width to prevent wrapping
        string_buffer = io.StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=PANEL_WIDTH)
        console.print(panel)
        panel_output = string_buffer.getvalue()

        # Write the panel to the formatter
        formatter.write("\n")
        formatter.write(panel_output)
        formatter.write("\n")


class StubGroup(click.Group):
    """A Click Group that shows installation instructions instead of executing subcommands.

    This group acts as a placeholder for command groups that require optional dependencies.
    It accepts any subcommand name but always shows installation instructions instead of
    executing the subcommand.

    Attributes:
        command_name: Name of the command (e.g., "model")
        extra_name: Name of the pip extra (e.g., "model")
        _show_installation_panel: Callback function to display the installation panel
    """

    def __init__(
        self,
        command_name: str,
        extra_name: str,
        show_installation_panel: Callable[[click.Context], None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the StubGroup.

        Args:
            command_name: Name of the command
            extra_name: Name of the pip extra
            show_installation_panel: Callback to show installation instructions
            *args: Additional positional arguments for click.Group
            **kwargs: Additional keyword arguments for click.Group
        """
        super().__init__(*args, **kwargs)
        self.command_name = command_name
        self.extra_name = extra_name
        self._show_installation_panel = show_installation_panel

    def get_command(self, _ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Return a dummy command for any subcommand name.

        This allows the group to accept any subcommand without raising
        "No such command" errors. The actual invocation is handled in
        the invoke method.

        Args:
            _ctx: Click context (unused)
            cmd_name: Name of the subcommand being requested

        Returns:
            A dummy command that does nothing (invoke handles the actual behavior)
        """

        # Return a dummy command - the actual behavior is in invoke()
        @click.command(name=cmd_name)
        def dummy() -> None:
            pass

        return dummy

    def invoke(self, ctx: click.Context) -> None:
        """Intercept invocation and show installation panel.

        This method is called when the group is invoked, whether with or without
        a subcommand. It shows the installation panel and exits, preventing any
        subcommand from executing.

        Args:
            ctx: Click context
        """
        # If --help was requested, let Click handle it normally
        # Check sys.argv for --help flag or if Click is in resilient parsing mode
        if "--help" in sys.argv or "-h" in sys.argv or ctx.resilient_parsing:
            super().invoke(ctx)
            return

        # Show installation panel instead of executing any subcommand
        self._show_installation_panel(ctx)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Format help text with a Rich Panel showing installation instructions.

        Args:
            ctx: Click context
            formatter: Help formatter instance
        """
        # Build and show Rich Panel with installation instructions FIRST
        requirements = get_extra_requirements(self.extra_name)
        install_cmd = escape(
            get_install_command(self.extra_name)
        )  # Escape square brackets
        all_install_cmd = escape(get_install_command("all"))  # Escape square brackets

        # Build panel content
        lines = []
        lines.append(
            f"The '[cyan]{self.command_name}[/cyan]' command requires additional packages."
        )
        lines.append("")
        lines.append("[bold]Install with:[/bold]")
        lines.append(f"  {install_cmd}")
        lines.append("")

        if requirements:
            lines.append("[bold]This will install:[/bold]")
            for req in requirements:
                lines.append(f"  • {req.name} {req.specifier}")
            lines.append("")

        lines.append("[bold]Or install all features:[/bold]")
        lines.append(f"  {all_install_cmd}")

        panel_content = "\n".join(lines)

        # Create Rich panel
        panel = Panel(
            panel_content,
            title="[yellow]Additional Package Required[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

        # Capture panel output with wider width to prevent wrapping
        string_buffer = io.StringIO()
        console = Console(file=string_buffer, force_terminal=True, width=PANEL_WIDTH)
        console.print(panel)
        panel_output = string_buffer.getvalue()

        # Write the panel to the formatter BEFORE standard help
        formatter.write(panel_output)
        formatter.write("\n")

        # Then let parent class format the standard help (Usage, Options, etc.)
        super().format_help(ctx, formatter)


def create_stub_command(
    command_name: str, extra_name: str, description: str
) -> click.Group:
    """Create a stub command group that shows installation instructions.

    Stub commands are placeholders for command groups that require optional dependencies.
    When invoked (with or without subcommands), they display a helpful message with
    installation instructions instead of failing with an import error.

    Args:
        command_name: Name of the command (e.g., "model")
        extra_name: Name of the pip extra (e.g., "model")
        description: Short description of the command

    Returns:
        A Click group that shows installation instructions
    """

    def show_installation_panel(ctx: click.Context) -> None:
        """Display installation instructions for this feature."""
        console = Console()

        # Get requirements dynamically from package metadata
        requirements = get_extra_requirements(extra_name)
        install_cmd = get_install_command(extra_name)
        all_install_cmd = get_install_command("all")

        # Escape square brackets for Rich markup (Rich uses [] for styling)
        install_cmd_escaped = escape(install_cmd)
        all_install_cmd_escaped = escape(all_install_cmd)

        # Format requirements list
        if requirements:
            req_list = "\n".join(
                f"  • {req.name} {req.specifier}" for req in requirements
            )
        else:
            req_list = "  (requirements list unavailable)"

        # Create rich formatted panel
        message = (
            f"[yellow]The '{command_name}' command requires additional packages.[/yellow]\n\n"
            f"[bold]Install with:[/bold]\n"
            f"  $ {install_cmd_escaped}\n\n"
            f"[bold]This will install:[/bold]\n"
            f"{req_list}\n\n"
            f"[bold]Or install all features:[/bold]\n"
            f"  $ {all_install_cmd_escaped}"
        )

        console.print(
            Panel.fit(
                message,
                title="Feature Not Installed",
                border_style="yellow",
            )
        )

        ctx.exit(1)

    # Create the stub group
    # invoke_without_command=True ensures our invoke() is called even without subcommand
    stub_group = StubGroup(
        command_name=command_name,
        extra_name=extra_name,
        show_installation_panel=show_installation_panel,
        name=command_name,
        help=f"{description}\n\nThis command requires additional packages to be installed.",
        short_help=description,
        invoke_without_command=True,
    )

    # Mark as stub command for identification and store extra name
    stub_group.__stub_command__ = True  # type: ignore[attr-defined]
    stub_group.__extra_name__ = extra_name  # type: ignore[attr-defined]

    return stub_group


def is_stub_command(cmd: click.Command) -> bool:
    """Check if a command is a stub command.

    Args:
        cmd: Click command to check

    Returns:
        True if the command is a stub, False otherwise
    """
    return getattr(cmd, "__stub_command__", False)
