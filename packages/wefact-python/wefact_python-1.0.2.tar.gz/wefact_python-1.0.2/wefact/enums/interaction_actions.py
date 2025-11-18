from enum import Enum


class InteractionAction(str, Enum):
    ATTACHMENT_ADD = "attachmentadd"
    ATTACHMENT_DELETE = "attachmentdelete"
    ATTACHMENT_DOWNLOAD = "attachmentdownload"
