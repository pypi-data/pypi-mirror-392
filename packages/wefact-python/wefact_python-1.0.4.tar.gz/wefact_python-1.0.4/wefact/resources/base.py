"""Base resource class for all WeFact API resources."""

from __future__ import annotations
from typing import Any, Dict, List

from ..request import RequestMixin
from ..enums import Action


class BaseResource(RequestMixin):
    """
    Base class for all WeFact API resources.

    Provides common CRUD operations (list, show, create, edit, delete) that
    work for most resources. Individual resources can override or extend these.
    """

    controller_name: str

    def __init__(self, api_key: str, api_url: str = "https://api.mijnwefact.nl/v2/"):
        self.api_key = api_key
        self.api_url = api_url

    def list(self, **params) -> Dict[str, Any]:
        """List items with optional filtering and pagination."""
        return self._send_request(self.controller_name, Action.LIST, params)

    def list_all(self, offset: int = 0, per_page: int = 1000) -> List[Dict[str, Any]]:
        """
        List all items with automatic pagination and detailed information.

        Note: This makes one API call per item for full details, which can be slow
        for large datasets. Use with caution and respect rate limits.
        """
        limit_per_second = 300 / 60
        calls = 1
        data: List[Dict[str, Any]] = []
        plural_name = self.get_plural_resource_name()

        result = self.list(limit=per_page, offset=offset)

        for index, item in enumerate(result.get(plural_name, [])):
            calls += 1
            if calls % limit_per_second == 0:
                import time

                time.sleep(1)
            detail = self.show(Identifier=item["Identifier"])
            if isinstance(detail, dict) and self.controller_name in detail:
                result[plural_name][index] = detail[self.controller_name]

        data.extend(result.get(plural_name, []))

        if result.get("currentresults", 0) >= per_page:
            data.extend(self.list_all(offset + per_page, per_page))

        return data

    def show(self, **params) -> Dict[str, Any]:
        """Get detailed information about a specific item."""
        return self._send_request(self.controller_name, Action.SHOW, params)

    def create(self, **params) -> Dict[str, Any]:
        """Create a new item."""
        return self._send_request(self.controller_name, Action.ADD, params)

    def edit(self, **params) -> Dict[str, Any]:
        """Update an existing item."""
        return self._send_request(self.controller_name, Action.EDIT, params)

    def delete(self, **params) -> Dict[str, Any]:
        """Delete an item."""
        return self._send_request(self.controller_name, Action.DELETE, params)

    def get_plural_resource_name(self) -> str:
        """Get the plural name for this resource (used in API responses)."""
        return f"{self.controller_name}s"
