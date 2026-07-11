import time
from datetime import datetime

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
        target_currency,
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

            # Capture snapshot for reporting
            snapshot = SnapshotService.create(invoice_name)
            whmcs_invoice_id = snapshot["header"].get("whmcs_invoice_id")

            start = time.perf_counter()

            try:

                tx = InvoiceTransaction(
                    invoice_name,
                    self.target_currency,
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
                    f"{invoice_name} -> {tx_result.new_invoice} "
                    f"({duration:.2f}s)"
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
