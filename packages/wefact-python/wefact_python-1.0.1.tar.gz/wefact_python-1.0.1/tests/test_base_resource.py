"""Tests for BaseResource class."""

import pytest
from wefact.resources.base import BaseResource


class TestBaseResource:
    """Test BaseResource functionality."""
    
    def test_get_plural_resource_name(self):
        """Test get_plural_resource_name method."""
        resource = BaseResource("test_key")
        resource.controller_name = "invoice"
        assert resource.get_plural_resource_name() == "invoices"
    
    def test_list_all_single_page(self, mocker):
        """Test list_all with single page of results."""
        resource = BaseResource("test_key")
        resource.controller_name = "product"
        
        # Mock single page response
        mock_response = {
            "products": [
                {"Identifier": 1, "ProductCode": "P001"},
                {"Identifier": 2, "ProductCode": "P002"},
            ],
            "currentresults": 2
        }
        
        mocker.patch.object(resource, 'list', return_value=mock_response)
        mocker.patch.object(resource, 'show', side_effect=lambda **kwargs: {
            "product": {"Identifier": kwargs["Identifier"], "ProductCode": f"P00{kwargs['Identifier']}"}
        })
        
        results = resource.list_all()
        
        assert len(results) == 2
        assert results[0]["Identifier"] == 1
        assert results[1]["Identifier"] == 2
    
    def test_list_all_multiple_pages(self, mocker):
        """Test list_all with pagination."""
        resource = BaseResource("test_key")
        resource.controller_name = "product"
        
        # First page - full (reduced from 1000 to 10 for speed)
        first_page = {
            "products": [{"Identifier": i} for i in range(1, 11)],
            "currentresults": 10
        }
        
        # Second page - partial
        second_page = {
            "products": [{"Identifier": i} for i in range(11, 16)],
            "currentresults": 5
        }
        
        mocker.patch.object(resource, 'list', side_effect=[first_page, second_page])
        mocker.patch.object(resource, 'show', side_effect=lambda **kwargs: {
            "product": {"Identifier": kwargs["Identifier"]}
        })
        
        # Use smaller per_page to trigger pagination
        results = resource.list_all(per_page=10)
        
        assert len(results) == 15
        assert results[0]["Identifier"] == 1
        assert results[-1]["Identifier"] == 15
    
    def test_list_all_rate_limiting(self, mocker):
        """Test list_all respects rate limiting."""
        resource = BaseResource("test_key")
        resource.controller_name = "product"
        
        # Create a response with just enough items to trigger rate limiting check
        # Reduced from 300 to 10 for speed
        mock_response = {
            "products": [{"Identifier": i} for i in range(1, 11)],
            "currentresults": 10
        }
        
        mocker.patch.object(resource, 'list', return_value=mock_response)
        
        # Mock show to track calls
        show_calls = []
        def mock_show(**kwargs):
            show_calls.append(kwargs["Identifier"])
            return {"product": {"Identifier": kwargs["Identifier"]}}
        
        mocker.patch.object(resource, 'show', side_effect=mock_show)
        
        # Mock time.sleep to track if it's called
        mock_sleep = mocker.patch('time.sleep')
        
        results = resource.list_all()
        
        assert len(results) == 10
        # Verify show was called for each item
        assert len(show_calls) == 10
