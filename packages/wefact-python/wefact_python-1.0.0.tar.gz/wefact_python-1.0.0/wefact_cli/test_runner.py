"""Test runner for executing endpoint tests"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from wefact import WeFact
from .endpoints.base_tester import BaseEndpointTester, TesterResult
from .endpoints.interactive_tester import InteractiveEndpointTester
from .utils.env_handler import get_all_dummy_ids
from .ui.tables import render_response_data


@dataclass
class EndpointTestReport:
    """Comprehensive test report"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    total_duration: float = 0.0
    results: List[TesterResult] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage"""
        return (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0.0
    
    def add_result(self, result: TesterResult) -> None:
        """Add a test result to the report"""
        self.results.append(result)
        self.total_tests += 1
        if result.success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        self.total_duration += result.duration
    
    def add_results(self, results: List[TesterResult]) -> None:
        """Add multiple test results"""
        for result in results:
            self.add_result(result)


class EndpointTestRunner:
    """Execute tests across WeFact API endpoints"""
    
    def __init__(self, client: WeFact):
        """
        Initialize the test runner
        
        Args:
            client: Authenticated WeFact client instance
        """
        self.client = client
        self.console = Console()
        self.dummy_ids = get_all_dummy_ids()
    
    def _get_tester(self, endpoint_name: str) -> Optional[BaseEndpointTester]:
        """
        Get a tester instance for an endpoint
        
        Args:
            endpoint_name: Name of the endpoint
        
        Returns:
            BaseEndpointTester instance or None
        """
        endpoint_map = {
            'invoices': (self.client.invoices, 'invoice'),
            'debtors': (self.client.debtors, 'debtor'),
            'products': (self.client.products, 'product'),
            'creditors': (self.client.creditors, 'creditor'),
            'groups': (self.client.groups, 'group'),
            'subscriptions': (self.client.subscriptions, 'subscription'),
            'quotes': (self.client.quotes, 'pricequote'),
            'interactions': (self.client.interactions, 'interaction'),
            'tasks': (self.client.tasks, 'task'),
            'transactions': (self.client.transactions, 'transaction'),
            'cost_categories': (self.client.cost_categories, 'cost_category'),
            'settings': (self.client.settings, 'settings'),
        }
        
        if endpoint_name not in endpoint_map:
            return None
        
        resource, resource_name = endpoint_map[endpoint_name]
        ids = self.dummy_ids.get(resource_name, [])
        
        return BaseEndpointTester(resource, resource_name, ids)
    
    def run_all_tests(self) -> EndpointTestReport:
        """
        Run tests for all endpoints
        
        Returns:
            EndpointTestReport object
        """
        report = EndpointTestReport()
        
        endpoints = [
            'invoices', 'debtors', 'products', 'creditors',
            'groups', 'subscriptions', 'quotes', 'interactions',
            'tasks', 'transactions', 'cost_categories', 'settings'
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("[cyan]Running all tests...", total=len(endpoints))
            
            for endpoint in endpoints:
                progress.update(main_task, description=f"[cyan]Testing {endpoint}...")
                
                tester = self._get_tester(endpoint)
                if tester:
                    results = tester.run_all_basic_tests()
                    report.add_results(results)
                
                progress.update(main_task, advance=1)
        
        return report
    
    def run_endpoint_tests(self, endpoint_name: str, method: Optional[str] = None, show_data: bool = True) -> EndpointTestReport:
        """
        Run tests for a specific endpoint
        
        Args:
            endpoint_name: Name of the endpoint to test
            method: Specific method to test, or None for all basic tests
            show_data: Whether to display response data
        
        Returns:
            EndpointTestReport object
        """
        report = EndpointTestReport()
        
        tester = self._get_tester(endpoint_name)
        if not tester:
            self.console.print(f"[red]Unknown endpoint: {endpoint_name}[/red]")
            return report
        
        if method and method != "all":
            # Test specific method
            result = tester.test_method(method)
            report.add_result(result)
            
            # Display response data if successful and show_data is True
            if show_data and result.success and result.response:
                render_response_data(
                    result.response,
                    title=f"{endpoint_name.title()} - {method} Response",
                    max_entries=5,
                    console=self.console
                )
        else:
            # Run all basic tests
            results = tester.run_all_basic_tests()
            report.add_results(results)
            
            # Display data from the first successful test that has response data
            if show_data:
                for result in results:
                    if result.success and result.response:
                        render_response_data(
                            result.response,
                            title=f"{endpoint_name.title()} - {result.method} Response",
                            max_entries=5,
                            console=self.console
                        )
                        break  # Only show first successful response
        
        return report
    
    def run_single_test(
        self,
        endpoint_name: str,
        method: str,
        show_data: bool = True,
        interactive: bool = True,
        **params
    ) -> TesterResult:
        """
        Run a single test with specific parameters
        
        Args:
            endpoint_name: Name of the endpoint
            method: Method to test
            show_data: Whether to display response data
            interactive: Whether to use interactive flow
            **params: Parameters to pass to the method
        
        Returns:
            TesterResult object
        """
        tester = self._get_tester(endpoint_name)
        if not tester:
            return TesterResult(
                endpoint=endpoint_name,
                method=method,
                success=False,
                duration=0.0,
                error=f"Unknown endpoint: {endpoint_name}"
            )
        
        # Use interactive tester if enabled and no params provided
        if interactive and not params:
            endpoint_map = {
                'invoices': (self.client.invoices, 'invoice'),
                'debtors': (self.client.debtors, 'debtor'),
                'products': (self.client.products, 'product'),
                'creditors': (self.client.creditors, 'creditor'),
                'groups': (self.client.groups, 'group'),
                'subscriptions': (self.client.subscriptions, 'subscription'),
                'quotes': (self.client.quotes, 'pricequote'),
                'interactions': (self.client.interactions, 'interaction'),
                'tasks': (self.client.tasks, 'task'),
                'transactions': (self.client.transactions, 'transaction'),
                'cost_categories': (self.client.cost_categories, 'cost_category'),
                'settings': (self.client.settings, 'settings'),
            }
            
            if endpoint_name in endpoint_map:
                resource, resource_name = endpoint_map[endpoint_name]
                ids = self.dummy_ids.get(resource_name, [])
                interactive_tester = InteractiveEndpointTester(
                    resource, resource_name, ids, self.console
                )
                return interactive_tester.test_with_flow(method)
        
        # Fallback to basic test
        result = tester.test_method(method, **params)
        
        # Display response data if successful and show_data is True
        if show_data and result.success and result.response:
            render_response_data(
                result.response,
                title=f"{endpoint_name.title()} - {method} Response",
                max_entries=5,
                console=self.console
            )
        
        return result
    
    def get_endpoint_methods(self, endpoint_name: str) -> List[str]:
        """
        Get available methods for an endpoint
        
        Args:
            endpoint_name: Name of the endpoint
        
        Returns:
            List of method names
        """
        tester = self._get_tester(endpoint_name)
        if not tester:
            return []
        
        return tester.get_available_methods()
