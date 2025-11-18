"""Interaction resource for WeFact API."""

from .base import BaseResource
from ..enums import Action
from ..enums.interaction_actions import InteractionAction


class InteractionResource(BaseResource):
    """
    Interaction resource for managing communications and interactions.
    
    Supports CRUD operations and attachments.
    """
    
    controller_name = "interaction"

    # Attachments
    def attachment_add(self, **params):
        """
        Add an attachment to an interaction.
        
        Args:
            ReferenceIdentifier: Interaction ID (numeric string)
            Filename: Attachment filename
            Base64: Base64 encoded file content
            
        Returns:
            Success confirmation
        """
        return self._send_request(
            self.controller_name, InteractionAction.ATTACHMENT_ADD, params
        )

    def attachment_delete(self, **params):
        """
        Delete an attachment from an interaction.
        
        Args:
            ReferenceIdentifier: Interaction ID (numeric string)
            Identifier: Attachment ID (numeric string)
            Filename: Or use filename instead of Identifier
            
        Returns:
            Success confirmation
        """
        return self._send_request(
            self.controller_name, InteractionAction.ATTACHMENT_DELETE, params
        )

    def attachment_download(self, **params):
        """
        Download an interaction attachment.
        
        Args:
            ReferenceIdentifier: Interaction ID (numeric string)
            Identifier: Attachment ID (numeric string)
            Filename: Or use filename instead of Identifier
            
        Returns:
            Array with [AttachmentId, Filename, Base64Content, MimeType]
        """
        return self._send_request(
            self.controller_name, InteractionAction.ATTACHMENT_DOWNLOAD, params
        )
