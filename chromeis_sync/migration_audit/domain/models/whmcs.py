from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional


# ============================================================
# WHMCS Invoice Item
# ============================================================

@dataclass(slots=True)
class WHMCSItem:
    id: int

    invoice_id: int
    user_id: int

    type: str
    relid: int

    description: str

    amount: Decimal

    taxed: bool

    due_date: Optional[date]

    payment_method: Optional[str] = None
    notes: Optional[str] = None


# ============================================================
# WHMCS Tax
# ============================================================

@dataclass(slots=True)
class WHMCSTax:
    level: int

    rate: Decimal

    amount: Decimal


# ============================================================
# WHMCS Invoice Header
# ============================================================

@dataclass(slots=True)
class WHMCSHeader:
    invoice_id: int

    userid: int

    status: str

    date: date
    due_date: Optional[date]

    subtotal: Decimal
    tax: Decimal
    tax2: Decimal
    credit: Decimal
    total: Decimal

    payment_method: Optional[str] = None
    notes: Optional[str] = None


# ============================================================
# WHMCS Invoice
# ============================================================

@dataclass(slots=True)
class WHMCSInvoice:
    header: WHMCSHeader

    items: List[WHMCSItem] = field(default_factory=list)

    taxes: List[WHMCSTax] = field(default_factory=list)

    created_at: Optional[datetime] = None

# ============================================================
# WHMCS Payment
# ============================================================

@dataclass(slots=True)
class WHMCSPayment:
    id: int

    invoice_id: int
    user_id: int

    amount: Decimal

    payment_date: datetime

    transaction_id: Optional[str] = None

    gateway: Optional[str] = None

    fees: Decimal = Decimal("0.00")

    currency: Optional[str] = None

    exchange_rate: Optional[Decimal] = None

    notes: Optional[str] = None
