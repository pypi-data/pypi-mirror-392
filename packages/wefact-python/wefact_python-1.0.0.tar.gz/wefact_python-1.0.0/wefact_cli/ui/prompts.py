"""Interactive prompts using Rich"""

from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table


console = Console()


def prompt_api_key() -> Optional[str]:
    """
    Prompt user for API key
    
    Returns:
        API key string or None if cancelled
    """
    console.print("\n[yellow]⚠ WeFact API key not found in .env file[/yellow]")
    console.print("You can find your API key in your WeFact account settings.")
    console.print()
    
    api_key = Prompt.ask("Please enter your WeFact API key", password=True)
    
    if not api_key or api_key.strip() == "":
        console.print("[red]No API key provided[/red]")
        return None
    
    return api_key.strip()


def prompt_initialize_dummy_data() -> bool:
    """
    Ask user if they want to initialize dummy data
    
    Returns:
        True if user wants to initialize, False otherwise
    """
    console.print("\n[cyan]Dummy data not found in your environment.[/cyan]")
    console.print("Dummy data consists of 5 test items per endpoint (debtors, products, etc.)")
    console.print("This data will be created in your WeFact account for testing purposes.")
    console.print()
    
    return Confirm.ask("Would you like to create dummy test data?", default=True)


def prompt_select_endpoint(endpoints: Optional[List[str]] = None) -> Optional[str]:
    """
    Prompt user to select an endpoint
    
    Args:
        endpoints: List of endpoint names. If None, uses default list.
    
    Returns:
        Selected endpoint name or None
    """
    if endpoints is None:
        endpoints = [
            "invoices",
            "debtors",
            "products",
            "creditors",
            "groups",
            "subscriptions",
            "quotes",
            "interactions",
            "tasks",
            "transactions",
            "cost_categories",
            "settings",
        ]
    
    console.print("\n[bold cyan]Available Endpoints:[/bold cyan]")
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    for i, endpoint in enumerate(endpoints, 1):
        table.add_row(f"[cyan]{i}.[/cyan]", endpoint)
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask(
        "Select endpoint",
        choices=[str(i) for i in range(1, len(endpoints) + 1)] + ["0"],
        default="0"
    )
    
    if choice == "0":
        return None
    
    return endpoints[int(choice) - 1]


def prompt_select_action(endpoint: str, actions: List[str]) -> Optional[str]:
    """
    Prompt user to select an action for an endpoint
    
    Args:
        endpoint: Endpoint name
        actions: List of available actions
    
    Returns:
        Selected action name or None
    """
    console.print(f"\n[bold cyan]Available Actions for {endpoint}:[/bold cyan]")
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    # Add "Test All" option
    table.add_row("[cyan]0.[/cyan]", "[bold]Test All[/bold]")
    
    for i, action in enumerate(actions, 1):
        table.add_row(f"[cyan]{i}.[/cyan]", action)
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask(
        "Select action",
        choices=[str(i) for i in range(len(actions) + 1)] + ["b"],
        default="b"
    )
    
    if choice == "b":
        return None
    
    if choice == "0":
        return "all"
    
    return actions[int(choice) - 1]


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user to confirm an action
    
    Args:
        message: Confirmation message
        default: Default choice
    
    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(f"\n{message}", default=default)


def prompt_menu_choice(title: str, options: List[tuple[str, str]], allow_back: bool = True) -> Optional[str]:
    """
    Display a menu and prompt for selection
    
    Args:
        title: Menu title
        options: List of (key, description) tuples
        allow_back: Whether to allow going back
    
    Returns:
        Selected option key or None for back
    """
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    for key, description in options:
        table.add_row(f"[cyan]{key}.[/cyan]", description)
    
    if allow_back:
        table.add_row("[dim]b.[/dim]", "[dim]Back[/dim]")
    
    console.print(table)
    console.print()
    
    valid_choices = [key for key, _ in options]
    if allow_back:
        valid_choices.append("b")
    
    choice = Prompt.ask("Select option", choices=valid_choices)
    
    if choice == "b":
        return None
    
    return choice


def prompt_for_input(field_name: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    """
    Prompt for a single input field
    
    Args:
        field_name: Name of the field
        required: Whether the field is required
        default: Default value
    
    Returns:
        User input or None
    """
    prompt_text = f"Enter {field_name}"
    
    if not required:
        prompt_text += " (optional)"
    
    value = Prompt.ask(prompt_text, default=default or "")
    
    if required and not value:
        console.print("[red]This field is required[/red]")
        return prompt_for_input(field_name, required, default)
    
    return value if value else None
