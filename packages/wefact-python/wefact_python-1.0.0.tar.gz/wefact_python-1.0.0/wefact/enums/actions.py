from enum import Enum

class Action(str, Enum):
    LIST = 'list'
    SHOW = 'show'
    ADD = 'add'
    EDIT = 'edit'
    DELETE = 'delete'
    # Generic cross-controller actions
    SEND_BY_EMAIL = 'sendbyemail'
    DOWNLOAD = 'download'
    SCHEDULE = 'schedule'
    CANCEL_SCHEDULE = 'cancelschedule'
    SORT_LINES = 'sortlines'
    ATTACHMENT_ADD = 'attachmentadd'
    ATTACHMENT_DELETE = 'attachmentdelete'
    ATTACHMENT_DOWNLOAD = 'attachmentdownload'
