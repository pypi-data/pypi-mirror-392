"""
WeFact API Resources

Each resource module provides a class that handles API operations for a specific
WeFact entity (invoices, debtors, products, etc.).

All resources use the controller/action API pattern via RequestMixin.
"""

from .base import BaseResource
from .invoice import InvoiceResource
from .credit_invoice import CreditInvoiceResource
from .debtor import DebtorResource
from .product import ProductResource
from .creditor import CreditorResource
from .group import GroupResource
from .subscription import SubscriptionResource
from .interaction import InteractionResource
from .quote import QuoteResource
from .task import TaskResource
from .transaction import TransactionResource
from .settings import SettingsResource
from .cost_category import CostCategoryResource

__all__ = [
    "BaseResource",
    "InvoiceResource",
    "CreditInvoiceResource",
    "DebtorResource",
    "ProductResource",
    "CreditorResource",
    "GroupResource",
    "SubscriptionResource",
    "InteractionResource",
    "QuoteResource",
    "TaskResource",
    "TransactionResource",
    "SettingsResource",
    "CostCategoryResource",
]
