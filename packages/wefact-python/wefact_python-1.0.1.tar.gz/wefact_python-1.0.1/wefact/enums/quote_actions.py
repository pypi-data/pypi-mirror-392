from enum import Enum


class QuoteAction(str, Enum):
    SEND_BY_EMAIL = "sendbyemail"
    DOWNLOAD = "download"
    SCHEDULE = "schedule"
    CANCEL_SCHEDULE = "cancelschedule"
    ACCEPT = "accept"
    DECLINE = "decline"
    ARCHIVE = "archive"
    SORT_LINES = "sortlines"
    PRICE_QUOTE_LINE_ADD = "pricequotelineadd"
    PRICE_QUOTE_LINE_DELETE = "pricequotelinedelete"
