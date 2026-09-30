from dataclasses import dataclass, field


@dataclass
class CertificationResult:
    """
    Final Level 5 accounting certification result.

    This model does not perform validation or repair.
    It records the final certification decision produced
    from identity, evidence, validation, and classification.
    """

    entity_type: str
    erp_id: str
    whmcs_id: str

    # CERTIFIED | PENDING_EXCEPTION | NOT_CERTIFIED
    certification_status: str = "NOT_CERTIFIED"

    # Identity result
    identity_classification: str = ""

    # Validation result
    verification_result: str = "NOT_VERIFIED"

    # Accounting difference classification
    reconciliation_classification: str = ""

    # Whether all evidence required for certification was available
    evidence_complete: bool = False

    # Exact findings
    differences: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    # Human-readable certification reasoning
    reasons: list = field(default_factory=list)

    # Evidence reference/snapshot
    evidence_snapshot: dict = field(default_factory=dict)
