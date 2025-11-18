"""
Invoice-specific endpoint tester with state management and lifecycle testing.

This tester handles the complex dependencies between invoice endpoints:
- Draft invoices: can be edited, blocked, scheduled, deleted
- Sent invoices: can be reminded, summated, partially paid, credited
- Paid invoices: can be marked unpaid
- Blocked invoices: can be unblocked

IMPORTANT: This tester uses the existing test debtor (configured during
dummy data initialization) to prevent sending emails to real customers.
It creates new invoices for each test run.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from wefact_cli.endpoints.base_tester import BaseEndpointTester, TesterResult
from wefact_cli.utils import get_test_debtor_code


class InvoiceTester(BaseEndpointTester):
    """Specialized tester for invoice endpoints with state management."""
    
    def __init__(self, wefact_client, resource_name: str = 'invoice'):
        super().__init__(wefact_client, resource_name)
        self.console = Console()
        # Track created invoices for cleanup
        self.test_invoices: Dict[str, Dict[str, Any]] = {}
    
    def _get_test_debtor_code(self) -> Optional[str]:
        """
        Get the test debtor code from environment.
        This debtor should be created during dummy data initialization.
        
        Returns:
            Test debtor code or None if not found
        """
        debtor_code = get_test_debtor_code()
        if not debtor_code:
            self.console.print("\n[red]⚠ Test debtor not found![/red]")
            self.console.print("[yellow]Please run 'Initialize Dummy Data' first to create a test debtor.[/yellow]")
            self.console.print("[dim]This ensures emails are sent to your test email address, not real customers.[/dim]\n")
        return debtor_code
    
    def _get_invoice_status_name(self, status: int) -> str:
        """Get human-readable status name."""
        statuses = {
            0: "Draft",
            2: "Sent",
            3: "Partially Paid",
            4: "Paid",
            5: "Overdue",
            8: "Credit Invoice"
        }
        return statuses.get(status, f"Unknown ({status})")
    
    def _create_test_invoice(self, debtor_code: str, status: int = 0, 
                            send: bool = False, **kwargs) -> Dict[str, Any]:
        """Create a test invoice with specified status."""
        params = {
            'DebtorCode': debtor_code,
            'InvoiceLines': [
                {
                    'Number': 1,
                    'Description': 'Test Product for Invoice Testing',
                    'PriceExcl': 100.00,
                    'TaxPercentage': 21
                }
            ],
            'Status': status,
            **kwargs
        }
        
        result = self.resource.create(**params)
        
        if result.get('status') == 'success' and 'invoice' in result:
            invoice = result['invoice']
            # If we need it sent, send it
            if send and invoice['Status'] == 0:
                send_result = self.resource.send_by_email(
                    Identifier=invoice['Identifier']
                )
                if send_result.get('status') == 'success':
                    invoice = send_result.get('invoice', invoice)
            
            return invoice
        
        return {}
    
    def test_full_lifecycle(self, debtor_code: Optional[str] = None) -> Dict[str, TesterResult]:
        """
        Test the complete invoice lifecycle with state transitions.
        
        Args:
            debtor_code: Optional existing debtor code. If not provided, uses the test debtor
                        from dummy data initialization.
        
        Flow:
        1. Create draft invoice
        2. Edit invoice (add discount)
        3. Add invoice line
        4. Sort invoice lines
        5. Block invoice
        6. Unblock invoice
        7. Schedule invoice
        8. Cancel schedule
        9. Send invoice by email
        10. Send reminder
        11. Send summation
        12. Add part payment
        13. Mark as paid
        14. Mark as unpaid
        15. Credit invoice
        16. Delete draft (cleanup)
        """
        results = {}
        self.console.print("\n[bold cyan]📋 Testing Complete Invoice Lifecycle[/bold cyan]\n")
        
        # Get test debtor if none provided
        if not debtor_code:
            debtor_code = self._get_test_debtor_code()
            if not debtor_code:
                return {
                    'setup_error': TesterResult(
                        success=False,
                        message="Test debtor not found - run 'Initialize Dummy Data' first",
                        endpoint="setup",
                        response={}
                    )
                }
            self.console.print(f"[dim]Using test debtor: {debtor_code}[/dim]\n")
        
        # Step 1: Create draft invoice
        self.console.print("[yellow]Step 1:[/yellow] Creating draft invoice...")
        invoice = self._create_test_invoice(debtor_code)
        if not invoice:
            results['create_draft'] = TesterResult(
                success=False,
                message="Failed to create draft invoice",
                endpoint="create",
                response={}
            )
            return results
        
        invoice_id = invoice['Identifier']
        invoice_code = invoice['InvoiceCode']
        results['create_draft'] = TesterResult(
            success=True,
            message=f"Created draft invoice {invoice_code}",
            endpoint="create",
            response={'invoice': invoice}
        )
        self.console.print(f"[green]✓[/green] Created {invoice_code} (Status: {self._get_invoice_status_name(invoice['Status'])})")
        
        # Step 2: Edit invoice
        self.console.print("\n[yellow]Step 2:[/yellow] Editing invoice (adding 10% discount)...")
        try:
            edit_result = self.resource.edit(
                Identifier=invoice_id,
                Discount=10,
                Term=30
            )
            results['edit'] = TesterResult(
                success=edit_result.get('status') == 'success',
                message="Edited invoice successfully" if edit_result.get('status') == 'success' else "Edit failed",
                endpoint="edit",
                response=edit_result
            )
            if results['edit'].success:
                self.console.print("[green]✓[/green] Invoice edited (10% discount, 30 days term)")
        except Exception as e:
            results['edit'] = TesterResult(success=False, message=str(e), endpoint="edit", response={})
            self.console.print(f"[red]✗[/red] Edit failed: {e}")
        
        # Step 3: Add invoice line
        self.console.print("\n[yellow]Step 3:[/yellow] Adding additional invoice line...")
        try:
            add_line_result = self.resource.invoice_line_add(
                Identifier=invoice_id,
                InvoiceLines=[{
                    'Number': 2,
                    'Description': 'Additional service',
                    'PriceExcl': 50.00,
                    'TaxPercentage': 21
                }]
            )
            results['add_line'] = TesterResult(
                success=add_line_result.get('status') == 'success',
                message="Added invoice line" if add_line_result.get('status') == 'success' else "Failed to add line",
                endpoint="invoice_line_add",
                response=add_line_result
            )
            if results['add_line'].success:
                self.console.print("[green]✓[/green] Added invoice line")
        except Exception as e:
            results['add_line'] = TesterResult(success=False, message=str(e), endpoint="invoice_line_add", response={})
            self.console.print(f"[red]✗[/red] Add line failed: {e}")
        
        # Step 4: Block invoice
        self.console.print("\n[yellow]Step 4:[/yellow] Blocking invoice...")
        try:
            block_result = self.resource.block(InvoiceCode=invoice_code)
            results['block'] = TesterResult(
                success=block_result.get('status') == 'success',
                message="Blocked invoice" if block_result.get('status') == 'success' else "Block failed",
                endpoint="block",
                response=block_result
            )
            if results['block'].success:
                self.console.print("[green]✓[/green] Invoice blocked")
        except Exception as e:
            results['block'] = TesterResult(success=False, message=str(e), endpoint="block", response={})
            self.console.print(f"[red]✗[/red] Block failed: {e}")
        
        # Step 5: Unblock invoice
        self.console.print("\n[yellow]Step 5:[/yellow] Unblocking invoice...")
        try:
            unblock_result = self.resource.unblock(InvoiceCode=invoice_code)
            results['unblock'] = TesterResult(
                success=unblock_result.get('status') == 'success',
                message="Unblocked invoice" if unblock_result.get('status') == 'success' else "Unblock failed",
                endpoint="unblock",
                response=unblock_result
            )
            if results['unblock'].success:
                self.console.print("[green]✓[/green] Invoice unblocked")
        except Exception as e:
            results['unblock'] = TesterResult(success=False, message=str(e), endpoint="unblock", response={})
            self.console.print(f"[red]✗[/red] Unblock failed: {e}")
        
        # Step 6: Schedule invoice
        scheduled_at = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        self.console.print(f"\n[yellow]Step 6:[/yellow] Scheduling invoice for {scheduled_at}...")
        try:
            schedule_result = self.resource.schedule(
                InvoiceCode=invoice_code,
                ScheduledAt=scheduled_at
            )
            results['schedule'] = TesterResult(
                success=schedule_result.get('status') == 'success',
                message=f"Scheduled for {scheduled_at}" if schedule_result.get('status') == 'success' else "Schedule failed",
                endpoint="schedule",
                response=schedule_result
            )
            if results['schedule'].success:
                self.console.print("[green]✓[/green] Invoice scheduled")
        except Exception as e:
            results['schedule'] = TesterResult(success=False, message=str(e), endpoint="schedule", response={})
            self.console.print(f"[red]✗[/red] Schedule failed: {e}")
        
        # Step 7: Cancel schedule
        self.console.print("\n[yellow]Step 7:[/yellow] Canceling schedule...")
        try:
            cancel_result = self.resource.cancel_schedule(InvoiceCode=invoice_code)
            results['cancel_schedule'] = TesterResult(
                success=cancel_result.get('status') == 'success',
                message="Schedule canceled" if cancel_result.get('status') == 'success' else "Cancel failed",
                endpoint="cancel_schedule",
                response=cancel_result
            )
            if results['cancel_schedule'].success:
                self.console.print("[green]✓[/green] Schedule canceled")
        except Exception as e:
            results['cancel_schedule'] = TesterResult(success=False, message=str(e), endpoint="cancel_schedule", response={})
            self.console.print(f"[red]✗[/red] Cancel schedule failed: {e}")
        
        # Step 8: Send invoice
        self.console.print("\n[yellow]Step 8:[/yellow] Sending invoice by email...")
        try:
            send_result = self.resource.send_by_email(InvoiceCode=invoice_code)
            results['send_by_email'] = TesterResult(
                success=send_result.get('status') == 'success',
                message="Invoice sent" if send_result.get('status') == 'success' else "Send failed",
                endpoint="send_by_email",
                response=send_result
            )
            if results['send_by_email'].success:
                self.console.print("[green]✓[/green] Invoice sent by email")
                # Update invoice object
                if 'invoice' in send_result:
                    invoice = send_result['invoice']
        except Exception as e:
            results['send_by_email'] = TesterResult(success=False, message=str(e), endpoint="send_by_email", response={})
            self.console.print(f"[red]✗[/red] Send failed: {e}")
        
        # Step 9: Send reminder (only if invoice was sent)
        if results.get('send_by_email', TesterResult(False, "", "", {})).success:
            self.console.print("\n[yellow]Step 9:[/yellow] Sending reminder email...")
            try:
                reminder_result = self.resource.send_reminder_by_email(InvoiceCode=invoice_code)
                results['send_reminder'] = TesterResult(
                    success=reminder_result.get('status') == 'success',
                    message="Reminder sent" if reminder_result.get('status') == 'success' else "Reminder failed",
                    endpoint="send_reminder_by_email",
                    response=reminder_result
                )
                if results['send_reminder'].success:
                    self.console.print("[green]✓[/green] Reminder sent")
            except Exception as e:
                results['send_reminder'] = TesterResult(success=False, message=str(e), endpoint="send_reminder_by_email", response={})
                self.console.print(f"[red]✗[/red] Reminder failed: {e}")
            
            # Step 10: Send summation
            self.console.print("\n[yellow]Step 10:[/yellow] Sending summation email...")
            try:
                summation_result = self.resource.send_summation_by_email(InvoiceCode=invoice_code)
                results['send_summation'] = TesterResult(
                    success=summation_result.get('status') == 'success',
                    message="Summation sent" if summation_result.get('status') == 'success' else "Summation failed",
                    endpoint="send_summation_by_email",
                    response=summation_result
                )
                if results['send_summation'].success:
                    self.console.print("[green]✓[/green] Summation sent")
            except Exception as e:
                results['send_summation'] = TesterResult(success=False, message=str(e), endpoint="send_summation_by_email", response={})
                self.console.print(f"[red]✗[/red] Summation failed: {e}")
            
            # Step 11: Part payment
            self.console.print("\n[yellow]Step 11:[/yellow] Processing part payment (€50)...")
            try:
                part_payment_result = self.resource.part_payment(
                    InvoiceCode=invoice_code,
                    AmountPaid=50.00
                )
                results['part_payment'] = TesterResult(
                    success=part_payment_result.get('status') == 'success',
                    message="Part payment processed" if part_payment_result.get('status') == 'success' else "Part payment failed",
                    endpoint="part_payment",
                    response=part_payment_result
                )
                if results['part_payment'].success:
                    self.console.print("[green]✓[/green] Part payment processed")
            except Exception as e:
                results['part_payment'] = TesterResult(success=False, message=str(e), endpoint="part_payment", response={})
                self.console.print(f"[red]✗[/red] Part payment failed: {e}")
            
            # Step 12: Mark as paid
            self.console.print("\n[yellow]Step 12:[/yellow] Marking invoice as paid...")
            try:
                mark_paid_result = self.resource.mark_as_paid(InvoiceCode=invoice_code)
                results['mark_as_paid'] = TesterResult(
                    success=mark_paid_result.get('status') == 'success',
                    message="Marked as paid" if mark_paid_result.get('status') == 'success' else "Mark paid failed",
                    endpoint="mark_as_paid",
                    response=mark_paid_result
                )
                if results['mark_as_paid'].success:
                    self.console.print("[green]✓[/green] Invoice marked as paid")
            except Exception as e:
                results['mark_as_paid'] = TesterResult(success=False, message=str(e), endpoint="mark_as_paid", response={})
                self.console.print(f"[red]✗[/red] Mark paid failed: {e}")
            
            # Step 13: Mark as unpaid
            self.console.print("\n[yellow]Step 13:[/yellow] Marking invoice as unpaid...")
            try:
                mark_unpaid_result = self.resource.mark_as_unpaid(InvoiceCode=invoice_code)
                results['mark_as_unpaid'] = TesterResult(
                    success=mark_unpaid_result.get('status') == 'success',
                    message="Marked as unpaid" if mark_unpaid_result.get('status') == 'success' else "Mark unpaid failed",
                    endpoint="mark_as_unpaid",
                    response=mark_unpaid_result
                )
                if results['mark_as_unpaid'].success:
                    self.console.print("[green]✓[/green] Invoice marked as unpaid")
            except Exception as e:
                results['mark_as_unpaid'] = TesterResult(success=False, message=str(e), endpoint="mark_as_unpaid", response={})
                self.console.print(f"[red]✗[/red] Mark unpaid failed: {e}")
            
            # Step 14: Payment process pause
            pause_end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            self.console.print(f"\n[yellow]Step 14:[/yellow] Pausing payment process until {pause_end_date}...")
            try:
                pause_result = self.resource.payment_process_pause(
                    InvoiceCode=invoice_code,
                    PaymentPausedEndDate=pause_end_date,
                    PaymentPausedReason="Testing payment pause functionality"
                )
                results['payment_pause'] = TesterResult(
                    success=pause_result.get('status') == 'success',
                    message="Payment process paused" if pause_result.get('status') == 'success' else "Pause failed",
                    endpoint="payment_process_pause",
                    response=pause_result
                )
                if results['payment_pause'].success:
                    self.console.print("[green]✓[/green] Payment process paused")
            except Exception as e:
                results['payment_pause'] = TesterResult(success=False, message=str(e), endpoint="payment_process_pause", response={})
                self.console.print(f"[red]✗[/red] Payment pause failed: {e}")
            
            # Step 15: Payment process reactivate
            self.console.print("\n[yellow]Step 15:[/yellow] Reactivating payment process...")
            try:
                reactivate_result = self.resource.payment_process_reactivate(InvoiceCode=invoice_code)
                results['payment_reactivate'] = TesterResult(
                    success=reactivate_result.get('status') == 'success',
                    message="Payment process reactivated" if reactivate_result.get('status') == 'success' else "Reactivate failed",
                    endpoint="payment_process_reactivate",
                    response=reactivate_result
                )
                if results['payment_reactivate'].success:
                    self.console.print("[green]✓[/green] Payment process reactivated")
            except Exception as e:
                results['payment_reactivate'] = TesterResult(success=False, message=str(e), endpoint="payment_process_reactivate", response={})
                self.console.print(f"[red]✗[/red] Payment reactivate failed: {e}")
            
            # Step 16: Download invoice
            self.console.print("\n[yellow]Step 16:[/yellow] Downloading invoice PDF...")
            try:
                download_result = self.resource.download(InvoiceCode=invoice_code)
                results['download'] = TesterResult(
                    success=download_result.get('status') == 'success' and 'invoice' in download_result,
                    message="Downloaded PDF" if download_result.get('status') == 'success' else "Download failed",
                    endpoint="download",
                    response=download_result
                )
                if results['download'].success:
                    # Save the PDF to downloads folder
                    import base64
                    from ..utils import save_invoice_pdf
                    
                    invoice_data = download_result.get('invoice', {})
                    if 'Base64' in invoice_data:
                        pdf_content = base64.b64decode(invoice_data['Base64'])
                        filename = invoice_data.get('Filename', f'{invoice_code}.pdf')
                        filepath = save_invoice_pdf(invoice_code, pdf_content, filename)
                        self.console.print(f"[green]✓[/green] Invoice PDF downloaded and saved to: {filepath}")
                    else:
                        self.console.print("[green]✓[/green] Invoice PDF downloaded (no content to save)")
            except Exception as e:
                results['download'] = TesterResult(success=False, message=str(e), endpoint="download", response={})
                self.console.print(f"[red]✗[/red] Download failed: {e}")
            
            # Step 17: Credit invoice
            self.console.print("\n[yellow]Step 17:[/yellow] Creating credit invoice...")
            try:
                credit_result = self.resource.credit(InvoiceCode=invoice_code)
                results['credit'] = TesterResult(
                    success=credit_result.get('status') == 'success',
                    message="Credit invoice created" if credit_result.get('status') == 'success' else "Credit failed",
                    endpoint="credit",
                    response=credit_result
                )
                if results['credit'].success:
                    credit_invoice = credit_result.get('invoice', {})
                    credit_code = credit_invoice.get('InvoiceCode', 'unknown')
                    self.console.print(f"[green]✓[/green] Credit invoice created: {credit_code}")
            except Exception as e:
                results['credit'] = TesterResult(success=False, message=str(e), endpoint="credit", response={})
                self.console.print(f"[red]✗[/red] Credit failed: {e}")
        
        # Summary
        self.console.print("\n[bold cyan]📊 Lifecycle Test Summary[/bold cyan]")
        passed = sum(1 for r in results.values() if r.success)
        total = len(results)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Message", style="dim")
        
        for endpoint_name, result in results.items():
            status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
            table.add_row(endpoint_name, status, result.message)
        
        self.console.print(table)
        self.console.print(f"\n[bold]Results:[/bold] {passed}/{total} tests passed")
        
        return results
    
    def test_attachment_workflow(self, debtor_code: Optional[str] = None) -> Dict[str, TesterResult]:
        """
        Test invoice attachment operations.
        
        Args:
            debtor_code: Optional existing debtor code. If not provided, uses the test debtor
                        from dummy data initialization.
        """
        results = {}
        self.console.print("\n[bold cyan]📎 Testing Invoice Attachments[/bold cyan]\n")
        
        # Get test debtor if none provided
        if not debtor_code:
            debtor_code = self._get_test_debtor_code()
            if not debtor_code:
                return {
                    'setup_error': TesterResult(
                        success=False,
                        message="Test debtor not found - run 'Initialize Dummy Data' first",
                        endpoint="setup",
                        response={}
                    )
                }
            self.console.print(f"[dim]Using test debtor: {debtor_code}[/dim]\n")
        
        # Create a draft invoice
        invoice = self._create_test_invoice(debtor_code)
        if not invoice:
            return {'error': TesterResult(False, "Failed to create test invoice", "create", {})}
        
        invoice_id = invoice['Identifier']
        invoice_code = invoice['InvoiceCode']
        
        # Test attachment add
        self.console.print(f"[yellow]Adding attachment to {invoice_code}...[/yellow]")
        try:
            # Create a simple PDF in base64 (minimal PDF)
            import base64
            pdf_content = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
            base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
            
            add_result = self.resource.attachment_add(
                ReferenceIdentifier=invoice_id,
                Filename="test_attachment.pdf",
                Base64=base64_pdf
            )
            results['add_attachment'] = TesterResult(
                success=add_result.get('status') == 'success',
                message="Attachment added" if add_result.get('status') == 'success' else "Add failed",
                endpoint="attachment_add",
                response=add_result
            )
            if results['add_attachment'].success:
                self.console.print("[green]✓[/green] Attachment added")
        except Exception as e:
            results['add_attachment'] = TesterResult(False, str(e), "attachment_add", {})
            self.console.print(f"[red]✗[/red] Add attachment failed: {e}")
        
        # Test attachment download (if add succeeded)
        if results.get('add_attachment', TesterResult(False, "", "", {})).success:
            self.console.print("\n[yellow]Downloading attachment...[/yellow]")
            try:
                download_result = self.resource.attachment_download(
                    ReferenceIdentifier=invoice_id,
                    Filename="test_attachment.pdf"
                )
                results['download_attachment'] = TesterResult(
                    success=download_result.get('status') == 'success',
                    message="Attachment downloaded" if download_result.get('status') == 'success' else "Download failed",
                    endpoint="attachment_download",
                    response=download_result
                )
                if results['download_attachment'].success:
                    self.console.print("[green]✓[/green] Attachment downloaded")
            except Exception as e:
                results['download_attachment'] = TesterResult(False, str(e), "attachment_download", {})
                self.console.print(f"[red]✗[/red] Download attachment failed: {e}")
            
            # Test attachment delete
            self.console.print("\n[yellow]Deleting attachment...[/yellow]")
            try:
                delete_result = self.resource.attachment_delete(
                    ReferenceIdentifier=invoice_id,
                    Filename="test_attachment.pdf"
                )
                results['delete_attachment'] = TesterResult(
                    success=delete_result.get('status') == 'success',
                    message="Attachment deleted" if delete_result.get('status') == 'success' else "Delete failed",
                    endpoint="attachment_delete",
                    response=delete_result
                )
                if results['delete_attachment'].success:
                    self.console.print("[green]✓[/green] Attachment deleted")
            except Exception as e:
                results['delete_attachment'] = TesterResult(False, str(e), "attachment_delete", {})
                self.console.print(f"[red]✗[/red] Delete attachment failed: {e}")
        
        # Cleanup: delete the test invoice
        try:
            self.resource.delete(InvoiceCode=invoice_code)
            self.console.print(f"[dim]Deleted test invoice {invoice_code}[/dim]")
        except:
            pass
        
        return results
