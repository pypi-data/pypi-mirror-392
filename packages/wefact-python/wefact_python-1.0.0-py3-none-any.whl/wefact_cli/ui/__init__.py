"""UI components for the CLI"""

from .prompts import (
    prompt_api_key,
    prompt_initialize_dummy_data,
    prompt_select_endpoint,
    prompt_select_action,
    confirm_action,
)
from .tables import (
    render_test_results,
    render_endpoint_menu,
    render_dummy_data_summary,
    render_main_menu,
    render_test_summary,
    render_settings,
)
from .panels import (
    create_header,
    create_status_panel,
    create_help_panel,
    create_welcome_panel,
    create_success_panel,
    create_error_panel,
)

__all__ = [
    "prompt_api_key",
    "prompt_initialize_dummy_data",
    "prompt_select_endpoint",
    "prompt_select_action",
    "confirm_action",
    "render_test_results",
    "render_endpoint_menu",
    "render_dummy_data_summary",
    "render_main_menu",
    "render_test_summary",
    "render_settings",
    "create_header",
    "create_status_panel",
    "create_help_panel",
    "create_welcome_panel",
    "create_success_panel",
    "create_error_panel",
]
