"""Main CLI application"""

import sys
from pathlib import Path
from typing import Optional

# Fix for running as script directly
if __name__ == '__main__' and __package__ is None:
    # Add parent directory to path so imports work
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    __package__ = 'wefact_cli'

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from wefact import WeFact
from .config import config
from .utils import ensure_api_key, ensure_test_email, get_all_dummy_ids, clear_dummy_data_flags
from .dummy_data import DummyDataGenerator
from .test_runner import EndpointTestRunner
from .ui import (
    prompt_initialize_dummy_data,
    prompt_select_endpoint,
    prompt_select_action,
    confirm_action,
    render_test_results,
    render_main_menu,
    render_dummy_data_summary,
    render_test_summary,
    render_settings,
    create_header,
    create_welcome_panel,
    create_success_panel,
    create_error_panel,
)


def show_welcome_banner(console: Console):
    """Display welcome banner."""
    console.clear()
    banner = """            
    ░        ░░        ░░        ░░   ░░░  ░░   ░░░  ░░░      ░░░  ░░░░  ░░░      ░░░        ░░        ░
    ▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒    ▒▒  ▒▒    ▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒
    ▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓  ▓  ▓  ▓▓  ▓  ▓  ▓▓  ▓▓▓▓  ▓▓▓  ▓▓  ▓▓▓  ▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓      ▓▓▓
    ██  ████████  ██████████  █████  ██    ██  ██    ██  ████  ████    ████        █████  █████  ███████
    █        ██        ██        ██  ███   ██  ███   ███      ██████  █████  ████  █████  █████        █
    """
    console.print(banner, style="bold cyan")
    console.print(Panel.fit(
        "[bold cyan]WeFact API Testing Tool[/bold cyan]\n"
        "[dim]Interactive endpoint testing and dummy data management[/dim]",
        border_style="cyan"
    ))


