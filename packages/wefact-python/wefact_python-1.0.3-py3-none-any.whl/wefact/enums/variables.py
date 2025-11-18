"""
WeFact API Variables/Constants

These enums provide both Dutch (API values) and English equivalents
for better developer experience.

Based on: https://developer.wefact.com/variable-list
"""

from enum import Enum


class PricePeriod(str, Enum):
    """Product price periods / Subscription billing frequencies"""
    NONE = ""  # No subscription / Geen abonnement
    DAILY = "d"  # Day / Dag
    WEEKLY = "w"  # Week / Week
    MONTHLY = "m"  # Month / Maand
    QUARTERLY = "k"  # Quarter / Kwartaal
    HALF_YEARLY = "h"  # Half year / Halfjaar
    YEARLY = "j"  # Year / Jaar
    BIANNUAL = "t"  # Two years / Twee jaar
    
    # English aliases
    DAY = "d"
    WEEK = "w"
    MONTH = "m"
    QUARTER = "k"
    HALF_YEAR = "h"
    YEAR = "j"
    TWO_YEARS = "t"


class SendMethod(str, Enum):
    """Invoice/Quote sending methods / Verzendmethode"""
    EMAIL = "0"  # Per e-mail
    POST = "1"  # Per post
    EMAIL_AND_POST = "3"  # Per e-mail en post
    DEBTOR_PREFERENCE = ""  # Uses debtor preference / Gebruikt de debiteur voorkeur


class PaymentMethod(str, Enum):
    """Payment methods / Betaalmethode"""
    WIRE = "wire"  # Bank transfer / Bankoverschrijving
    CASH = "cash"  # Cash payment / Contante betaling
    CARD = "card"  # Pin/Card payment / Betaling via pin
    AUTH = "auth"  # Direct debit / Automatische incasso
    ACCOUNTING = "accounting"  # Via accounting package / Via boekhoudpakket
    VARIOUS = "various"  # Multiple methods / Verschillende betaalmethoden
    PAYPAL = "paypal"  # PayPal
    IDEAL = "ideal"  # iDEAL
    QRCODE = "qrcode"  # QR Code
    OTHER = "other"  # Online payment method / Online betaalmethode
    
    # English aliases
    BANK_TRANSFER = "wire"
    DIRECT_DEBIT = "auth"


class InvoiceStatus(str, Enum):
    """Invoice statuses / Factuur status"""
    CONCEPT = "0"  # Draft invoice / Concept factuur
    SENT = "2"  # Sent / Verzonden
    PARTIALLY_PAID = "3"  # Partially paid / Deels betaald
    PAID = "4"  # Paid / Betaald
    CREDIT = "8"  # Credit invoice / Creditfactuur
    EXPIRED = "9"  # Expired / Vervallen
    
    # English aliases
    DRAFT = "0"


class CreditInvoiceStatus(str, Enum):
    """Credit invoice (purchase) statuses / Inkoopfactuur status"""
    NOT_PAID = "1"  # Not yet paid / Nog niet betaald
    PARTIALLY_PAID = "2"  # Partially paid / Deels betaald
    PAID = "3"  # Paid / Betaald
    CREDIT = "8"  # Credit invoice / Creditfactuur


class QuoteStatus(str, Enum):
    """Quote statuses / Offerte status"""
    CONCEPT = "0"  # Draft quote / Concept offerte
    SENT = "2"  # Sent / Verzonden
    ACCEPTED = "3"  # Accepted / Geaccepteerd
    INVOICE_CREATED = "4"  # Invoice created / Factuur aangemaakt
    DECLINED = "8"  # Declined / Geweigerd
    
    # English aliases
    DRAFT = "0"
    REJECTED = "8"


class SubscriptionStatus(str, Enum):
    """Subscription statuses / Abonnement status"""
    ACTIVE = "active"  # All active subscriptions / Alle actieve abonnementen
    TERMINATED = "terminated"  # Terminated subscriptions / Opgezegde abonnementen
    
    # English aliases
    CANCELLED = "terminated"


class TaskStatus(str, Enum):
    """Task statuses / Taak status"""
    OPEN = "open"  # Open
    IN_PROGRESS = "in_progress"  # In progress / In uitvoering
    COMPLETED = "completed"  # Completed / Voltooid
    
    # English aliases
    DONE = "completed"


class CommunicationMethod(str, Enum):
    """Interaction communication methods / Interactie contact via"""
    PHONE = "phone"  # Phone / Contact via telefoon
    WHATSAPP = "whatsapp"  # WhatsApp / Contact via Whatsapp
    CHAT = "whatsapp"  # Chat / Contact via chat (for now uses WhatsApp)
    EMAIL = "email"  # Email / Contact via e-mail
    POST = "post"  # Mail / Contact per post
    IN_PERSON = "in_person"  # In person / Persoonlijk contact
    
    # English aliases
    MAIL = "post"
    FACE_TO_FACE = "in_person"


