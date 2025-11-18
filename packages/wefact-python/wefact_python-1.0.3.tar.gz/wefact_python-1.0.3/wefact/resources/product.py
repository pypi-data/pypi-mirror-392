"""Product resource for WeFact API."""

from .base import BaseResource


class ProductResource(BaseResource):
    """
    Product resource for managing products and services.
    
    Supports standard CRUD operations (list, show, create, edit, delete).
    """
    
    controller_name = "product"
