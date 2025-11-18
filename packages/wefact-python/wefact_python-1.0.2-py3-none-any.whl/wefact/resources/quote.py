"""Price Quote resource for WeFact API."""

from .base import BaseResource
from ..enums import Action, QuoteAction


class QuoteResource(BaseResource):
    """
    Quote (Price Quote) resource for managing quotations.
    
    Supports CRUD operations, email sending, status management, line operations,
    and attachments.
    """
    
    controller_name = "pricequote"

    # Email and document operations
    
    def send_by_email(self, **params):
        """
        Send quote by email.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            
        Returns:
            Success confirmation
        """
        return self._send_request(
            self.controller_name, QuoteAction.SEND_BY_EMAIL, params
        )

    def download(self, **params):
        """
        Download quote PDF.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            
        Returns:
            Response with Base64 encoded PDF
        """
        return self._send_request(
            self.controller_name, QuoteAction.DOWNLOAD, params
        )

    # Scheduling
    
    def schedule(self, **params):
        """
        Schedule a quote to be sent automatically.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            ScheduledAt: Required (datetime string)
            
        Returns:
            Quote with ScheduledAt set
        """
        return self._send_request(
            self.controller_name, QuoteAction.SCHEDULE, params
        )

    def cancel_schedule(self, **params):
        """
        Cancel a scheduled quote send.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            
        Returns:
            Quote with ScheduledAt cleared
        """
        return self._send_request(
            self.controller_name, QuoteAction.CANCEL_SCHEDULE, params
        )

    # Status management
    
    def accept(self, **params):
        """
        Mark quote as accepted.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            
        Returns:
            Quote with accepted status
        """
        return self._send_request(
            self.controller_name, QuoteAction.ACCEPT, params
        )

    def decline(self, **params):
        """
        Mark quote as declined.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            
        Returns:
            Quote with declined status
        """
        return self._send_request(
            self.controller_name, QuoteAction.DECLINE, params
        )

    def archive(self, **params):
        """
        Archive a quote.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            
        Returns:
            Archived quote
        """
        return self._send_request(
            self.controller_name, QuoteAction.ARCHIVE, params
        )

    # Line management
    
    def sort_lines(self, **params):
        """
        Reorder quote lines.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            PriceQuoteLines: Required (array of {Identifier: line_id})
            
        Returns:
            Quote with lines in new order
        """
        return self._send_request(
            self.controller_name, QuoteAction.SORT_LINES, params
        )

    def price_quote_line_add(self, **params):
        """
        Add one or more lines to a quote.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            PriceQuoteLines: Required (array of line objects)
            
        Returns:
            Quote with new lines added
        """
        return self._send_request(
            self.controller_name, QuoteAction.PRICE_QUOTE_LINE_ADD, params
        )

    def price_quote_line_delete(self, **params):
        """
        Delete one or more lines from a quote.
        
        Args:
            Identifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            PriceQuoteLines: Required (array of {Identifier: line_id})
            
        Returns:
            Quote with lines removed
        """
        return self._send_request(
            self.controller_name, QuoteAction.PRICE_QUOTE_LINE_DELETE, params
        )

    # Attachments
    
    def attachment_add(self, **params):
        """
        Add an attachment to a quote.
        
        Args:
            ReferenceIdentifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
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
        Delete an attachment from a quote.
        
        Args:
            ReferenceIdentifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
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
        Download a quote attachment.
        
        Args:
            ReferenceIdentifier: Quote ID (numeric string)
            PriceQuoteCode: Or use quote code
            Filename: Attachment filename
            
        Returns:
            Response with Base64 encoded file
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DOWNLOAD, params
        )
