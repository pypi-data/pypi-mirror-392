from __future__ import annotations

from .resources import (
    InvoiceResource,
    CreditInvoiceResource,
    DebtorResource,
    ProductResource,
    CreditorResource,
    GroupResource,
    SubscriptionResource,
    SettingsResource,
    CostCategoryResource,
    InteractionResource,
    QuoteResource,
    TaskResource,
    TransactionResource,
)


class WeFact:
    def __init__(self, api_key: str, api_url: str = "https://api.mijnwefact.nl/v2/"):
        if not isinstance(api_key, str):
            raise TypeError(
                f"api_key must be a string, got {type(api_key).__name__}. "
                "Did you forget quotes? Use: WeFact(api_key='your_key_here')"
            )
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")
        
        self.api_key = api_key
        self.api_url = api_url

    @property
    def invoices(self) -> InvoiceResource:
        return InvoiceResource(self.api_key, self.api_url)

    @property
    def credit_invoices(self) -> CreditInvoiceResource:
        return CreditInvoiceResource(self.api_key, self.api_url)

    @property
    def debtors(self) -> DebtorResource:
        return DebtorResource(self.api_key, self.api_url)

    @property
    def products(self) -> ProductResource:
        return ProductResource(self.api_key, self.api_url)

    @property
    def creditors(self) -> CreditorResource:
        return CreditorResource(self.api_key, self.api_url)

    @property
    def groups(self) -> GroupResource:
        return GroupResource(self.api_key, self.api_url)

    @property
    def subscriptions(self) -> SubscriptionResource:
        return SubscriptionResource(self.api_key, self.api_url)

    @property
    def settings(self) -> SettingsResource:
        return SettingsResource(self.api_key, self.api_url)

    @property
    def cost_categories(self) -> CostCategoryResource:
        return CostCategoryResource(self.api_key, self.api_url)

    @property
    def interactions(self) -> InteractionResource:
        return InteractionResource(self.api_key, self.api_url)

    @property
    def quotes(self) -> QuoteResource:
        return QuoteResource(self.api_key, self.api_url)

    @property
    def tasks(self) -> TaskResource:
        return TaskResource(self.api_key, self.api_url)

    @property
    def transactions(self) -> TransactionResource:
        return TransactionResource(self.api_key, self.api_url)
