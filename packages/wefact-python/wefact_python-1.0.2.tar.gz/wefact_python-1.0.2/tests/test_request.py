"""Tests for request module."""

import pytest
import requests
from unittest.mock import Mock
from wefact.request import flatten_params, RequestMixin
from wefact.exceptions import ClientError, ValidationError, NotFoundError


class TestFlattenParams:
    """Test flatten_params function."""
    
    def test_simple_params(self):
        """Test flattening simple key-value pairs."""
        params = {"key1": "value1", "key2": "value2"}
        result = flatten_params(params)
        assert result == [("key1", "value1"), ("key2", "value2")]
    
    def test_nested_dict(self):
        """Test flattening nested dictionary."""
        params = {"user": {"name": "John", "age": 30}}
        result = flatten_params(params)
        assert set(result) == {("user[name]", "John"), ("user[age]", "30")}
    
    def test_list_of_dicts(self):
        """Test flattening list of dictionaries (like InvoiceLines)."""
        params = {
            "InvoiceLines": [
                {"Number": 1, "ProductCode": "P0001"},
                {"Number": 2, "ProductCode": "P0002"}
            ]
        }
        result = flatten_params(params)
        expected = [
            ("InvoiceLines[0][Number]", "1"),
            ("InvoiceLines[0][ProductCode]", "P0001"),
            ("InvoiceLines[1][Number]", "2"),
            ("InvoiceLines[1][ProductCode]", "P0002")
        ]
        assert result == expected
    
    def test_simple_list(self):
        """Test flattening simple list."""
        params = {"tags": ["tag1", "tag2", "tag3"]}
        result = flatten_params(params)
        expected = [
            ("tags[0]", "tag1"),
            ("tags[1]", "tag2"),
            ("tags[2]", "tag3")
        ]
        assert result == expected
    
    def test_complex_nested_structure(self):
        """Test flattening complex nested structure."""
        params = {
            "Debtor": {
                "CompanyName": "Acme Corp",
                "Address": {"Street": "Main St", "Number": "123"}
            },
            "InvoiceLines": [
                {"Description": "Product A", "PriceExcl": 100.00}
            ]
        }
        result = flatten_params(params)
        assert ("Debtor[CompanyName]", "Acme Corp") in result
        assert ("Debtor[Address][Street]", "Main St") in result
        assert ("Debtor[Address][Number]", "123") in result
        assert ("InvoiceLines[0][Description]", "Product A") in result
        assert ("InvoiceLines[0][PriceExcl]", "100.0") in result
    
    def test_empty_dict(self):
        """Test flattening empty dictionary."""
        params = {}
        result = flatten_params(params)
        assert result == []


class TestRequestMixin:
    """Test RequestMixin class."""
    
    def test_send_request_success(self, mocker):
        """Test successful API request."""
        mixin = RequestMixin()
        mixin.api_key = "test_key"
        mixin.api_url = "https://api.test.com/"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "controller": "invoice",
            "action": "list",
            "status": "success",
            "invoices": []
        }
        
        mock_post = mocker.patch('requests.post', return_value=mock_response)
        
        result = mixin._send_request("invoice", "list", {"limit": 10})
        
        assert result["status"] == "success"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "api_key=test_key" in call_args.kwargs["data"]
        assert "controller=invoice" in call_args.kwargs["data"]
        assert "action=list" in call_args.kwargs["data"]
    
    def test_send_request_network_error(self, mocker):
        """Test handling of network errors."""
        mixin = RequestMixin()
        mixin.api_key = "test_key"
        mixin.api_url = "https://api.test.com/"
        
        mocker.patch('requests.post', side_effect=requests.RequestException("Network error"))
        
        with pytest.raises(ClientError, match="Network error"):
            mixin._send_request("invoice", "list", {})
    
    def test_send_request_invalid_json(self, mocker):
        """Test handling of invalid JSON response."""
        mixin = RequestMixin()
        mixin.api_key = "test_key"
        mixin.api_url = "https://api.test.com/"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mocker.patch('requests.post', return_value=mock_response)
        
        with pytest.raises(ValidationError, match="Invalid JSON response"):
            mixin._send_request("invoice", "list", {})
    
    def test_send_request_with_nested_params(self, mocker):
        """Test request with nested parameters."""
        mixin = RequestMixin()
        mixin.api_key = "test_key"
        mixin.api_url = "https://api.test.com/"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "controller": "invoice",
            "action": "add",
            "status": "success"
        }
        
        mock_post = mocker.patch('requests.post', return_value=mock_response)
        
        params = {
            "DebtorCode": "DB001",
            "InvoiceLines": [
                {"Number": 1, "ProductCode": "P001"},
                {"Number": 2, "ProductCode": "P002"}
            ]
        }
        
        result = mixin._send_request("invoice", "add", params)
        
        assert result["status"] == "success"
        call_data = mock_post.call_args.kwargs["data"]
        # URL encoded brackets: [ = %5B, ] = %5D
        assert "InvoiceLines%5B0%5D%5BNumber%5D=1" in call_data
        assert "InvoiceLines%5B0%5D%5BProductCode%5D=P001" in call_data
        assert "InvoiceLines%5B1%5D%5BNumber%5D=2" in call_data
        assert "InvoiceLines%5B1%5D%5BProductCode%5D=P002" in call_data
    
    def test_send_request_http_error(self, mocker):
        """Test handling of HTTP error responses."""
        mixin = RequestMixin()
        mixin.api_key = "test_key"
        mixin.api_url = "https://api.test.com/"
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errors": ["Not found"]}
        mock_response.headers = {}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        with pytest.raises(NotFoundError, match="404"):
            mixin._send_request("invoice", "list", {})
    
    def test_send_request_wefact_error(self, mocker):
        """Test handling of WeFact API error response."""
        mixin = RequestMixin()
        mixin.api_key = "test_key"
        mixin.api_url = "https://api.test.com/"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "controller": "invoice",
            "action": "show",
            "status": "error",
            "errors": ["Invoice not found"]
        }
        mock_response.headers = {}
        
        mocker.patch('requests.post', return_value=mock_response)
        
        with pytest.raises(ValidationError, match="Invoice not found"):
            mixin._send_request("invoice", "show", {"Identifier": "999"})
