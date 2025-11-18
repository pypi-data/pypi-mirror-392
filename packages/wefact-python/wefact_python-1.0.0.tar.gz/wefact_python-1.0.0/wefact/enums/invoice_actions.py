from enum import Enum

class InvoiceAction(str, Enum):
    CREDIT = 'credit'
    PART_PAYMENT = 'partpayment'
    MARK_AS_PAID = 'markaspaid'
    MARK_AS_UNPAID = 'markasunpaid'
    SEND_BY_EMAIL = 'sendbyemail'
    SEND_REMINDER_BY_EMAIL = 'sendreminderbyemail'
    SEND_SUMMATION_BY_EMAIL = 'sendsummationbyemail'
    DOWNLOAD = 'download'
    BLOCK = 'block'
    UNBLOCK = 'unblock'
    SCHEDULE = 'schedule'
    CANCEL_SCHEDULE = 'cancelschedule'
    PAYMENT_PROCESS_PAUSE = 'paymentprocesspause'
    PAYMENT_PROCESS_REACTIVATE = 'paymentprocessreactivate'
    SORT_LINES = 'sortlines'
    INVOICE_LINE_ADD = 'invoicelineadd'
    INVOICE_LINE_DELETE = 'invoicelinedelete'

