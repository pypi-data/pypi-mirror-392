"""Subscription resource for WeFact API."""

from .base import BaseResource
from ..enums.subscription_actions import SubscriptionAction
from ..exceptions import ClientError


class SubscriptionResource(BaseResource):
    """
    Subscription resource for managing recurring subscriptions.
    
    Supports CRUD operations (except delete) and termination.
    """
    
    controller_name = "subscription"

    def delete(self, **params):
        """Delete is not available for subscriptions. Use terminate() instead."""
        raise ClientError("delete is not available for this resource.")

    def terminate(self, **params):
        """
        Terminate a subscription.
        
        Args:
            Identifier: Subscription ID (numeric string)
            SubscriptionCode: Or use subscription code
            TerminationDate: Optional (defaults to today)
            
        Returns:
            Terminated subscription details
        """
        return self._send_request(
            self.controller_name, SubscriptionAction.TERMINATE, params
        )
