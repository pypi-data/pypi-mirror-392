"""Invoice resource for WeFact API."""

from .base import BaseResource
from ..enums import InvoiceAction, Action


class InvoiceResource(BaseResource):
    """
    Invoice resource with complete lifecycle management.
    
    Supports all 25 invoice operations including:
    - CRUD operations (list, show, create, edit, delete)
    - Email operations (send, reminder, summation)
    - Payment management (part payment, mark paid/unpaid)
    - State management (block, unblock, schedule)
    - Line management (add, delete, sort)
    - Attachments (add, delete, download)
    - Credit invoice creation
    """
    
    controller_name = "invoice"

    # Invoice-specific actions
    
    def credit(self, **params):
        """
        Create a credit invoice for an existing invoice.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Response with the new credit invoice details
        """
        return self._send_request(
            self.controller_name, InvoiceAction.CREDIT, params
        )

    def part_payment(self, **params):
        """
        Process a partial payment for an invoice.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            AmountPaid: Required (float)
            PayDate: Optional (date)
            PaymentMethod: Optional (see variables list)
            
        Returns:
            Updated invoice with payment applied
        """
        return self._send_request(
            self.controller_name, InvoiceAction.PART_PAYMENT, params
        )

    def mark_as_paid(self, **params):
        """
        Mark an invoice as fully paid.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            PayDate: Optional (defaults to today)
            PaymentMethod: Optional (defaults to wire transfer)
            
        Returns:
            Invoice with status changed to Paid (4)
        """
        return self._send_request(
            self.controller_name, InvoiceAction.MARK_AS_PAID, params
        )

    def mark_as_unpaid(self, **params):
        """
        Reverse a payment, changing invoice from Paid back to Sent.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Invoice with status changed back to Sent (2)
        """
        return self._send_request(
            self.controller_name, InvoiceAction.MARK_AS_UNPAID, params
        )

    # Email operations
    
    def send_by_email(self, **params):
        """
        Send invoice by email (or Peppol if applicable).
        Changes status from Draft (0) to Sent (2).
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Sent invoice details
        """
        return self._send_request(
            self.controller_name, InvoiceAction.SEND_BY_EMAIL, params
        )

    def send_reminder_by_email(self, **params):
        """
        Send a payment reminder email.
        Only works for sent invoices (status >= 2).
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Success confirmation
        """
        return self._send_request(
            self.controller_name, InvoiceAction.SEND_REMINDER_BY_EMAIL, params
        )

    def send_summation_by_email(self, **params):
        """
        Send a payment summation (collection notice) email.
        Only works for sent invoices (status >= 2).
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Success confirmation
        """
        return self._send_request(
            self.controller_name, InvoiceAction.SEND_SUMMATION_BY_EMAIL, params
        )

    # Document operations
    
    def download(self, **params):
        """
        Download invoice PDF.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Response with Base64 encoded PDF in invoice.Base64
        """
        return self._send_request(
            self.controller_name, InvoiceAction.DOWNLOAD, params
        )

    # State management
    
    def block(self, **params):
        """
        Block a draft invoice.
        Prevents subscriptions from being added and sending the invoice.
        Only works on draft invoices (status = 0).
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Invoice with SubStatus = 'BLOCKED'
        """
        return self._send_request(
            self.controller_name, InvoiceAction.BLOCK, params
        )

    def unblock(self, **params):
        """
        Remove block from a draft invoice.
        Only works on blocked draft invoices.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Invoice with SubStatus cleared
        """
        return self._send_request(
            self.controller_name, InvoiceAction.UNBLOCK, params
        )

    def schedule(self, **params):
        """
        Schedule a draft invoice to be sent automatically.
        Only works on draft invoices (status = 0).
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            ScheduledAt: Required (datetime string: "2024-12-31 20:00:00")
            
        Returns:
            Invoice with ScheduledAt set
        """
        return self._send_request(
            self.controller_name, InvoiceAction.SCHEDULE, params
        )

    def cancel_schedule(self, **params):
        """
        Cancel a scheduled invoice send.
        Only works on scheduled draft invoices.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Invoice with ScheduledAt cleared
        """
        return self._send_request(
            self.controller_name, InvoiceAction.CANCEL_SCHEDULE, params
        )

    # Payment process management
    
    def payment_process_pause(self, **params):
        """
        Pause the payment collection process.
        Only works on Sent (2) or Partially Paid (3) invoices.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            PaymentPausedEndDate: Optional (date)
            PaymentPausedReason: Optional (string)
            DisableOnlinePayment: Optional ('yes' or 'no', default 'no')
            
        Returns:
            Invoice with SubStatus = 'PAUSED'
        """
        return self._send_request(
            self.controller_name, InvoiceAction.PAYMENT_PROCESS_PAUSE, params
        )

    def payment_process_reactivate(self, **params):
        """
        Reactivate a paused payment process.
        Only works on paused invoices.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            
        Returns:
            Invoice with SubStatus cleared
        """
        return self._send_request(
            self.controller_name, InvoiceAction.PAYMENT_PROCESS_REACTIVATE, params
        )

    # Line management
    
    def sort_lines(self, **params):
        """
        Reorder invoice lines.
        Works on invoices in any status.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            InvoiceLines: Required (array of {Identifier: line_id})
            
        Returns:
            Invoice with lines in new order
        """
        return self._send_request(
            self.controller_name, InvoiceAction.SORT_LINES, params
        )

    def invoice_line_add(self, **params):
        """
        Add one or more lines to an invoice.
        Works on invoices in any status.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            InvoiceLines: Required (array of line objects)
            
        Returns:
            Invoice with new lines added
        """
        return self._send_request(
            self.controller_name, InvoiceAction.INVOICE_LINE_ADD, params
        )

    def invoice_line_delete(self, **params):
        """
        Delete one or more lines from an invoice.
        Works on invoices in any status.
        
        Args:
            Identifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            InvoiceLines: Required (array of {Identifier: line_id})
            
        Returns:
            Invoice with lines removed
        """
        return self._send_request(
            self.controller_name, InvoiceAction.INVOICE_LINE_DELETE, params
        )

    # Attachments
    
    def attachment_add(self, **params):
        """Add an attachment to an invoice.
        
        Works on invoices in any status.
        
        Args:
            ReferenceIdentifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
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
        Delete an attachment from an invoice.
        
        Args:
            ReferenceIdentifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
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
        Download an invoice attachment.
        
        Args:
            ReferenceIdentifier: Invoice ID (numeric string)
            InvoiceCode: Or use invoice code (e.g., "INV10000")
            Filename: Attachment filename
            
        Returns:
            Response with Base64 encoded file content
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DOWNLOAD, params
        )