class WefactTestCLI:
    """Interactive CLI for testing WeFact API endpoints"""
    
    def __init__(self):
        """Initialize the CLI application"""
        self.console = Console()
        self.client: Optional[WeFact] = None
        self.test_runner: Optional[EndpointTestRunner] = None
        self.running = True
    
    def run(self) -> None:
        """Main application loop"""
        try:
            self._initialize()
            
            while self.running:
                self._show_main_menu()
        
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Fatal error: {e}[/red]")
            raise
        finally:
            self._cleanup()
    
    def _initialize(self) -> None:
        """Initialize the application"""
        show_welcome_banner(self.console)
        
        # Ensure API key exists
        api_key = ensure_api_key()
        if not api_key:
            self.console.print(create_error_panel("API key is required to continue"))
            sys.exit(1)
        
        # Initialize WeFact client
        self.client = WeFact(api_key=api_key)
        self.test_runner = EndpointTestRunner(self.client)
        
        self.console.print("\n[green]✓ Connected to WeFact API[/green]\n")
        
        # Ensure test email is configured
        test_email = ensure_test_email()
        if test_email:
            # Create/update test debtor
            generator = DummyDataGenerator(self.client)
            generator.ensure_test_debtor(test_email)
        
        # Check if dummy data needs to be initialized
        if not config.is_dummy_data_initialized():
            if prompt_initialize_dummy_data():
                self._initialize_dummy_data()
    
    def _show_main_menu(self) -> None:
        """Display and handle main menu"""
        self.console.clear()
        self.console.print(create_header())
        self.console.print(render_main_menu())
        
        choice = Prompt.ask(
            "\nSelect option",
            choices=["1", "2", "3", "4", "5", "6", "7"],
            default="7"
        )
        
        if choice == "1":
            self._test_all_endpoints()
        elif choice == "2":
            self._test_specific_endpoint()
        elif choice == "3":
            self._initialize_dummy_data()
        elif choice == "4":
            self._view_dummy_data()
        elif choice == "5":
            self._clear_dummy_data()
        elif choice == "6":
            self._show_settings()
        elif choice == "7":
            self._exit()
    
    def _test_all_endpoints(self) -> None:
        """Test all endpoints"""
        self.console.clear()
        self.console.print(create_header("Testing All Endpoints"))
        
        if not confirm_action("This will test all endpoints. Continue?", default=True):
            return
        
        self.console.print()
        report = self.test_runner.run_all_tests()
        
        # Display results
        self.console.print("\n")
        self.console.print(render_test_summary(report.results))
        self.console.print()
        self.console.print(render_test_results(report.results, title="Detailed Results"))
        
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _test_specific_endpoint(self) -> None:
        """Test a specific endpoint"""
        self.console.clear()
        self.console.print(create_header("Test Specific Endpoint"))
        
        endpoint = prompt_select_endpoint()
        if not endpoint:
            return
        
        # Get available methods
        methods = self.test_runner.get_endpoint_methods(endpoint)
        if not methods:
            self.console.print(create_error_panel(f"No methods available for {endpoint}"))
            self.console.input("\n[dim]Press Enter to continue...[/dim]")
            return
        
        action = prompt_select_action(endpoint, methods)
        if not action:
            return
        
        self.console.print(f"\n[cyan]Testing {endpoint} - {action}...[/cyan]\n")
        
        # Run tests
        if action == "all":
            report = self.test_runner.run_endpoint_tests(endpoint)
            self.console.print(render_test_summary(report.results))
            self.console.print()
            self.console.print(render_test_results(report.results))
        else:
            result = self.test_runner.run_single_test(endpoint, action)
            self.console.print(render_test_results([result]))
        
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _initialize_dummy_data(self) -> None:
        """Initialize dummy data"""
        self.console.clear()
        self.console.print(create_header("Initialize Dummy Data"))
        
        if config.is_dummy_data_initialized():
            self.console.print("[yellow]⚠ Dummy data already initialized[/yellow]")
            if not confirm_action("Reinitialize? This will create new test data.", default=False):
                return
        
        self.console.print()
        generator = DummyDataGenerator(self.client)
        
        try:
            created_ids = generator.generate_all(count=5)
            
            self.console.print()
            self.console.print(create_success_panel(
                f"Successfully created dummy data!\n"
                f"Total items created: {sum(len(ids) for ids in created_ids.values())}"
            ))
            
            self.console.print()
            self.console.print(render_dummy_data_summary(created_ids))
        
        except Exception as e:
            self.console.print()
            self.console.print(create_error_panel(f"Failed to create dummy data: {e}"))
        
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _view_dummy_data(self) -> None:
        """View dummy data summary"""
        self.console.clear()
        self.console.print(create_header("Dummy Data Summary"))
        
        dummy_data = get_all_dummy_ids()
        
        if not dummy_data:
            self.console.print(create_error_panel("No dummy data found. Initialize dummy data first."))
        else:
            total_items = sum(len(ids) for ids in dummy_data.values())
            self.console.print(f"\n[cyan]Total dummy items: {total_items}[/cyan]\n")
            self.console.print(render_dummy_data_summary(dummy_data))
        
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _clear_dummy_data(self) -> None:
        """Clear all dummy data"""
        self.console.clear()
        self.console.print(create_header("Clear Dummy Data"))
        
        if not config.is_dummy_data_initialized():
            self.console.print(create_error_panel("No dummy data to clear"))
            self.console.input("\n[dim]Press Enter to continue...[/dim]")
            return
        
        dummy_data = get_all_dummy_ids()
        total_items = sum(len(ids) for ids in dummy_data.values())
        
        self.console.print(f"\n[yellow]This will delete {total_items} test items from your WeFact account.[/yellow]")
        self.console.print(render_dummy_data_summary(dummy_data))
        
        if not confirm_action("\nAre you sure you want to delete all dummy data?", default=False):
            return
        
        self.console.print()
        generator = DummyDataGenerator(self.client)
        generator.created_ids = dummy_data
        
        try:
            generator.clear_all()
            clear_dummy_data_flags()
            
            self.console.print()
            self.console.print(create_success_panel("Dummy data cleared successfully"))
        
        except Exception as e:
            self.console.print()
            self.console.print(create_error_panel(f"Failed to clear dummy data: {e}"))
        
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _show_settings(self) -> None:
        """Show current settings"""
        self.console.clear()
        self.console.print(create_header("Settings"))
        
        api_key = config.get_api_key() or ""
        api_url = config.get_api_url()
        dummy_initialized = config.is_dummy_data_initialized()
        
        self.console.print()
        self.console.print(render_settings(api_key, api_url, dummy_initialized))
        
        self.console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _exit(self) -> None:
        """Exit the application"""
        self.running = False
        self.console.print("\n[cyan]Thanks for using WeFact API Testing Tool![/cyan]\n")
    
    def _cleanup(self) -> None:
        """Cleanup before exit"""
        pass


def main():
    """Main entry point"""
    app = WefactTestCLI()
    app.run()


if __name__ == "__main__":
    main()
