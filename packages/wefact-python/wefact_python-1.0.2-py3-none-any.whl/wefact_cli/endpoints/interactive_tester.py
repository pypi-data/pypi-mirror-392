"""Interactive endpoint tester with context-aware flows"""

import base64
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

from ..endpoints.base_tester import BaseEndpointTester, TesterResult
from ..ui.tables import render_response_data
from ..utils.data_helpers import format_currency, safe_float
from ..utils import get_test_debtor_code, save_invoice_pdf


class InteractiveEndpointTester:
    """Enhanced tester with interactive flows for each action"""
    
    def __init__(self, resource: Any, resource_name: str, dummy_ids: List[str], console: Console):
        """
        Initialize interactive tester
        
        Args:
            resource: WeFact resource instance
            resource_name: Name of the resource
            dummy_ids: List of dummy data IDs
            console: Rich console for output
        """
        self.resource = resource
        self.resource_name = resource_name
        self.dummy_ids = dummy_ids
        self.console = console
        self.base_tester = BaseEndpointTester(resource, resource_name, dummy_ids)
    
    def test_with_flow(self, method: str) -> TesterResult:
        """
        Execute a test with appropriate interactive flow
        
        Args:
            method: Method name to test
        
        Returns:
            TesterResult object
        """
        # Normalize method name (remove underscores for lookup)
        normalized_method = method.lower().replace('_', '')
        
        # Map methods to their interactive flows
        flow_map = {
            'list': self._flow_list,
            'listall': self._flow_list_all,
            'show': self._flow_show,
            'create': self._flow_create,
            'edit': self._flow_edit,
            'delete': self._flow_delete,
            'credit': self._flow_credit,
            'markaspaid': self._flow_mark_as_paid,
            'markasunpaid': self._flow_mark_as_unpaid,
            'sendbyemail': self._flow_send_by_email,
            'sendreminderbyemail': self._flow_send_reminder_by_email,
            'sendsummationbyemail': self._flow_send_summation_by_email,
            'terminate': self._flow_terminate,
            'attachmentadd': self._flow_add_attachment,
            'attachmentdelete': self._flow_delete_attachment,
            'attachmentdownload': self._flow_download_attachment,
            'block': self._flow_block,
            'unblock': self._flow_unblock,
            'download': self._flow_download,
            'partpayment': self._flow_part_payment,
        }
        
        # Get the flow function or use default
        flow_func = flow_map.get(normalized_method, self._flow_default)
        
        return flow_func(method)
    
    def _select_item_from_list(self, title: str = "Select Item") -> Optional[Dict[str, Any]]:
        """
        List items and let user select one
        
        Args:
            title: Title for the selection
        
        Returns:
            Selected item dict or None
        """
        self.console.print(f"\n[cyan]Fetching {self.resource_name} list...[/cyan]")
        
        # Get list of items
        response = self.resource.list(limit=20)
        
        if not isinstance(response, dict):
            self.console.print("[red]Failed to fetch list[/red]")
            return None
        
        # Find the list key (pluralized resource name)
        plural_name = self.resource.get_plural_resource_name() if hasattr(self.resource, 'get_plural_resource_name') else f"{self.resource_name}s"
        items = response.get(plural_name, [])
        
        if not items:
            self.console.print(f"[yellow]No {self.resource_name}s found[/yellow]")
            return None
        
        # Display items in a table
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Identifier", style="yellow")
        
        # Add key fields based on resource type
        if self.resource_name == 'debtor':
            table.add_column("Code", style="white")
            table.add_column("Company/Name", style="white")
        elif self.resource_name == 'invoice':
            table.add_column("Code", style="white")
            table.add_column("Debtor", style="white")
            table.add_column("Amount", style="green")
        elif self.resource_name == 'product':
            table.add_column("Code", style="white")
            table.add_column("Name", style="white")
            table.add_column("Price", style="green")
        else:
            # Generic display
            table.add_column("Info", style="white")
        
        # Add rows
        for i, item in enumerate(items[:20], 1):
            identifier = str(item.get('Identifier', ''))
            
            if self.resource_name == 'debtor':
                code = item.get('DebtorCode', '')
                name = item.get('CompanyName') or f"{item.get('Initials', '')} {item.get('SurName', '')}"
                table.add_row(str(i), identifier, code, name)
            elif self.resource_name == 'invoice':
                code = item.get('InvoiceCode', '')
                debtor = item.get('Debtor', '')
                amount = format_currency(item.get('AmountExcl', 0))
                table.add_row(str(i), identifier, code, debtor, amount)
            elif self.resource_name == 'product':
                code = item.get('ProductCode', '')
                name = item.get('ProductName', '')
                price = format_currency(item.get('PriceExcl', 0))
                table.add_row(str(i), identifier, code, name, price)
            else:
                info = str(item.get('Title') or item.get('Name') or item.get('Description', ''))[:50]
                table.add_row(str(i), identifier, info)
        
        self.console.print(table)
        
        # Prompt for selection
        choice = Prompt.ask(
            "\nSelect item number (or 'b' to cancel)",
            choices=[str(i) for i in range(1, min(len(items), 20) + 1)] + ['b'],
            default='b'
        )
        
        if choice == 'b':
            return None
        
        return items[int(choice) - 1]
    
    def _create_dummy_pdf(self) -> tuple[str, str]:
        """
        Create a dummy PDF file for testing
        
        Returns:
            Tuple of (filename, base64_content)
        """
        # Create minimal PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(WeFact Test Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF
