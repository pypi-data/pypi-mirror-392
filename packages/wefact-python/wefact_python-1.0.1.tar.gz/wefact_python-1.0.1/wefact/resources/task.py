"""Task resource for WeFact API."""

from .base import BaseResource
from ..enums import Action
from ..enums.task_actions import TaskAction


class TaskResource(BaseResource):
    """
    Task resource for managing tasks.
    
    Supports CRUD operations, status changes, and attachments.
    """
    
    controller_name = "task"

    def change_status(self, **params):
        """
        Change the status of a task.
        
        Args:
            Identifier: Task ID (numeric string)
            Status: Task status string (e.g., "open", "completed")
            
        Returns:
            Task with updated status
        """
        return self._send_request(
            self.controller_name, TaskAction.CHANGE_STATUS, params
        )

    # Attachments
    
    def attachment_add(self, **params):
        """
        Add an attachment to a task.
        
        Args:
            ReferenceIdentifier: Task ID (numeric string)
            Filename: Attachment filename
            Base64: Base64 encoded file content
            
        Note:
            Type parameter is automatically set to "crm_task"
            
        Returns:
            Success confirmation
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_ADD, params
        )

    def attachment_delete(self, **params):
        """
        Delete an attachment from a task.
        
        Args:
            ReferenceIdentifier: Task ID (numeric string)
            Identifier: Attachment ID (numeric string)
            Filename: Or use filename instead of Identifier
            
        Note:
            Type parameter is automatically set to "crm_task"
            
        Returns:
            Success confirmation
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DELETE, params
        )

    def attachment_download(self, **params):
        """
        Download a task attachment.
        
        Args:
            ReferenceIdentifier: Task ID (numeric string)
            Identifier: Attachment ID (numeric string)
            Filename: Or use filename instead of Identifier
            
        Note:
            Type parameter is automatically set to "crm_task"
            
        Returns:
            Array with [AttachmentId, Filename, Base64Content, MimeType]
        """
        params["Type"] = self.controller_name
        return self._send_request(
            self.controller_name, Action.ATTACHMENT_DOWNLOAD, params
        )