class EntityType(str, Enum):
    """Entity types for interactions/tasks / Aan interacties/taken te koppelen entiteitstypes"""
    UNLINKED = "unlinked"  # Not linked / Niet gekoppeld
    DEBTOR = "debtor"  # Linked to customer / Gekoppeld aan een klant
    CREDITOR = "creditor"  # Linked to supplier / Gekoppeld aan een leverancier
    INVOICE = "invoice"  # Linked to invoice / Gekoppeld aan een factuur
    QUOTE = "pricequote"  # Linked to quote / Gekoppeld aan een offerte
    CREDIT_INVOICE = "creditinvoice"  # Linked to purchase invoice / Gekoppeld aan een inkoopfactuur
    UNPROCESSED_CREDIT_INVOICE = "unprocessed_creditinvoice"  # Linked to unprocessed purchase / Gekoppeld aan een onverwerkte inkoopfactuur
    SUBSCRIPTION = "subscription"  # Linked to subscription / Gekoppeld aan een abonnement
    
    # English aliases
    CUSTOMER = "debtor"
    SUPPLIER = "creditor"
    PRICE_QUOTE = "pricequote"
    PURCHASE_INVOICE = "creditinvoice"


class Currency(str, Enum):
    """Currency codes (if activated in the administration) / Valuta"""
    ANG = "ANG"  # Netherlands Antillean Guilder
    AED = "AED"  # UAE Dirham
    AUD = "AUD"  # Australian Dollar
    AWG = "AWG"  # Aruban Florin
    BGN = "BGN"  # Bulgarian Lev
    BRL = "BRL"  # Brazilian Real
    CAD = "CAD"  # Canadian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan Renminbi
    CZK = "CZK"  # Czech Koruna
    DKK = "DKK"  # Danish Krone
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    HKD = "HKD"  # Hong Kong Dollar
    HRK = "HRK"  # Croatian Kuna
    HUF = "HUF"  # Hungarian Forint
    ILS = "ILS"  # Israeli Shekel
    INR = "INR"  # Indian Rupee
    ISK = "ISK"  # Icelandic Krona
    JPY = "JPY"  # Japanese Yen
    MAD = "MAD"  # Moroccan Dirham
    MXN = "MXN"  # Mexican Peso
    MYR = "MYR"  # Malaysian Ringgit
    NOK = "NOK"  # Norwegian Krone
    NZD = "NZD"  # New Zealand Dollar
    PHP = "PHP"  # Philippine Peso
    PLN = "PLN"  # Polish Zloty
    QAR = "QAR"  # Qatari Rial
    RON = "RON"  # Romanian Leu
    RUB = "RUB"  # Russian Ruble
    SEK = "SEK"  # Swedish Krona
    SGD = "SGD"  # Singapore Dollar
    THB = "THB"  # Thai Baht
    TRY = "TRY"  # Turkish Lira
    TWD = "TWD"  # New Taiwan Dollar
    USD = "USD"  # US Dollar
    ZAR = "ZAR"  # South African Rand


class BoolInt(str, Enum):
    """Boolean values as 0/1 strings / Boolean waarden als 0/1"""
    NO = "0"  # No / Nee
    YES = "1"  # Yes / Ja
    
    # English aliases
    FALSE = "0"
    TRUE = "1"


class YesNo(str, Enum):
    """Boolean values as yes/no strings / Boolean waarden als ja/nee"""
    NO = "no"  # No / Nee
    YES = "yes"  # Yes / Ja


class VatCalculation(str, Enum):
    """VAT calculation method / BTW berekeningswijze"""
    EXCLUSIVE = "excl"  # Price exclusive of VAT / Prijs exclusief BTW
    INCLUSIVE = "incl"  # Price inclusive of VAT / Prijs inclusief BTW
    
    # English aliases
    EXCL = "excl"
    INCL = "incl"


class Gender(str, Enum):
    """Gender / Geslacht"""
    MALE = "m"  # Male / Man
    FEMALE = "f"  # Female / Vrouw
    DIVERSE = "d"  # Diverse / Divers
    FAMILY = "fam"  # Family / Familie
    UNKNOWN = "u"  # Unknown / Onbekend
    
    # English aliases
    M = "m"
    F = "f"
    D = "d"
    FAM = "fam"
    U = "u"


class InvoiceSubStatus(str, Enum):
    """Invoice sub-status / Factuur substatus"""
    BLOCKED = "BLOCKED"  # Blocked / Geblokkeerd
    PAUSED = "PAUSED"  # Paused / Gepauzeerd


class PeriodicType(str, Enum):
    """Invoice line periodic type / Factuurregel periodiek type"""
    ONCE = "once"  # One-time / Eenmalig
    PERIOD = "period"  # Periodic / Periodiek


# Helper functions to convert between enum names and values
def get_enum_value(enum_class, name_or_value):
    """
    Get enum value from name or value (case-insensitive)
    
    Usage:
        get_enum_value(PricePeriod, 'MONTHLY')  # Returns 'm'
        get_enum_value(PricePeriod, 'month')    # Returns 'm'
        get_enum_value(PricePeriod, 'm')        # Returns 'm'
    """
    name_upper = str(name_or_value).upper()
    
    # Check if it's already a valid value
    for item in enum_class:
        if item.value == name_or_value:
            return item.value
    
    # Check if it's a name
    try:
        return enum_class[name_upper].value
    except KeyError:
        # Check for partial matches in names
        for item in enum_class:
            if name_upper in item.name:
                return item.value
        raise ValueError(f"Invalid {enum_class.__name__}: {name_or_value}")


def get_enum_name(enum_class, value):
    """
    Get enum name from value
    
    Usage:
        get_enum_name(PricePeriod, 'm')  # Returns 'MONTHLY'
    """
    for item in enum_class:
        if item.value == value:
            return item.name
    raise ValueError(f"Invalid {enum_class.__name__} value: {value}")
