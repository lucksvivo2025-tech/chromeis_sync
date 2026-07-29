from __future__ import annotations

from chromeis_sync.migration_audit.application.invoice_integrity_engine import (
    InvoiceIntegrityEngine,
)


def run(invoice_id: int = 620):

    engine = InvoiceIntegrityEngine()

    result = engine.validate(invoice_id)

    print()
    print("=" * 60)
    print(f"Invoice Integrity Report ({invoice_id})")
    print("=" * 60)
    print(f"Status       : {result.status}")
    print(f"Header Total : {result.header_total}")
    print(f"Item Total   : {result.item_total}")
    print(f"Difference   : {result.difference}")
    print(f"Item Count   : {result.item_count}")
    print(f"Valid        : {result.valid}")
    print("=" * 60)
    print()

    return {
        "status": result.status,
        "header_total": str(result.header_total),
        "item_total": str(result.item_total),
        "difference": str(result.difference),
        "item_count": result.item_count,
        "valid": result.valid,
    }
