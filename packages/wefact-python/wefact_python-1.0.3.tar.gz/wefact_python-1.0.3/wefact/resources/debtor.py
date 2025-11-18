"""Debtor (client/customer) resource for WeFact API."""

from .base import BaseResource
from ..enums import Action
from ..enums.debtor_actions import DebtorAction
from ..exceptions import ClientError


class DebtorResource(BaseResource):
    """
    Debtor resource for managing clients/customers.
    
    Supports CRUD operations, extra contacts, and attachments.
    Note: Delete is not available for debtors.
    """
    
    controller_name = "debtor"

    def delete(self, **params):
        """Delete is not available for debtors."""
        raise ClientError("delete is not available for this resource.")

    # Extra client contact management
    
    def extra_client_contact_add(self, **params):
        """
        Add an extra contact person to a debtor.
        
        Args:
            Identifier: Debtor ID (numeric string)
            DebtorCode: Or use debtor code (e.g., "DB10000")
            EmailAddress: Required
            FirstName: Optional
            LastName: Optional
            Gender: Optional ('m' or 'f')
            TelephoneNumber: Optional
            
        Returns:
            Debtor with new contact added
        """
        return self._send_request(
            self.controller_name, DebtorAction.EXTRA_CLIENT_CONTACT_ADD, params
        )

    def extra_client_contact_edit(self, **params):
        """
        Edit an extra contact person.
        
        Args:
            Identifier: Debtor ID (numeric string)
            DebtorCode: Or use debtor code (e.g., "DB10000")
            ContactIdentifier: Contact ID
            EmailAddress: Optional
            FirstName: Optional
            LastName: Optional
            Gender: Optional
            TelephoneNumber: Optional
            
        Returns:
            Debtor with updated contact
        """
        return self._send_request(
            self.controller_name, DebtorAction.EXTRA_CLIENT_CONTACT_EDIT, params
        )

    def extra_client_contact_delete(self, **params):
        """
        Delete an extra contact person.
        
        Args:
            Identifier: Debtor ID (numeric string)
            DebtorCode: Or use debtor code (e.g., "DB10000")
            ContactIdentifier: Contact ID
            
        Returns:
            Debtor with contact removed
        """
        return self._send_request(
            self.controller_name, DebtorAction.EXTRA_CLIENT_CONTACT_DELETE, params
        )

    # Attachments
    
    def attachment_add(self, **params):
        """
        Add an attachment to a debtor.
        
        Args:
            ReferenceIdentifier: Debtor ID (numeric string)
            DebtorCode: Or use debtor code (e.g., "DB10000")
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
        Delete an attachment from a debtor.
        
        Args:
            ReferenceIdentifier: Debtor ID (numeric string)
            DebtorCode: Or use debtor code (e.g., "DB10000")
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
        Download a debtor attachment.
        
        Args:
            ReferenceIdentifier: Debtor ID (numeric string)
            DebtorCode: Or use debtor code (e.g., "DB10000")
            Filename: Attachment filename
            
        Returns:
            Response with Base64 encoded file
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DOWNLOAD, params
        )
