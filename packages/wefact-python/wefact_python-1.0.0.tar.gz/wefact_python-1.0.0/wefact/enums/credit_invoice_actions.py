"""Credit Invoice specific actions for WeFact API."""

from enum import Enum


class CreditInvoiceAction(Enum):
    """Actions specific to credit invoices (purchase invoices)."""
    
    PART_PAYMENT = "partpayment"
    MARK_AS_PAID = "markaspaid"
    CREDIT_INVOICE_LINE_ADD = "creditinvoiceline/add"
    CREDIT_INVOICE_LINE_DELETE = "creditinvoiceline/delete"
