"""Tests for WeFact main class."""

import pytest
from wefact import WeFact


class TestWeFact:
    """Test WeFact main class."""
    
    def test_initialization(self):
        """Test WeFact initialization."""
        client = WeFact(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.api_url == "https://api.mijnwefact.nl/v2/"
    
    def test_custom_api_url(self):
        """Test WeFact with custom API URL."""
        client = WeFact(api_key="test_key", api_url="https://custom.api.url/")
        assert client.api_url == "https://custom.api.url/"
    
    def test_invoices_property(self):
        """Test invoices resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.invoices, 'list')
        assert hasattr(client.invoices, 'create')
    
    def test_credit_invoices_property(self):
        """Test credit_invoices resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.credit_invoices, 'list')
        assert hasattr(client.credit_invoices, 'create')
    
    def test_debtors_property(self):
        """Test debtors resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.debtors, 'list')
        assert hasattr(client.debtors, 'create')
    
    def test_products_property(self):
        """Test products resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.products, 'list')
        assert hasattr(client.products, 'create')
    
    def test_creditors_property(self):
        """Test creditors resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.creditors, 'list')
        assert hasattr(client.creditors, 'create')
    
    def test_groups_property(self):
        """Test groups resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.groups, 'list')
        assert hasattr(client.groups, 'create')
    
    def test_subscriptions_property(self):
        """Test subscriptions resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.subscriptions, 'list')
        assert hasattr(client.subscriptions, 'create')
    
    def test_settings_property(self):
        """Test settings resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.settings, 'list')
    
    def test_cost_categories_property(self):
        """Test cost_categories resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.cost_categories, 'list')
        assert hasattr(client.cost_categories, 'create')
    
    def test_interactions_property(self):
        """Test interactions resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.interactions, 'list')
        assert hasattr(client.interactions, 'create')
    
    def test_quotes_property(self):
        """Test quotes resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.quotes, 'list')
        assert hasattr(client.quotes, 'create')
    
    def test_tasks_property(self):
        """Test tasks resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.tasks, 'list')
        assert hasattr(client.tasks, 'create')
    
    def test_transactions_property(self):
        """Test transactions resource property."""
        client = WeFact(api_key="test_key")
        assert hasattr(client.transactions, 'list')
        assert hasattr(client.transactions, 'create')
