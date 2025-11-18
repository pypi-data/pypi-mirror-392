"""Transaction resource for WeFact API."""

from .base import BaseResource
from ..enums.transaction_actions import TransactionAction


class TransactionResource(BaseResource):
    """
    Transaction resource for managing bank transactions.
    
    Supports CRUD operations, matching to invoices, and ignoring transactions.
    """
    
    controller_name = "transaction"

    def match(self, **params):
        """
        Match a transaction to one or more invoices.
        
        Args:
            Identifier: Transaction ID (numeric string)
            InvoiceIdentifiers: Array of invoice IDs
            
        Returns:
            Matched transaction details
        """
        return self._send_request(
            self.controller_name, TransactionAction.MATCH, params
        )

    def ignore(self, **params):
        """
        Mark a transaction as ignored.
        
        Args:
            Identifier: Transaction ID (numeric string)
            
        Returns:
            Ignored transaction details
        """
        return self._send_request(
            self.controller_name, TransactionAction.IGNORE, params
        )
