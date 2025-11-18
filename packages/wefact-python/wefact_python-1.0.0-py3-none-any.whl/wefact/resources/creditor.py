"""Creditor (supplier) resource for WeFact API."""

from .base import BaseResource
from ..enums import Action


class CreditorResource(BaseResource):
    """
    Creditor resource for managing suppliers.
    
    Supports CRUD operations and attachments.
    """
    
    controller_name = "creditor"

    # Attachments
    
    def attachment_add(self, **params):
        """
        Add an attachment to a creditor.
        
        Args:
            ReferenceIdentifier: Creditor ID (numeric string)
            CreditorCode: Or use creditor code
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
        Delete an attachment from a creditor.
        
        Args:
            ReferenceIdentifier: Creditor ID (numeric string)
            CreditorCode: Or use creditor code
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
        Download a creditor attachment.
        
        Args:
            ReferenceIdentifier: Creditor ID (numeric string)
            CreditorCode: Or use creditor code
            Filename: Attachment filename
            
        Returns:
            Response with Base64 encoded file
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DOWNLOAD, params
        )
