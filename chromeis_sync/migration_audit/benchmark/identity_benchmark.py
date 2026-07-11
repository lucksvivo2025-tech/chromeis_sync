from __future__ import annotations

from chromeis_sync.migration_audit.benchmark.benchmark_result import (
    BenchmarkResult,
)

from chromeis_sync.migration_audit.domain.normalizers.identity_extractor import (
    IdentityExtractor,
)


class IdentityBenchmark:
    """
    Executes the IdentityExtractor
    against invoice descriptions.
    """

    def __init__(self):

        self.extractor = IdentityExtractor()

    def run(
        self,
        invoice_id: int,
        description: str,
    ) -> BenchmarkResult:

        identity = self.extractor.extract(description)

        return BenchmarkResult(
            invoice_id=invoice_id,
            description=description,
            identity=identity,
            success=True,
        )
