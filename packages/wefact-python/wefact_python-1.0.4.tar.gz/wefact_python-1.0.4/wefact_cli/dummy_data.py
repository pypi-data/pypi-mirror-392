"""Dummy data generator for WeFact API testing"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from faker import Faker
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from wefact import WeFact
from wefact.enums import PricePeriod, CommunicationMethod
from .utils import save_dummy_ids, mark_dummy_data_initialized
from .utils.validators import is_success_response


class DummyDataGenerator:
    """Generate realistic dummy/test data for all WeFact endpoints"""
    
    def __init__(self, client: WeFact):
        """
        Initialize the dummy data generator
        
        Args:
            client: Authenticated WeFact client instance
        """
        self.client = client
        self.faker = Faker('nl_NL')  # Dutch locale for realistic data
        self.console = Console()
        
        # Store created IDs for cross-reference
        self.created_ids: Dict[str, List[str]] = {
            'debtor': [],
            'product': [],
            'creditor': [],
            'group': [],
            'invoice': [],
            'quote': [],
            'subscription': [],
            'interaction': [],
            'task': [],
            'transaction': [],
            'cost_category': [],
        }
    
    def generate_all(self, count: int = 5) -> Dict[str, List[str]]:
        """
        Generate dummy data for all endpoints
        
        Args:
            count: Number of items to create per endpoint
        
        Returns:
            Dictionary mapping endpoint names to created IDs
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            # Define generation order (dependencies matter!)
            tasks_config = [
                ("Creating debtors", self.create_debtors),
                ("Creating products", self.create_products),
                ("Creating creditors", self.create_creditors),
                ("Creating groups", self.create_groups),
                ("Creating cost categories", self.create_cost_categories),
                ("Creating invoices", self.create_invoices),
                ("Creating quotes", self.create_quotes),
                ("Creating subscriptions", self.create_subscriptions),
                ("Creating interactions", self.create_interactions),
                ("Creating tasks", self.create_tasks),
                # Skipping transactions as they're typically bank-imported
            ]
            
            main_task = progress.add_task("[cyan]Generating dummy data...", total=len(tasks_config))
            
            for task_desc, task_func in tasks_config:
                progress.update(main_task, description=f"[cyan]{task_desc}...")
                try:
                    task_func(count)
                    progress.update(main_task, advance=1)
                except Exception as e:
                    self.console.print(f"[red]Error in {task_desc}: {e}[/red]")
                    progress.update(main_task, advance=1)
        
        # Save all IDs to .env
        self._save_all_ids()
        
        return self.created_ids
    
    def create_debtors(self, count: int = 5) -> List[str]:
        """Create dummy debtor records"""
        ids = []
        
        for i in range(count):
            company = self.faker.company()
            data = {
                'CompanyName': company,
                'Initials': self.faker.first_name()[:1],
                'SurName': self.faker.last_name(),
                'Address': self.faker.street_address(),
                'ZipCode': self.faker.postcode(),
                'City': self.faker.city(),
                'Country': 'NL',
                'EmailAddress': self.faker.company_email(),
                'PhoneNumber': self.faker.phone_number(),
            }
            
            try:
                response = self.client.debtors.create(**data)
                if is_success_response(response) and 'debtor' in response:
                    # Store DebtorCode (string like 'DB10001'), not Identifier (int)
                    debtor_code = response['debtor'].get('DebtorCode')
                    if debtor_code:
                        ids.append(str(debtor_code))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create debtor {i+1}: {e}[/yellow]")
        
        self.created_ids['debtor'] = ids
        return ids
    def create_products(self, count: int = 5) -> List[str]:
        """Create dummy product records"""
        ids = []
        
        product_types = [
            ("Website Hosting", "hosting", 9.99, PricePeriod.MONTHLY),
            ("Domain Registration", "domain", 14.99, PricePeriod.YEARLY),
            ("Email Service", "email", 4.99, PricePeriod.MONTHLY),
            ("SSL Certificate", "ssl", 29.99, PricePeriod.YEARLY),
            ("Support Package", "support", 49.99, PricePeriod.MONTHLY),
            ("Backup Service", "backup", 19.99, PricePeriod.MONTHLY),
            ("Premium Hosting", "premium-hosting", 24.99, PricePeriod.MONTHLY),
        ]
        
        for i in range(min(count, len(product_types))):
            name, keyphrase, price, period = product_types[i]
            data = {
                'ProductName': name,
                'ProductKeyPhrase': keyphrase,
                'PriceExcl': price,
                'PricePeriod': period.value,  # Convert enum to API value
                'TaxPercentage': 21.0,  # Dutch VAT
            }
            
            try:
                response = self.client.products.create(**data)
                if is_success_response(response) and 'product' in response:
                    # Store ProductCode (string like 'P0001'), not Identifier (int)
                    product_code = response['product'].get('ProductCode')
                    if product_code:
                        ids.append(str(product_code))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create product {i+1}: {e}[/yellow]")
        
        self.created_ids['product'] = ids
        return ids
    
    def create_creditors(self, count: int = 5) -> List[str]:
        """Create dummy creditor records"""
        ids = []
        
        for i in range(count):
            company = f"{self.faker.company()} B.V."
            data = {
                'CompanyName': company,
                'ContactName': self.faker.name(),
                'Address': self.faker.street_address(),
                'ZipCode': self.faker.postcode(),
                'City': self.faker.city(),
                'Country': 'NL',
                'EmailAddress': self.faker.company_email(),
                'PhoneNumber': self.faker.phone_number(),
            }
            
            try:
                response = self.client.creditors.create(**data)
                if is_success_response(response) and 'creditor' in response:
                    # Store CreditorCode (string like 'CD10001'), not Identifier (int)
                    creditor_code = response['creditor'].get('CreditorCode')
                    if creditor_code:
                        ids.append(str(creditor_code))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create creditor {i+1}: {e}[/yellow]")
        
        self.created_ids['creditor'] = ids
        return ids
    
    def create_groups(self, count: int = 5) -> List[str]:
        """Create dummy group records"""
        ids = []
        
        group_configs = [
            ("debtor", "VIP Clients"),
            ("debtor", "Standard Clients"),
            ("debtor", "New Clients"),
            ("product", "Hosting Services"),
            ("product", "Domain Services"),
        ]
        
        for i in range(min(count, len(group_configs))):
            group_type, group_name = group_configs[i]
            # Add timestamp to make names unique
            timestamp = datetime.now().strftime('%H%M%S')
            unique_name = f"{group_name} {timestamp}"
            
            data = {
                'Type': group_type,
                'GroupName': unique_name,
            }
            
            try:
                response = self.client.groups.create(**data)
                if is_success_response(response) and 'group' in response:
                    identifier = response['group'].get('Identifier')
                    if identifier:
                        ids.append(str(identifier))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create group {i+1}: {e}[/yellow]")
        
        self.created_ids['group'] = ids
        return ids
    
    def create_cost_categories(self, count: int = 5) -> List[str]:
        """Create dummy cost category records"""
        ids = []
        
        categories = [
            "Cloud Infrastructure",
            "Software Licenses",
            "Marketing Expenses",
            "Office Supplies",
            "Professional Services",
        ]
        
        for i in range(min(count, len(categories))):
            data = {
                'Title': categories[i],
            }
            
            try:
                response = self.client.cost_categories.create(**data)
                if is_success_response(response) and 'costcategory' in response:
                    identifier = response['costcategory'].get('Identifier')
                    if identifier:
                        ids.append(str(identifier))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create cost category {i+1}: {e}[/yellow]")
        
        self.created_ids['cost_category'] = ids
        return ids
    
    def create_invoices(self, count: int = 5) -> List[str]:
        """Create dummy invoice records"""
        ids = []
        
        if not self.created_ids['debtor'] or not self.created_ids['product']:
            self.console.print("[yellow]Skipping invoices: need debtors and products first[/yellow]")
            return ids
        
        for i in range(min(count, len(self.created_ids['debtor']))):
            debtor_code = self.created_ids['debtor'][i]
            product_code = self.created_ids['product'][i % len(self.created_ids['product'])]
            
            data = {
                'DebtorCode': debtor_code,
                'InvoiceLines': [
                    {
                        'Number': 1,
                        'ProductCode': product_code,
                        'Description': f'Test service {i+1}',
                        'PriceExcl': round(self.faker.random.uniform(10, 100), 2),
                    }
                ],
            }
            
            try:
                response = self.client.invoices.create(**data)
                if is_success_response(response) and 'invoice' in response:
                    # Prefer InvoiceCode over Identifier for consistency
                    invoice_code = response['invoice'].get('InvoiceCode')
                    if invoice_code:
                        ids.append(str(invoice_code))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create invoice {i+1}: {e}[/yellow]")
        
        self.created_ids['invoice'] = ids
        return ids
    
    def create_quotes(self, count: int = 5) -> List[str]:
        """Create dummy quote records"""
        ids = []
        
        if not self.created_ids['debtor']:
            self.console.print("[yellow]Skipping quotes: need debtors first[/yellow]")
            return ids
        
        for i in range(min(count, len(self.created_ids['debtor']))):
            debtor_code = self.created_ids['debtor'][i]
            
            data = {
                'DebtorCode': debtor_code,
                'PriceQuoteLines': [
                    {
                        'Description': f'Quote service {i+1}',
                        'PriceExcl': round(self.faker.random.uniform(50, 500), 2),
                    }
                ],
            }
            
            try:
                response = self.client.quotes.create(**data)
                if is_success_response(response) and 'pricequote' in response:
                    # Prefer PriceQuoteCode over Identifier for consistency
                    quote_code = response['pricequote'].get('PriceQuoteCode')
                    if quote_code:
                        ids.append(str(quote_code))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create quote {i+1}: {e}[/yellow]")
        
        self.created_ids['quote'] = ids
        return ids
    
    def create_subscriptions(self, count: int = 5) -> List[str]:
        """Create dummy subscription records"""
        ids = []
        
        if not self.created_ids['debtor'] or not self.created_ids['product']:
            self.console.print("[yellow]Skipping subscriptions: need debtors and products first[/yellow]")
            return ids
        
        for i in range(min(count, len(self.created_ids['debtor']))):
            debtor_code = self.created_ids['debtor'][i]
            product_code = self.created_ids['product'][i % len(self.created_ids['product'])]
            
            # Subscription with minimal required fields
            # When ProductCode is provided, other fields auto-fill from product
            data = {
                'DebtorCode': debtor_code,
                'Subscription': {
                    'ProductCode': product_code,
                    'Number': 1,  # Quantity
                }
            }
            
            try:
                response = self.client.subscriptions.create(**data)
                if is_success_response(response) and 'subscription' in response:
                    identifier = response['subscription'].get('Identifier')
                    if identifier:
                        ids.append(str(identifier))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create subscription {i+1}: {e}[/yellow]")
        
        self.created_ids['subscription'] = ids
        return ids
    
    def create_interactions(self, count: int = 5) -> List[str]:
        """Create dummy interaction records"""
        ids = []
        
        if not self.created_ids['debtor']:
            self.console.print("[yellow]Skipping interactions: need debtors first[/yellow]")
            return ids
        
        interaction_subjects = [
            "Initial consultation call",
            "Follow-up meeting",
            "Support ticket discussion",
            "Contract renewal discussion",
            "Technical issue resolution",
        ]
        
        communication_methods = [
            CommunicationMethod.PHONE,
            CommunicationMethod.EMAIL,
            CommunicationMethod.IN_PERSON,
            CommunicationMethod.WHATSAPP,
            CommunicationMethod.EMAIL,
        ]
        
        for i in range(min(count, len(self.created_ids['debtor']))):
            debtor_code = self.created_ids['debtor'][i]
            
            # First, get the DebtorId from the DebtorCode
            try:
                debtor_response = self.client.debtors.show(DebtorCode=debtor_code)
                if not is_success_response(debtor_response) or 'debtor' not in debtor_response:
                    self.console.print(f"[yellow]Warning: Could not find debtor {debtor_code}[/yellow]")
                    continue
                
                debtor_id = debtor_response['debtor'].get('Identifier')
                if not debtor_id:
                    continue
                
                # Interactions require: AssigneeId, Description, CommunicationMethod, and DebtorId
                data = {
                    'AssigneeId': 1,  # Assign to user ID 1 (usually the account owner)
                    'DebtorId': debtor_id,
                    'Description': interaction_subjects[i % len(interaction_subjects)] + "\n" + self.faker.text(max_nb_chars=150),
                    'CommunicationMethod': communication_methods[i % len(communication_methods)].value,  # Convert enum to API value
                }
                
                response = self.client.interactions.create(**data)
                if is_success_response(response) and 'interaction' in response:
                    identifier = response['interaction'].get('Identifier')
                    if identifier:
                        ids.append(str(identifier))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create interaction {i+1}: {e}[/yellow]")
        
        self.created_ids['interaction'] = ids
        return ids
    
    def create_tasks(self, count: int = 5) -> List[str]:
        """Create dummy task records"""
        ids = []
        
        task_titles = [
            "Call back client",
            "Send proposal",
            "Review contract",
            "Schedule meeting",
            "Process refund",
        ]
        
        for i in range(count):
            # Tasks only require Title (all other fields are optional)
            data = {
                'Title': task_titles[i % len(task_titles)],
                'Description': self.faker.text(max_nb_chars=150),
            }
            
            # Optionally link to a debtor if available
            if self.created_ids['debtor']:
                debtor_code = self.created_ids['debtor'][i % len(self.created_ids['debtor'])]
                try:
                    debtor_response = self.client.debtors.show(DebtorCode=debtor_code)
                    if is_success_response(debtor_response) and 'debtor' in debtor_response:
                        debtor_id = debtor_response['debtor'].get('Identifier')
                        if debtor_id:
                            data['DebtorId'] = debtor_id
                except Exception:
                    pass  # Continue without debtor link
            
            try:
                response = self.client.tasks.create(**data)
                if is_success_response(response) and 'task' in response:
                    identifier = response['task'].get('Identifier')
                    if identifier:
                        ids.append(str(identifier))
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to create task {i+1}: {e}[/yellow]")
        
        self.created_ids['task'] = ids
        return ids
    
    def _save_all_ids(self) -> None:
        """Save all created IDs to .env file"""
        for endpoint, ids in self.created_ids.items():
            if ids:
                save_dummy_ids(endpoint, ids)
        
        mark_dummy_data_initialized()
    
    def clear_all(self) -> None:
        """Delete all created dummy data"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Delete in reverse order to handle dependencies
            delete_tasks = [
                ("Deleting tasks", 'task', self.client.tasks),
                ("Deleting interactions", 'interaction', self.client.interactions),
                ("Deleting subscriptions", 'subscription', self.client.subscriptions),
                ("Deleting quotes", 'quote', self.client.quotes),
                ("Deleting invoices", 'invoice', self.client.invoices),
                ("Deleting cost categories", 'cost_category', self.client.cost_categories),
                ("Deleting groups", 'group', self.client.groups),
                ("Deleting creditors", 'creditor', self.client.creditors),
                ("Deleting products", 'product', self.client.products),
                ("Deleting debtors", 'debtor', self.client.debtors),
            ]
            
            task = progress.add_task("[red]Clearing dummy data...", total=len(delete_tasks))
            
            for task_desc, endpoint, resource in delete_tasks:
                progress.update(task, description=f"[red]{task_desc}...")
                ids = self.created_ids.get(endpoint, [])
                
                for identifier in ids:
                    try:
                        # Some endpoints don't support delete
                        if hasattr(resource, 'delete'):
                            resource.delete(Identifier=identifier)
                    except Exception as e:
                        # Ignore errors during cleanup
                        pass
                
                progress.update(task, advance=1)
    
    def ensure_test_debtor(self, test_email: str) -> Optional[str]:
        """
        Create or update a test debtor for email testing.
        
        This debtor will be used for all email-sending tests to prevent
        emails from being sent to real customers.
        
        Args:
            test_email: Email address for test debtor
        
        Returns:
            DebtorCode of the test debtor, or None if failed
        """
        from .utils import get_test_debtor_code, set_test_debtor_code
        
        # Check if we already have a test debtor
        existing_code = get_test_debtor_code()
        
        if existing_code:
            # Verify it still exists and update email if needed
            try:
                response = self.client.debtors.show(DebtorCode=existing_code)
                if is_success_response(response):
                    # Update email if changed
                    current_email = response.get('debtor', {}).get('EmailAddress')
                    if current_email != test_email:
                        self.client.debtors.edit(
                            DebtorCode=existing_code,
                            EmailAddress=test_email
                        )
                        self.console.print(f"[green]✓ Updated test debtor email: {test_email}[/green]")
                    return existing_code
            except Exception:
                # Test debtor doesn't exist anymore, create new one
                pass
        
        # Create new test debtor
        self.console.print("[cyan]Creating test debtor for email testing...[/cyan]")
        
        data = {
            'CompanyName': 'TEST - DO NOT USE',
            'Initials': 'T',
            'SurName': 'Test User',
            'Address': 'Test Street 1',
            'ZipCode': '1234AB',
            'City': 'Test City',
            'Country': 'NL',
            'EmailAddress': test_email,
            'PhoneNumber': '+31 6 12345678',
            'Comment': 'This is a TEST debtor for API testing. All test emails will be sent to this debtor.'
        }
        
        try:
            response = self.client.debtors.create(**data)
            if is_success_response(response) and 'debtor' in response:
                debtor_code = response['debtor'].get('DebtorCode')
                if debtor_code:
                    set_test_debtor_code(debtor_code)
                    self.console.print(f"[green]✓ Test debtor created: {debtor_code}[/green]")
                    self.console.print(f"[dim]All test emails will be sent to: {test_email}[/dim]")
                    return debtor_code
        except Exception as e:
            self.console.print(f"[red]Failed to create test debtor: {e}[/red]")
        
        return None
