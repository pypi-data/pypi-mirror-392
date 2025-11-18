"""Formatting utilities for output display"""

import json
from typing import Any, Dict, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text


def format_json(data: Dict[str, Any], theme: str = "monokai") -> Syntax:
    """
    Format JSON data with syntax highlighting
    
    Args:
        data: Data to format
        theme: Pygments theme to use
    
    Returns:
        Rich Syntax object
    """
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    return Syntax(json_str, "json", theme=theme, line_numbers=False)


def format_error(error: str, title: str = "Error") -> Panel:
    """
    Format error message as a Rich panel
    
    Args:
        error: Error message
        title: Panel title
    
    Returns:
        Rich Panel object
    """
    error_text = Text(error, style="bold red")
    return Panel(
        error_text,
        title=f"[bold red]{title}[/bold red]",
        border_style="red",
        expand=False
    )


def format_success(message: str, title: str = "Success") -> Panel:
    """
    Format success message as a Rich panel
    
    Args:
        message: Success message
        title: Panel title
    
    Returns:
        Rich Panel object
    """
    success_text = Text(message, style="bold green")
    return Panel(
        success_text,
        title=f"[bold green]{title}[/bold green]",
        border_style="green",
        expand=False
    )


def format_warning(message: str, title: str = "Warning") -> Panel:
    """
    Format warning message as a Rich panel
    
    Args:
        message: Warning message
        title: Panel title
    
    Returns:
        Rich Panel object
    """
    warning_text = Text(message, style="bold yellow")
    return Panel(
        warning_text,
        title=f"[bold yellow]{title}[/bold yellow]",
        border_style="yellow",
        expand=False
    )


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string (e.g., "1.23s", "123ms")
    """
    if seconds < 1:
        milliseconds = seconds * 1000
        return f"{milliseconds:.0f}ms"
    else:
        return f"{seconds:.2f}s"


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count to human-readable string
    
    Args:
        bytes_count: Number of bytes
    
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_status(success: bool) -> str:
    """
    Format status as colored emoji
    
    Args:
        success: Whether operation was successful
    
    Returns:
        Formatted status string
    """
    return "[green]✓ PASS[/green]" if success else "[red]✗ FAIL[/red]"


def format_identifier_list(identifiers: list[str], max_display: int = 5) -> str:
    """
    Format list of identifiers for display
    
    Args:
        identifiers: List of identifier strings
        max_display: Maximum number to display before truncating
    
    Returns:
        Formatted string
    """
    if not identifiers:
        return "[dim]None[/dim]"
    
    if len(identifiers) <= max_display:
        return ", ".join(identifiers)
    
    displayed = identifiers[:max_display]
    remaining = len(identifiers) - max_display
    return f"{', '.join(displayed)} [dim](+{remaining} more)[/dim]"
