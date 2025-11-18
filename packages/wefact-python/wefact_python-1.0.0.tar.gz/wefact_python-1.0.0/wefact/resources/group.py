"""Group resource for WeFact API."""

from .base import BaseResource


class GroupResource(BaseResource):
    """
    Group resource for managing debtor/creditor groups.
    
    Supports standard CRUD operations (list, show, create, edit, delete).
    """
    
    controller_name = "group"
