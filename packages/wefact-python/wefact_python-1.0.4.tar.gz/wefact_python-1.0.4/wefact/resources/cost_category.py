"""Cost Category resource for WeFact API."""

from .base import BaseResource
from ..enums.cost_category_actions import CostCategoryAction


class CostCategoryResource(BaseResource):
    """
    Cost Category resource for managing expense categories.
    
    Note: Cost categories use the 'settings' controller but have their own actions.
    Responses have nested structure that gets unwrapped for consistency.
    """
    
    controller_name = "settings"  # Cost categories are under the settings controller

    def get_plural_resource_name(self) -> str:
        """Cost categories use 'costcategories' as plural name."""
        return "costcategories"

    def list(self, **params):
        """
        List cost categories.
        
        Returns:
            Response with 'costcategories' array unwrapped from nested structure
        """
        response = self._send_request(
            self.controller_name, CostCategoryAction.LIST, params
        )
        # Unwrap the nested structure: {'settings': {'costcategories': [...]}}
        if 'settings' in response and 'costcategories' in response['settings']:
            return {
                **response,
                'costcategories': response['settings']['costcategories']
            }
        return response

    def show(self, **params):
        """
        Show a specific cost category.
        
        Args:
            Identifier: Required
            
        Returns:
            Response with 'costcategory' unwrapped from nested structure
        """
        response = self._send_request(
            self.controller_name, CostCategoryAction.SHOW, params
        )
        # Unwrap the nested structure if needed
        if 'settings' in response and 'costcategory' in response['settings']:
            return {
                **response,
                'costcategory': response['settings']['costcategory']
            }
        return response

    def create(self, **params):
        """
        Create a new cost category.
        
        Args:
            Title: Required
            
        Returns:
            Response with new cost category unwrapped
        """
        response = self._send_request(
            self.controller_name, CostCategoryAction.ADD, params
        )
        # Unwrap the nested structure: {'settings': {'costcategory': {...}}}
        if 'settings' in response and 'costcategory' in response['settings']:
            return {
                **response,
                'costcategory': response['settings']['costcategory']
            }
        return response

    def edit(self, **params):
        """
        Edit an existing cost category.
        
        Args:
            Identifier: Required
            Title: Optional
            
        Returns:
            Response with updated cost category unwrapped
        """
        response = self._send_request(
            self.controller_name, CostCategoryAction.EDIT, params
        )
        # Unwrap if needed
        if 'settings' in response and 'costcategory' in response['settings']:
            return {
                **response,
                'costcategory': response['settings']['costcategory']
            }
        return response

    def delete(self, **params):
        """
        Delete a cost category.
        
        Args:
            Identifier: Required
            
        Returns:
            Success confirmation
        """
        return self._send_request(
            self.controller_name, CostCategoryAction.DELETE, params
        )
