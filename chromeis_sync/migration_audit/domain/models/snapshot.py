from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, datetime
from decimal import Decimal
from typing import List, Optional


@dataclass(slots=True)
class SnapshotItem:
    idx: int
    item_code: str
    item_name: str
    description: str

    qty: Decimal
    rate: Decimal
    amount: Decimal

    income_account: Optional[str] = None
    cost_center: Optional[str] = None

    warehouse: Optional[str] = None
    project: Optional[str] = None

    custom_whmcs_service_id: Optional[int] = None
    custom_whmcs_domain_id: Optional[int] = None
    custom_whmcs_addon_id: Optional[int] = None
    custom_whmcs_config_id: Optional[int] = None


@dataclass(slots=True)
class SnapshotTax:
    idx: int
    account_head: str
    charge_type: str
    rate: Decimal
    tax_amount: Decimal
    description: Optional[str] = None


@dataclass(slots=True)
class SnapshotGLEntry:
    account: str
    debit: Decimal
    credit: Decimal

    cost_center: Optional[str] = None
    against: Optional[str] = None
    remarks: Optional[str] = None


@dataclass(slots=True)
class SnapshotHeader:
    invoice_name: str

    customer: str
    customer_name: str

    company: str
    currency: str

    posting_date: date
    posting_time: time
    due_date: date

    whmcs_invoice_id: Optional[int]
    custom_whmcs_client_id: Optional[int]

    remarks: Optional[str]

    grand_total: Decimal
    net_total: Decimal
    rounded_total: Decimal
    outstanding_amount: Decimal

    cost_center: Optional[str]


@dataclass(slots=True)
class SnapshotInvoice:
    header: SnapshotHeader

    items: List[SnapshotItem] = field(default_factory=list)
    taxes: List[SnapshotTax] = field(default_factory=list)
    gl_entries: List[SnapshotGLEntry] = field(default_factory=list)

    created_at: Optional[datetime] = None
