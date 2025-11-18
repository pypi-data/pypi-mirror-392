"""Base endpoint tester with generic testing methods"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime


@dataclass
class TesterResult:
    """Result of a single test operation"""
    endpoint: str
    method: str
    success: bool
    duration: float
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        status = "✓ PASS" if self.success else "✗ FAIL"
        return f"{self.method:20} {status:10} {self.duration:.2f}s"


class BaseEndpointTester:
    """Generic endpoint tester with common test methods"""
    
    def __init__(self, resource: Any, resource_name: str, dummy_ids: List[str]):
        """
        Initialize the endpoint tester
        
        Args:
            resource: WeFact resource instance (e.g., client.invoices)
            resource_name: Name of the resource (e.g., 'invoice')
            dummy_ids: List of dummy data IDs for this endpoint
        """
        self.resource = resource
        self.resource_name = resource_name
        self.dummy_ids = dummy_ids
    
    def _execute_test(
        self,
        method_name: str,
        test_func: Callable,
        *args,
        **kwargs
    ) -> TesterResult:
        """
        Execute a test function and capture results
        
        Args:
            method_name: Name of the method being tested
            test_func: Function to execute
            *args, **kwargs: Arguments to pass to test function
        
        Returns:
            TesterResult object
        """
        start_time = time.time()
        
        try:
            response = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Check if response indicates success
            is_success = self._is_success_response(response)
            
            return TesterResult(
                endpoint=self.resource_name,
                method=method_name,
                success=is_success,
                duration=duration,
                response=response,
                error=None if is_success else self._extract_error(response)
            )
        
        except Exception as e:
            duration = time.time() - start_time
            return TesterResult(
                endpoint=self.resource_name,
                method=method_name,
                success=False,
                duration=duration,
                response=None,
                error=str(e)
            )
    
    def _is_success_response(self, response: Any) -> bool:
        """Check if response indicates success"""
        # list_all returns a list directly, not a dict
        if isinstance(response, list):
            return True
        
        if not isinstance(response, dict):
            return False
        
        # Check for explicit error
        if response.get("status") == "error":
            return False
        
        if "error" in response and response["error"]:
            return False
        
        if "errors" in response and response["errors"]:
            return False
        
        # If response has data, consider it successful
        return True
    
    def _extract_error(self, response: Any) -> str:
        """Extract error message from response"""
        if not isinstance(response, dict):
            return "Invalid response format"
        
        if "error" in response:
            return str(response["error"])
        
        if "errors" in response:
            errors = response["errors"]
            if isinstance(errors, list) and errors:
                return str(errors[0])
            return str(errors)
        
        return "Unknown error"
    
    def test_list(self, **params) -> TesterResult:
        """Test the list operation"""
        default_params = {'limit': 10, 'offset': 0}
        
        # Some resources require additional parameters for list
        if self.resource_name == 'group':
            # Groups require a type parameter (debtor or product) - lowercase 'type'
            if 'type' not in params and 'Type' not in params:
                default_params['type'] = 'debtor'
        
        elif self.resource_name == 'interaction':
            # Interactions require referenceId and referenceType
            if 'referenceId' not in params:
                default_params['referenceId'] = 1  # Use debtor #1
            if 'referenceType' not in params:
                default_params['referenceType'] = 'debtor'
        
        default_params.update(params)
        
        return self._execute_test(
            "list",
            self.resource.list,
            **default_params
        )
    
    def test_show(self, identifier: Optional[str] = None) -> TesterResult:
        """Test the show operation"""
        if not identifier and self.dummy_ids:
            identifier = self.dummy_ids[0]
        
        if not identifier:
            return TesterResult(
                endpoint=self.resource_name,
                method="show",
                success=False,
                duration=0.0,
                error="No identifier provided and no dummy data available"
            )
        
        # Determine the correct parameter name based on resource type
        # Some resources use Code fields, others use Identifier
        param_name = self._get_identifier_param_name()
        
        return self._execute_test(
            "show",
            self.resource.show,
            **{param_name: identifier}
        )
    
    def _get_identifier_param_name(self) -> str:
        """Get the appropriate identifier parameter name for this resource"""
        # Map resource names to their identifier parameter names
        code_based_resources = {
            'debtor': 'DebtorCode',
            'product': 'ProductCode',
            'creditor': 'CreditorCode',
            'invoice': 'InvoiceCode',
            'quote': 'PriceQuoteCode',
        }
        
        return code_based_resources.get(self.resource_name, 'Identifier')
    
    def test_create(self, data: Dict[str, Any]) -> TesterResult:
        """Test the create operation"""
        return self._execute_test(
            "create",
            self.resource.create,
            **data
        )
    
    def test_edit(self, identifier: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> TesterResult:
        """Test the edit operation"""
        if not identifier and self.dummy_ids:
            identifier = self.dummy_ids[0]
        
        if not identifier:
            return TesterResult(
                endpoint=self.resource_name,
                method="edit",
                success=False,
                duration=0.0,
                error="No identifier provided and no dummy data available"
            )
        
        if not data:
            data = {}
        
        data['Identifier'] = identifier
        
        return self._execute_test(
            "edit",
            self.resource.edit,
            **data
        )
    
    def test_delete(self, identifier: Optional[str] = None) -> TesterResult:
        """Test the delete operation"""
        if not identifier and self.dummy_ids:
            # Use the last dummy ID for delete tests
            identifier = self.dummy_ids[-1] if len(self.dummy_ids) > 1 else None
        
        if not identifier:
            return TesterResult(
                endpoint=self.resource_name,
                method="delete",
                success=False,
                duration=0.0,
                error="No identifier provided and no dummy data available"
            )
        
        return self._execute_test(
            "delete",
            self.resource.delete,
            Identifier=identifier
        )
    
    def test_method(self, method_name: str, **params) -> TesterResult:
        """
        Test a custom method on the resource
        
        Args:
            method_name: Name of the method to test
            **params: Parameters to pass to the method
        
        Returns:
            TesterResult object
        """
        if not hasattr(self.resource, method_name):
            return TesterResult(
                endpoint=self.resource_name,
                method=method_name,
                success=False,
                duration=0.0,
                error=f"Method '{method_name}' not found on resource"
            )
        
        method = getattr(self.resource, method_name)
        
        return self._execute_test(
            method_name,
            method,
            **params
        )
    
    def run_all_basic_tests(self) -> List[TesterResult]:
        """
        Run all basic CRUD tests
        
        Returns:
            List of TesterResult objects
        """
        results = []
        
        # Test list
        results.append(self.test_list())
        
        # Test show (if we have dummy data)
        if self.dummy_ids:
            results.append(self.test_show())
        
        # Note: We don't test create/edit/delete in basic tests
        # as they modify data. Those should be tested explicitly.
        
        return results
    
    def get_available_methods(self) -> List[str]:
        """
        Get list of available methods on the resource
        
        Returns:
            List of method names
        """
        methods = []
        for attr in dir(self.resource):
            if not attr.startswith('_') and callable(getattr(self.resource, attr)):
                methods.append(attr)
        return methods
