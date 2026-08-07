import frappe


class OrderPersistence:

    @staticmethod
    def create(payload):
        doc = frappe.get_doc(payload)
        doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return doc

    @staticmethod
    def update(document_name, payload):
        doc = frappe.get_doc("Sales Order", document_name)

        for field, value in payload["data"].items():
            setattr(doc, field, value)

        doc.save(ignore_permissions=True)

        frappe.db.commit()

        return doc
