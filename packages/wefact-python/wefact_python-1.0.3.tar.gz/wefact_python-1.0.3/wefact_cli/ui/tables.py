"""Table rendering utilities using Rich"""

from typing import List, Dict, Any, Optional
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
import json

from ..endpoints.base_tester import TesterResult
from ..utils.formatters import format_duration, format_status, format_identifier_list


def render_test_results(results: List[TesterResult], title: str = "Test Results") -> Table:
    """
    Render test results as a Rich table
    
    Args:
        results: List of TesterResult objects
        title: Table title
    
    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Duration", justify="right")
    table.add_column("Error", style="red dim", overflow="fold")
    
    for result in results:
        status = format_status(result.success)
        duration = format_duration(result.duration)
        error = result.error[:50] + "..." if result.error and len(result.error) > 50 else (result.error or "")
        
        table.add_row(
            result.method,
            status,
            duration,
            error if not result.success else ""
        )
    
    return table


def render_endpoint_menu() -> Table:
    """
    Render the main endpoint selection menu
    
    Returns:
        Rich Table object
    """
    table = Table(title="WeFact API Endpoints", show_header=False, box=None, padding=(0, 2))
    
    endpoints = [
        ("1", "Invoices", "Create, list, and manage invoices"),
        ("2", "Debtors", "Manage customer/client records"),
        ("3", "Products", "Product and service catalog"),
        ("4", "Creditors", "Vendor/supplier management"),
        ("5", "Groups", "Customer and product groups"),
        ("6", "Subscriptions", "Recurring billing subscriptions"),
        ("7", "Quotes", "Price quotes and proposals"),
        ("8", "Interactions", "Customer interaction tracking"),
        ("9", "Tasks", "Task management"),
        ("10", "Transactions", "Financial transactions"),
        ("11", "Cost Categories", "Expense categorization"),
        ("12", "Settings", "Account settings"),
    ]
    
    table.add_column("", style="cyan", no_wrap=True)
    table.add_column("Endpoint", style="bold white", no_wrap=True)
    table.add_column("Description", style="dim")
    
    for num, name, desc in endpoints:
        table.add_row(num, name, desc)
    
    return table


def render_main_menu() -> Table:
    """
    Render the main application menu
    
    Returns:
        Rich Table object
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    options = [
        ("1", "Test All Endpoints", "Run comprehensive test suite"),
        ("2", "Test Specific Endpoint", "Select and test individual endpoint"),
        ("3", "Initialize Dummy Data", "Create test data for all endpoints"),
        ("4", "View Dummy Data", "Display created test data IDs"),
        ("5", "Clear Dummy Data", "Remove all test data from API"),
        ("6", "Settings", "View and update configuration"),
        ("7", "Exit", "Exit the application"),
    ]
    
    table.add_column("", style="cyan", no_wrap=True)
    table.add_column("Option", style="bold white", no_wrap=True)
    table.add_column("Description", style="dim")
    
    for num, name, desc in options:
        table.add_row(num, name, desc)
    
    return table


