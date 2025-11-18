from enum import Enum


class DebtorAction(str, Enum):
    EXTRA_CLIENT_CONTACT_ADD = "extraclientcontactadd"
    EXTRA_CLIENT_CONTACT_EDIT = "extraclientcontactedit"
    EXTRA_CLIENT_CONTACT_DELETE = "extraclientcontactdelete"
