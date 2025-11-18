"""Credit Invoice (Purchase Invoice) resource for WeFact API."""

from .base import BaseResource
from ..enums import Action
from ..enums.credit_invoice_actions import CreditInvoiceAction


class CreditInvoiceResource(BaseResource):
    """
    Credit Invoice resource for managing purchase/supplier invoices.
    
    Credit invoices (Inkoopfacturen) are invoices you receive from suppliers,
    as opposed to regular invoices which you send to customers.
    
    Supports CRUD operations, payment management, line management, and attachments.
    """
    
    controller_name = "creditinvoice"

    # Payment operations
    
    def part_payment(self, **params):
        """
        Process a partial payment for a credit invoice.
        
        Args:
            Identifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            AmountPaid: Required (float)
            PayDate: Optional (date)
            PaymentMethod: Optional (see variables list)
            
        Returns:
            Updated credit invoice with payment applied
        """
        return self._send_request(
            self.controller_name, CreditInvoiceAction.PART_PAYMENT, params
        )

    def mark_as_paid(self, **params):
        """
        Mark a credit invoice as fully paid.
        
        Args:
            Identifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            PayDate: Optional (defaults to today)
            PaymentMethod: Optional (defaults to wire transfer)
            
        Returns:
            Credit invoice with status changed to Paid
        """
        return self._send_request(
            self.controller_name, CreditInvoiceAction.MARK_AS_PAID, params
        )

    # Line management
    
    def credit_invoice_line_add(self, **params):
        """
        Add one or more lines to a credit invoice.
        
        Args:
            Identifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            CreditInvoiceLines: Required (array of line objects)
            
        Returns:
            Credit invoice with new lines added
        """
        return self._send_request(
            self.controller_name, CreditInvoiceAction.CREDIT_INVOICE_LINE_ADD, params
        )

    def credit_invoice_line_delete(self, **params):
        """
        Delete one or more lines from a credit invoice.
        
        Args:
            Identifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            CreditInvoiceLines: Required (array of {Identifier: line_id})
            
        Returns:
            Credit invoice with lines removed
        """
        return self._send_request(
            self.controller_name, CreditInvoiceAction.CREDIT_INVOICE_LINE_DELETE, params
        )

    # Attachments
    
    def attachment_add(self, **params):
        """
        Add an attachment to a credit invoice.
        
        Args:
            ReferenceIdentifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            Filename: Attachment filename
            Base64: Base64 encoded file content
            
        Returns:
            Success confirmation
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_ADD, params
        )

    def attachment_delete(self, **params):
        """
        Delete an attachment from a credit invoice.
        
        Args:
            ReferenceIdentifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            Identifier: Attachment ID
            Filename: Or use filename
            
        Returns:
            Success confirmation
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DELETE, params
        )

    def attachment_download(self, **params):
        """
        Download a credit invoice attachment.
        
        Args:
            ReferenceIdentifier: Credit invoice ID (numeric string)
            CreditInvoiceCode: Or use credit invoice code
            Filename: Attachment filename
            
        Returns:
            Response with Base64 encoded file content
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DOWNLOAD, params
        )