def render_dummy_data_summary(dummy_data: Dict[str, List[str]]) -> Table:
    """
    Render summary of dummy data
    
    Args:
        dummy_data: Dictionary mapping endpoint names to ID lists
    
    Returns:
        Rich Table object
    """
    table = Table(title="Dummy Data Summary", show_header=True, header_style="bold cyan")
    
    table.add_column("Endpoint", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("IDs", style="dim")
    
    if not dummy_data:
        table.add_row("[dim]No dummy data found[/dim]", "", "")
        return table
    
    for endpoint, ids in sorted(dummy_data.items()):
        if ids:
            table.add_row(
                endpoint.replace("_", " ").title(),
                str(len(ids)),
                format_identifier_list(ids, max_display=3)
            )
    
    return table


def render_test_summary(results: List[TesterResult]) -> Table:
    """
    Render summary statistics for test results
    
    Args:
        results: List of TesterResult objects
    
    Returns:
        Rich Table object
    """
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed
    total_duration = sum(r.duration for r in results)
    avg_duration = total_duration / total if total > 0 else 0
    
    table = Table(title="Test Summary", show_header=True, header_style="bold cyan", box=None)
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Total Tests", str(total))
    table.add_row("Passed", f"[green]{passed}[/green]")
    table.add_row("Failed", f"[red]{failed}[/red]")
    table.add_row("Pass Rate", f"{(passed/total*100):.1f}%" if total > 0 else "0%")
    table.add_row("Total Duration", format_duration(total_duration))
    table.add_row("Average Duration", format_duration(avg_duration))
    
    return table


def render_settings(api_key: str, api_url: str, dummy_initialized: bool) -> Table:
    """
    Render current settings
    
    Args:
        api_key: API key (will be masked)
        api_url: API URL
        dummy_initialized: Whether dummy data is initialized
    
    Returns:
        Rich Table object
    """
    table = Table(title="Current Settings", show_header=True, header_style="bold cyan")
    
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    # Mask API key for security
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    
    table.add_row("API Key", masked_key)
    table.add_row("API URL", api_url)
    table.add_row("Dummy Data Initialized", "[green]Yes[/green]" if dummy_initialized else "[red]No[/red]")
    
    return table


def render_response_data(
    response: Any,
    title: str = "API Response",
    max_entries: int = 5,
    console: Optional[Console] = None
) -> None:
    """
    Display the first few entries from an API response
    
    Args:
        response: API response (dict or list)
        title: Title for the display
        max_entries: Maximum number of entries to show
        console: Rich console instance (creates new if None)
    """
    if console is None:
        console = Console()
    
    # Handle list responses (from list_all)
    if isinstance(response, list):
        total_count = len(response)
        entries_to_show = response[:max_entries]
        
        console.print(f"\n[bold cyan]{title}[/bold cyan]")
        console.print(f"[dim]Showing {len(entries_to_show)} of {total_count} entries[/dim]\n")
        
        for i, entry in enumerate(entries_to_show, 1):
            # Create a table for each entry
            table = Table(
                title=f"Entry {i}",
                show_header=True,
                header_style="bold yellow",
                border_style="dim"
            )
            table.add_column("Field", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            # Add key-value pairs
            for key, value in entry.items():
                # Format value based on type
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, indent=2)
                elif value is None:
                    value_str = "[dim]null[/dim]"
                else:
                    value_str = str(value)
                
                # Truncate very long values
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                
                table.add_row(key, value_str)
            
            console.print(table)
            console.print()
        
        return
    
    # Handle dict responses (from list, show, create, etc.)
    if isinstance(response, dict):
        console.print(f"\n[bold cyan]{title}[/bold cyan]\n")
        
        # Check if response contains a list of items
        list_keys = [k for k in response.keys() if isinstance(response.get(k), list) and k != 'errors']
        
        if list_keys:
            # Display the first list found
            list_key = list_keys[0]
            items = response[list_key]
            total_count = len(items)
            entries_to_show = items[:max_entries]
            
            console.print(f"[dim]Found {total_count} {list_key}, showing {len(entries_to_show)}[/dim]\n")
            
            for i, entry in enumerate(entries_to_show, 1):
                # Handle different entry types
                if isinstance(entry, dict):
                    # Dictionary entry - show as table
                    table = Table(
                        title=f"{list_key.capitalize()[:-1]} {i}",
                        show_header=True,
                        header_style="bold yellow",
                        border_style="dim"
                    )
                    table.add_column("Field", style="cyan", no_wrap=True)
                    table.add_column("Value", style="white")
                    
                    for key, value in entry.items():
                        if isinstance(value, (dict, list)):
                            value_str = json.dumps(value, indent=2)
                        elif value is None:
                            value_str = "[dim]null[/dim]"
                        else:
                            value_str = str(value)
                        
                        if len(value_str) > 100:
                            value_str = value_str[:97] + "..."
                        
                        table.add_row(key, value_str)
                    
                    console.print(table)
                    console.print()
                elif isinstance(entry, (str, int, float, bool)):
                    # Simple value - just print it
                    console.print(f"  {i}. {entry}")
                else:
                    # Other types (list, etc.) - print as JSON
                    console.print(f"  {i}. {json.dumps(entry, indent=2)}")
        else:
            # Single item response (like show)
            table = Table(
                title=title,
                show_header=True,
                header_style="bold yellow",
                border_style="dim"
            )
            table.add_column("Field", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            for key, value in response.items():
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, indent=2)
                elif value is None:
                    value_str = "[dim]null[/dim]"
                else:
                    value_str = str(value)
                
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                
                table.add_row(key, value_str)
            
            console.print(table)
            console.print()
        
        return
    
    # Fallback for other types
    console.print(Panel(str(response), title=title, border_style="cyan"))