"""
        base64_content = base64.b64encode(pdf_content).decode('utf-8')
        return "test_document.pdf", base64_content
    
    # Flow implementations
    
    def _flow_list(self, method: str) -> TesterResult:
        """Interactive flow for list operation"""
        self.console.print("\n[cyan]Listing items...[/cyan]")
        
        # Ask for limit
        limit = Prompt.ask("How many items to fetch?", default="10")
        
        result = self.base_tester.test_method(method, limit=int(limit))
        
        if result.success and result.response:
            render_response_data(result.response, f"{self.resource_name.title()} List", console=self.console)
        
        return result
    
    def _flow_list_all(self, method: str) -> TesterResult:
        """Interactive flow for list_all operation"""
        self.console.print("\n[yellow]⚠ Warning: list_all fetches ALL items with detailed info[/yellow]")
        self.console.print("[dim]This may take a while for large datasets[/dim]")
        
        if not Confirm.ask("Continue?", default=False):
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Cancelled by user"
            )
        
        result = self.base_tester.test_method(method)
        
        if result.success and result.response:
            render_response_data(result.response, f"{self.resource_name.title()} Complete List", max_entries=5, console=self.console)
        
        return result
    
    def _flow_show(self, method: str) -> TesterResult:
        """Interactive flow for show operation"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to View")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success and result.response:
            render_response_data(result.response, f"{self.resource_name.title()} Details", console=self.console)
        
        return result
    
    def _flow_create(self, method: str) -> TesterResult:
        """Interactive flow for create operation"""
        self.console.print(f"\n[yellow]Create flow not yet implemented for {self.resource_name}[/yellow]")
        self.console.print("[dim]Use 'Initialize Dummy Data' from main menu to create test items[/dim]")
        
        return TesterResult(
            endpoint=self.resource_name,
            method=method,
            success=False,
            duration=0.0,
            error="Interactive create not implemented"
        )
    
    def _flow_edit(self, method: str) -> TesterResult:
        """Interactive flow for edit operation"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Edit")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        self.console.print(f"\n[yellow]Edit flow requires field input - using dummy update[/yellow]")
        
        identifier = item.get('Identifier')
        # Minimal update to test the endpoint
        params = {'Identifier': identifier}
        
        result = self.base_tester.test_method(method, **params)
        
        if result.success and result.response:
            render_response_data(result.response, f"{self.resource_name.title()} Updated", console=self.console)
        
        return result
    
    def _flow_delete(self, method: str) -> TesterResult:
        """Interactive flow for delete operation"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Delete")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        # Show confirmation
        identifier = item.get('Identifier')
        self.console.print(Panel(
            f"[red]You are about to delete:[/red]\n\n"
            f"Identifier: {identifier}\n"
            f"This action cannot be undone.",
            title="⚠ Confirm Deletion",
            border_style="red"
        ))
        
        if not Confirm.ask("Proceed with deletion?", default=False):
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Deletion cancelled by user"
            )
        
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Item deleted successfully[/green]")
        
        return result
    
    def _flow_credit(self, method: str) -> TesterResult:
        """Interactive flow for credit operation (invoices)"""
        item = self._select_item_from_list("Select Invoice to Credit")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No invoice selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success and result.response:
            render_response_data(result.response, "Credit Invoice Result", console=self.console)
        
        return result
    
    def _flow_mark_as_paid(self, method: str) -> TesterResult:
        """Interactive flow for mark as paid"""
        item = self._select_item_from_list("Select Invoice to Mark as Paid")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No invoice selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Invoice marked as paid[/green]")
        
        return result
    
    def _flow_mark_as_unpaid(self, method: str) -> TesterResult:
        """Interactive flow for mark as unpaid"""
        item = self._select_item_from_list("Select Invoice to Mark as Unpaid")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No invoice selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Invoice marked as unpaid[/green]")
        
        return result
    
    def _flow_send_by_email(self, method: str) -> TesterResult:
        """Interactive flow for sending by email"""
        # Check if test debtor is configured
        test_debtor = get_test_debtor_code()
        if test_debtor:
            self.console.print(f"[green]✓ Using test debtor: {test_debtor}[/green]")
            self.console.print("[dim]Emails will be sent to your test email address[/dim]\n")
        else:
            self.console.print("[yellow]⚠ No test debtor configured - emails will go to real addresses![/yellow]")
        
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Send by Email")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        self.console.print("[yellow]⚠ This will send an actual email![/yellow]")
        if not Confirm.ask("Continue?", default=False):
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Cancelled by user"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Email sent successfully[/green]")
        
        return result
    
    def _flow_terminate(self, method: str) -> TesterResult:
        """Interactive flow for terminate (subscriptions)"""
        item = self._select_item_from_list("Select Subscription to Terminate")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No subscription selected"
            )
        
        identifier = item.get('Identifier')
        
        self.console.print(Panel(
            f"[yellow]Terminating subscription {identifier}[/yellow]\n"
            "The subscription will be marked for termination.",
            title="Terminate Subscription",
            border_style="yellow"
        ))
        
        if not Confirm.ask("Proceed?", default=False):
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Cancelled by user"
            )
        
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Subscription terminated[/green]")
        
        return result
    
    def _flow_add_attachment(self, method: str) -> TesterResult:
        """Interactive flow for adding attachment"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Add Attachment")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        identifier = item.get('Identifier')
        
        # Create dummy PDF
        self.console.print("\n[cyan]Creating dummy PDF document...[/cyan]")
        filename, base64_content = self._create_dummy_pdf()
        
        # Use the correct WeFact API parameter names
        params = {
            'Identifier': identifier,
            'FileName': filename,
            'FileData': base64_content
        }
        
        result = self.base_tester.test_method(method, **params)
        
        if result.success:
            self.console.print(f"[green]✓ Attachment '{filename}' added successfully[/green]")
        
        return result
    
    def _flow_delete_attachment(self, method: str) -> TesterResult:
        """Interactive flow for deleting attachment"""
        self.console.print("[yellow]Delete attachment requires attachment ID - not fully implemented[/yellow]")
        
        return TesterResult(
            endpoint=self.resource_name,
            method=method,
            success=False,
            duration=0.0,
            error="Interactive attachment deletion not implemented"
        )
    
    def _flow_download_attachment(self, method: str) -> TesterResult:
        """Interactive flow for downloading attachment"""
        self.console.print("[yellow]Download attachment requires attachment ID - not fully implemented[/yellow]")
        
        return TesterResult(
            endpoint=self.resource_name,
            method=method,
            success=False,
            duration=0.0,
            error="Interactive attachment download not implemented"
        )
    
    def _flow_send_reminder_by_email(self, method: str) -> TesterResult:
        """Interactive flow for sending reminder by email"""
        # Check if test debtor is configured
        test_debtor = get_test_debtor_code()
        if test_debtor:
            self.console.print(f"[green]✓ Using test debtor: {test_debtor}[/green]")
            self.console.print("[dim]Reminder will be sent to your test email[/dim]\n")
        else:
            self.console.print("[yellow]⚠ No test debtor - reminder will go to real address![/yellow]")
        
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Send Reminder")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        self.console.print("[yellow]⚠ This will send an actual reminder email![/yellow]")
        if not Confirm.ask("Continue?", default=False):
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Cancelled by user"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Reminder email sent successfully[/green]")
        
        return result
    
    def _flow_send_summation_by_email(self, method: str) -> TesterResult:
        """Interactive flow for sending summation by email"""
        # Check if test debtor is configured
        test_debtor = get_test_debtor_code()
        if test_debtor:
            self.console.print(f"[green]✓ Using test debtor: {test_debtor}[/green]")
            self.console.print("[dim]Summation will be sent to your test email[/dim]\n")
        else:
            self.console.print("[yellow]⚠ No test debtor - summation will go to real address![/yellow]")
        
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Send Summation")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        self.console.print("[yellow]⚠ This will send an actual summation email![/yellow]")
        if not Confirm.ask("Continue?", default=False):
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Cancelled by user"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Summation email sent successfully[/green]")
        
        return result
    
    def _flow_block(self, method: str) -> TesterResult:
        """Interactive flow for blocking an item"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Block")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Item blocked successfully[/green]")
        
        return result
    
    def _flow_unblock(self, method: str) -> TesterResult:
        """Interactive flow for unblocking an item"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Unblock")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success:
            self.console.print("[green]✓ Item unblocked successfully[/green]")
        
        return result
    
    def _flow_download(self, method: str) -> TesterResult:
        """Interactive flow for downloading an item (like invoice PDF)"""
        item = self._select_item_from_list(f"Select {self.resource_name.title()} to Download")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No item selected"
            )
        
        identifier = item.get('Identifier')
        result = self.base_tester.test_method(method, Identifier=identifier)
        
        if result.success and result.response:
            # The PDF content might be in different places depending on the API
            pdf_content_b64 = None
            filename = None
            
            # Check for Base64 in nested invoice object (current WeFact API format)
            if 'invoice' in result.response and isinstance(result.response['invoice'], dict):
                if 'Base64' in result.response['invoice']:
                    pdf_content_b64 = result.response['invoice']['Base64']
                    filename = result.response['invoice'].get('Filename', None)
            # Check for Content in root (fallback for other formats)
            elif 'Content' in result.response:
                pdf_content_b64 = result.response['Content']
                filename = result.response.get('Filename', None)
            
            if pdf_content_b64:
                try:
                    # Decode base64 content
                    pdf_content = base64.b64decode(pdf_content_b64)
                    
                    # Get invoice code for filename (prefer API filename if available)
                    if filename:
                        invoice_code = filename.replace('.pdf', '')
                    else:
                        invoice_code = item.get('InvoiceCode', item.get('Code', str(identifier)))
                    
                    # Save to downloads directory
                    filepath = save_invoice_pdf(invoice_code, pdf_content)
                    
                    self.console.print(f"[green]✓ Downloaded and saved successfully![/green]")
                    self.console.print(f"[cyan]📁 {filepath}[/cyan]")
                    self.console.print(f"[dim]File size: {len(pdf_content):,} bytes[/dim]")
                except Exception as e:
                    self.console.print(f"[yellow]⚠ Download succeeded but failed to save: {e}[/yellow]")
                    content_length = len(pdf_content_b64)
                    self.console.print(f"[dim]Base64 size: {content_length:,} bytes[/dim]")
            else:
                # Show what we got to help debug
                self.console.print("[green]✓ Download successful[/green]")
                self.console.print("[yellow]⚠ No 'Base64' or 'Content' field found in response[/yellow]")
                self.console.print(f"[dim]Response keys: {list(result.response.keys())}[/dim]")
                if 'invoice' in result.response:
                    invoice_data = result.response['invoice']
                    if isinstance(invoice_data, dict):
                        self.console.print(f"[dim]Invoice keys: {list(invoice_data.keys())}[/dim]")
        
        return result
        return result
    
    def _flow_part_payment(self, method: str) -> TesterResult:
        """Interactive flow for part payment"""
        item = self._select_item_from_list("Select Invoice for Part Payment")
        
        if not item:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="No invoice selected"
            )
        
        identifier = item.get('Identifier')
        
        # Ask for payment amount
        amount = Prompt.ask("Enter payment amount", default="10.00")
        
        amount_float = safe_float(amount, None)
        if amount_float is None:
            return TesterResult(
                endpoint=self.resource_name,
                method=method,
                success=False,
                duration=0.0,
                error="Invalid amount entered"
            )
        
        result = self.base_tester.test_method(
            method, 
            Identifier=identifier,
            Amount=amount_float
        )
        
        if result.success:
            self.console.print(f"[green]✓ Part payment of €{amount_float:.2f} recorded[/green]")
        
        return result
    
    def _flow_default(self, method: str) -> TesterResult:
        """Default flow for methods without specific implementation"""
        self.console.print(f"\n[cyan]Testing {method} with default flow...[/cyan]")
        
        # Try to execute with minimal params
        result = self.base_tester.test_method(method)
        
        if result.success and result.response:
            render_response_data(result.response, f"{method.title()} Result", console=self.console)
        
        return result
