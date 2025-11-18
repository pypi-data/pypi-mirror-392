"""Environment file (.env) handler utilities"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key, unset_key


def get_env_file_path() -> Path:
    """Get the path to the .env file"""
    return Path(__file__).parent.parent.parent / ".env"


def load_env() -> None:
    """Load environment variables from .env file"""
    env_path = get_env_file_path()
    load_dotenv(env_path)


def get_env_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a value from environment variables"""
    return os.getenv(key, default)


def set_env_value(key: str, value: str) -> bool:
    """
    Set a value in the .env file
    
    Args:
        key: Environment variable key
        value: Value to set
    
    Returns:
        True if successful, False otherwise
    """
    env_path = get_env_file_path()
    
    try:
        # Create .env if it doesn't exist
        if not env_path.exists():
            env_path.touch()
        
        # Set the key-value pair
        set_key(env_path, key, value)
        
        # Reload environment
        load_env()
        return True
    except Exception as e:
        print(f"Error setting environment variable: {e}")
        return False


def delete_env_value(key: str, silent: bool = False) -> bool:
    """
    Delete a key from the .env file
    
    Args:
        key: Environment variable key to delete
        silent: If True, suppress error messages
    
    Returns:
        True if successful, False otherwise
    """
    env_path = get_env_file_path()
    
    try:
        if env_path.exists():
            unset_key(env_path, key)
            load_env()
        return True
    except Exception as e:
        if not silent:
            print(f"Error deleting environment variable: {e}")
        return False


def ensure_api_key() -> Optional[str]:
    """
    Ensure API key exists, prompt if missing
    
    Returns:
        API key or None if user cancels
    """
    from rich.console import Console
    from rich.prompt import Prompt
    
    console = Console()
    api_key = get_env_value("WEFACT_API_KEY")
    
    if not api_key:
        console.print("\n[yellow]⚠ WeFact API key not found in .env file[/yellow]")
        api_key = Prompt.ask("Please enter your WeFact API key")
        
        if api_key:
            if set_env_value("WEFACT_API_KEY", api_key):
                console.print("[green]✓ API key saved to .env[/green]")
            else:
                console.print("[red]✗ Failed to save API key[/red]")
                return None
    
    return api_key


def ensure_test_email() -> Optional[str]:
    """
    Ensure test email is configured, prompt if not found.
    This email will be used for test debtors to prevent sending emails to real customers.
    
    Returns:
        Test email address or None if not available
    """
    from rich.console import Console
    from rich.prompt import Prompt
    
    console = Console()
    test_email = get_env_value("WEFACT_TEST_EMAIL")
    
    if not test_email:
        console.print("\n[yellow]⚠ Test email not configured[/yellow]")
        console.print("[dim]When testing email-sending features (invoices, reminders, etc.),\n"
                     "emails will be sent to this address instead of real customers.[/dim]\n")
        
        test_email = Prompt.ask("Enter your test email address", default="")
        
        if test_email and "@" in test_email:
            set_env_value("WEFACT_TEST_EMAIL", test_email)
            console.print(f"[green]✓ Test email saved: {test_email}[/green]")
        else:
            console.print("[red]Invalid email address[/red]")
            return None
    
    return test_email


def get_test_debtor_code() -> Optional[str]:
    """
    Get the test debtor code used for email testing.
    
    Returns:
        Test debtor code or None
    """
    return get_env_value("WEFACT_TEST_DEBTOR_CODE")


def set_test_debtor_code(debtor_code: str) -> bool:
    """
    Save the test debtor code to .env
    
    Args:
        debtor_code: DebtorCode to save
    
    Returns:
        True if successful
    """
    return set_env_value("WEFACT_TEST_DEBTOR_CODE", debtor_code)


def save_dummy_ids(endpoint: str, ids: list[str]) -> bool:
    """
    Save dummy data IDs for an endpoint
    
    Args:
        endpoint: Endpoint name (e.g., 'debtor', 'product')
        ids: List of identifiers
    
    Returns:
        True if successful
    """
    key = f"DUMMY_{endpoint.upper()}_IDS"
    value = ",".join(ids)
    return set_env_value(key, value)


def mark_dummy_data_initialized() -> bool:
    """Mark that dummy data has been initialized"""
    return set_env_value("WEFACT_DUMMY_DATA_INITIALIZED", "true")


def clear_dummy_data_flags() -> bool:
    """Clear all dummy data flags and IDs from .env"""
    endpoints = [
        "DEBTOR", "PRODUCT", "CREDITOR", "GROUP", "INVOICE",
        "QUOTE", "SUBSCRIPTION", "INTERACTION", "TASK",
        "TRANSACTION", "COST_CATEGORY"
    ]
    
    success = True
    
    # Clear the initialized flag (silently)
    success &= delete_env_value("WEFACT_DUMMY_DATA_INITIALIZED", silent=True)
    
    # Clear all dummy ID lists (silently)
    for endpoint in endpoints:
        key = f"DUMMY_{endpoint}_IDS"
        success &= delete_env_value(key, silent=True)
    
    return success


def get_all_dummy_ids() -> dict[str, list[str]]:
    """
    Get all dummy IDs from environment
    
    Returns:
        Dictionary mapping endpoint names to lists of IDs
    """
    endpoints = [
        "debtor", "product", "creditor", "group", "invoice",
        "quote", "subscription", "interaction", "task",
        "transaction", "cost_category"
    ]
    
    result = {}
    for endpoint in endpoints:
        key = f"DUMMY_{endpoint.upper()}_IDS"
        ids_str = get_env_value(key, "")
        if ids_str:
            result[endpoint] = [id.strip() for id in ids_str.split(",") if id.strip()]
    
    return result


def get_downloads_dir() -> Path:
    """
    Get the downloads directory for saving invoices, PDFs, etc.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path to the downloads directory
    """
    downloads_dir = Path(__file__).parent.parent.parent / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    return downloads_dir


def save_invoice_pdf(invoice_code: str, pdf_content: bytes, filename: str = None) -> Path:
    """
    Save an invoice PDF to the downloads directory.
    
    Args:
        invoice_code: The invoice code (e.g., "F2024-001")
        pdf_content: The PDF file content as bytes
        filename: Optional custom filename (defaults to invoice_code.pdf)
    
    Returns:
        Path to the saved file
    """
    downloads_dir = get_downloads_dir()
    
    if filename is None:
        # Sanitize invoice code for filename
        safe_code = invoice_code.replace("/", "-").replace("\\", "-")
        filename = f"{safe_code}.pdf"
    
    filepath = downloads_dir / filename
    filepath.write_bytes(pdf_content)
    
    return filepath

