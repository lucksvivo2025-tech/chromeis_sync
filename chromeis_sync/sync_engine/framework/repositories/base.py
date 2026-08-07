import frappe

from chromeis_sync.sync_engine.framework.models.identity_result import IdentityResult
from chromeis_sync.sync_engine.framework.models.status import SyncStatus


class BaseRepository:
    """
    Base Repository

    Every ERP Repository inherits from this class.

    Responsibilities
    ----------------
    • Lookup ERP records
    • Return IdentityResult
    • Never raise exceptions for missing records
    • Provide reusable lookup methods
    """

    doctype = None
    whmcs_field = None
    default_fields = ["name"]

    @classmethod
    def _build_result(cls, doc, whmcs_id, reason="Matched"):
        """Create a consistent IdentityResult."""

        if not doc:
            return IdentityResult(
                status=SyncStatus.MISSING,
                doctype=cls.doctype,
                whmcs_id=str(whmcs_id) if whmcs_id is not None else None,
                reason=f"{cls.doctype} not found",
            )

        return IdentityResult(
            status=SyncStatus.MATCHED,
            doctype=cls.doctype,
            document_name=doc["name"],
            erp_id=doc["name"],
            whmcs_id=str(whmcs_id) if whmcs_id is not None else None,
            data=doc,
            reason=reason,
        )

    @classmethod
    def find(cls, whmcs_id, fields=None):
        """Lookup using the repository's primary WHMCS field."""

        if not whmcs_id:
            return IdentityResult(
                status=SyncStatus.MISSING,
                doctype=cls.doctype,
                whmcs_id=None,
                reason="WHMCS identifier missing",
            )

        return cls.find_by_field(
            cls.whmcs_field,
            whmcs_id,
            fields=fields,
        )

    @classmethod
    def find_by_field(cls, field_name, value, fields=None):
        """Generic lookup by any ERP field."""

        if not value:
            return IdentityResult(
                status=SyncStatus.MISSING,
                doctype=cls.doctype,
                whmcs_id=None,
                reason=f"{field_name} missing",
            )

        if fields is None:
            fields = cls.default_fields

        doc = frappe.db.get_value(
            cls.doctype,
            {field_name: str(value)},
            fields,
            as_dict=True,
        )

        return cls._build_result(
            doc,
            value,
            reason=f"Matched using {field_name}",
        )

    @classmethod
    def exists(cls, whmcs_id):
        return cls.find(whmcs_id).found

    @classmethod
    def get_document(cls, document_name):
        """Return the complete ERP document."""

        if not document_name:
            return None

        return frappe.get_doc(
            cls.doctype,
            document_name,
        )
