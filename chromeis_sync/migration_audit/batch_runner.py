import frappe
import time
from datetime import datetime

import frappe

from chromeis_sync.migration_audit.batch_logger import BatchLogger
from chromeis_sync.migration_audit.batch_models import (
    BatchDetail,
    BatchResult,
)
from chromeis_sync.migration_audit.snapshot import SnapshotService
from chromeis_sync.migration_audit.transaction import InvoiceTransaction


class InvoiceBatchRunner:

    def __init__(
        self,
        invoices,
        target_currency=None,
        batch_size=None,
        continue_on_error=True,
    ):
        self.invoices = list(invoices)

        if batch_size:
            self.invoices = self.invoices[:batch_size]

        self.target_currency = target_currency
        self.continue_on_error = continue_on_error

        self.logger = BatchLogger()

    def run(self):

        result = BatchResult(
            started_at=datetime.now()
        )

        total = len(self.invoices)

        for index, invoice_name in enumerate(self.invoices, start=1):

            self.logger.separator()
            self.logger.info(
                f"[{index}/{total}] {invoice_name}"
            )

            # Skip invoices that are already cancelled/draft
            docstatus = frappe.db.get_value(
                "Sales Invoice",
                invoice_name,
                "docstatus",
            )

            if docstatus != 1:

                detail = BatchDetail(
                    invoice_name=invoice_name,
                    whmcs_invoice_id=None,
                    status="SKIPPED",
                    message=f"Invoice docstatus={docstatus}. Already repaired or not submitted.",
                )

                result.add(detail)

                self.logger.warning(
                    f"{invoice_name} skipped (docstatus={docstatus})"
                )

                continue

            # Capture snapshot for reporting
            snapshot = SnapshotService.create(invoice_name)
            whmcs_invoice_id = snapshot["header"].get("whmcs_invoice_id")

            start = time.perf_counter()

            try:

                currency = self.target_currency

                if currency is None:
                    currency = frappe.db.get_value(
                        "Sales Invoice",
                        invoice_name,
                        "currency",
                    )

                tx = InvoiceTransaction(
                    invoice_name,
                    currency,
                )

                tx_result = tx.execute()

                duration = time.perf_counter() - start

                detail = BatchDetail(
                    invoice_name=invoice_name,
                    whmcs_invoice_id=whmcs_invoice_id,
                    status="PASS",
                    new_invoice=tx_result.new_invoice,
                    message=tx_result.message,
                    duration=duration,
                )

                result.add(detail)

                self.logger.success(
                    f"{invoice_name} -> {tx_result.new_invoice} ({duration:.2f}s)"
                )

            except Exception as exc:

                duration = time.perf_counter() - start

                detail = BatchDetail(
                    invoice_name=invoice_name,
                    whmcs_invoice_id=whmcs_invoice_id,
                    status="FAIL",
                    message=str(exc),
                    duration=duration,
                )

                result.add(detail)

                self.logger.error(
                    f"{invoice_name} ({duration:.2f}s)"
                )

                self.logger.error(str(exc))

                if not self.continue_on_error:
                    break

        result.finished_at = datetime.now()

        self.logger.summary(result)

        return result
