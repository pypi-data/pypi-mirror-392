"""Panel and layout components using Rich"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from typing import Optional


def create_header(subtitle: Optional[str] = None) -> Panel:
    """
    Create the application header
    
    Args:
        subtitle: Optional subtitle text
    
    Returns:
        Rich Panel object
    """
    title_text = Text()
    title_text.append("WeFact API Testing Tool", style="bold cyan")
    
    if subtitle:
        title_text.append("\n")
        title_text.append(subtitle, style="dim")
    
    return Panel(
        Align.center(title_text),
        border_style="cyan",
        padding=(1, 2)
    )


def create_status_panel(
    api_connected: bool,
    dummy_data_initialized: bool,
    total_tests: int = 0
) -> Panel:
    """
    Create a status panel showing current state
    
    Args:
        api_connected: Whether API is connected
        dummy_data_initialized: Whether dummy data exists
        total_tests: Number of tests run
    
    Returns:
        Rich Panel object
    """
    status_text = Text()
    
    # API Status
    if api_connected:
        status_text.append("✓ ", style="green")
        status_text.append("API Connected\n")
    else:
        status_text.append("✗ ", style="red")
        status_text.append("API Not Connected\n", style="red")
    
    # Dummy Data Status
    if dummy_data_initialized:
        status_text.append("✓ ", style="green")
        status_text.append("Dummy Data Available\n")
    else:
        status_text.append("⚠ ", style="yellow")
        status_text.append("No Dummy Data\n", style="yellow")
    
    # Tests Run
    if total_tests > 0:
        status_text.append("ℹ ", style="blue")
        status_text.append(f"{total_tests} tests run")
    
    return Panel(
        status_text,
        title="[bold]Status[/bold]",
        border_style="blue",
        padding=(0, 1)
    )


def create_help_panel() -> Panel:
    """
    Create a help panel with keyboard shortcuts
    
    Returns:
        Rich Panel object
    """
    help_text = Text()
    help_text.append("Navigation:\n", style="bold")
    help_text.append("  b - Go back\n", style="dim")
    help_text.append("  q - Quit\n", style="dim")
    help_text.append("  h - Show help\n", style="dim")
    help_text.append("\nCommands:\n", style="bold")
    help_text.append("  1-9 - Select menu option\n", style="dim")
    help_text.append("  Enter - Confirm selection\n", style="dim")
    
    return Panel(
        help_text,
        title="[bold]Help[/bold]",
        border_style="yellow",
        padding=(0, 1)
    )


def create_welcome_panel() -> Panel:
    """
    Create a welcome message panel
    
    Returns:
        Rich Panel object
    """
    welcome_text = Text()
    welcome_text.append("Welcome to the WeFact API Testing Tool!\n\n", style="bold cyan")
    welcome_text.append("This interactive CLI helps you:\n")
    welcome_text.append("  • Test all WeFact API endpoints\n", style="dim")
    welcome_text.append("  • Generate dummy test data\n", style="dim")
    welcome_text.append("  • Validate API responses\n", style="dim")
    welcome_text.append("  • Monitor endpoint performance\n", style="dim")
    welcome_text.append("\nPress 'h' for help at any time.", style="italic dim")
    
    return Panel(
        Align.center(welcome_text),
        border_style="cyan",
        padding=(1, 2)
    )


def create_error_panel(error_message: str, title: str = "Error") -> Panel:
    """
    Create an error message panel
    
    Args:
        error_message: Error message to display
        title: Panel title
    
    Returns:
        Rich Panel object
    """
    error_text = Text(error_message, style="bold red")
    
    return Panel(
        error_text,
        title=f"[bold red]{title}[/bold red]",
        border_style="red",
        padding=(1, 2)
    )


def create_success_panel(message: str, title: str = "Success") -> Panel:
    """
    Create a success message panel
    
    Args:
        message: Success message to display
        title: Panel title
    
    Returns:
        Rich Panel object
    """
    success_text = Text(message, style="bold green")
    
    return Panel(
        success_text,
        title=f"[bold green]{title}[/bold green]",
        border_style="green",
        padding=(1, 2)
    )


def create_info_panel(message: str, title: str = "Info") -> Panel:
    """
    Create an info message panel
    
    Args:
        message: Info message to display
        title: Panel title
    
    Returns:
        Rich Panel object
    """
    info_text = Text(message, style="cyan")
    
    return Panel(
        info_text,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )


def create_layout(header: bool = True, footer: bool = True) -> Layout:
    """
    Create a basic layout structure
    
    Args:
        header: Whether to include header
        footer: Whether to include footer
    
    Returns:
        Rich Layout object
    """
    layout = Layout()
    
    if header and footer:
        layout.split(
            Layout(name="header", size=5),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
    elif header:
        layout.split(
            Layout(name="header", size=5),
            Layout(name="main")
        )
    elif footer:
        layout.split(
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
    else:
        layout.split(Layout(name="main"))
    
    return layout
