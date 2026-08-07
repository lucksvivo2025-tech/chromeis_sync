import frappe

from chromeis_sync.sync_engine.framework.upsert.base import (
    BaseUpsert,
)


class UpsertEngine(BaseUpsert):
    """
    Generic ERPNext Upsert Engine.

    The builder must return:

        {
            "doctype": "...",
            "data": {...}
        }
    """

    @classmethod
    def create(cls, identity_result, builder):

        payload = builder.build()

        doc = frappe.get_doc(payload)

        doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return cls.success(
            action="created",
            doctype=doc.doctype,
            document_name=doc.name,
            message="Document created",
        )

    @classmethod
    def update(cls, identity_result, builder):

        payload = builder.build()

        doc = frappe.get_doc(
            payload["doctype"],
            identity_result.document_name,
        )

        for field, value in payload["data"].items():
            setattr(doc, field, value)

        doc.save(ignore_permissions=True)

        frappe.db.commit()

        return cls.success(
            action="updated",
            doctype=doc.doctype,
            document_name=doc.name,
            message="Document updated",
        )

