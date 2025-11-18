"""Utility modules for WeFact CLI"""

from .env_handler import (
    load_env,
    get_env_value,
    set_env_value,
    ensure_api_key,
    ensure_test_email,
    get_test_debtor_code,
    set_test_debtor_code,
    save_dummy_ids,
    mark_dummy_data_initialized,
    clear_dummy_data_flags,
    get_all_dummy_ids,
    get_downloads_dir,
    save_invoice_pdf,
)
from .validators import (
    validate_api_key,
    validate_response,
    is_success_response,
)
from .formatters import (
    format_json,
    format_error,
    format_duration,
)
from .data_helpers import (
    safe_float,
    safe_int,
    format_currency,
    format_percentage,
    normalize_api_response,
    get_display_name,
)

__all__ = [
    "load_env",
    "get_env_value",
    "set_env_value",
    "ensure_api_key",
    "ensure_test_email",
    "get_test_debtor_code",
    "set_test_debtor_code",
    "save_dummy_ids",
    "mark_dummy_data_initialized",
    "clear_dummy_data_flags",
    "get_all_dummy_ids",
    "get_downloads_dir",
    "save_invoice_pdf",
    "validate_api_key",
    "validate_response",
    "is_success_response",
    "format_json",
    "format_error",
    "format_duration",
    "safe_float",
    "safe_int",
    "format_currency",
    "format_percentage",
    "normalize_api_response",
    "get_display_name",
    "normalize_api_response",
    "get_display_name",
]
