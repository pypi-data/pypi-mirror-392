"""Settings resource for WeFact API."""

from .base import BaseResource
from ..exceptions import ClientError


class SettingsResource(BaseResource):
    """
    Settings resource for retrieving account settings.
    
    Only supports list() operation. Individual CRUD operations are not available.
    """
    
    controller_name = "settings"

    def get_plural_resource_name(self) -> str:
        """Settings resource name is singular."""
        return self.controller_name

    def show(self, **params):
        """Show is not available for settings. Use list() instead."""
        raise ClientError("show is not available for this resource.")

    def create(self, **params):
        """Create is not available for settings."""
        raise ClientError("create is not available for this resource.")

    def edit(self, **params):
        """Edit is not available for settings."""
        raise ClientError("edit is not available for this resource.")

    def delete(self, **params):
        """Delete is not available for settings."""
        raise ClientError("delete is not available for this resource.")
