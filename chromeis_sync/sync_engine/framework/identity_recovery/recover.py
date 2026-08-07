import frappe

from chromeis_sync.sync_engine.framework.identity_recovery.validator import (
    IdentityRecoveryValidator,
)


class IdentityRecovery:

    @staticmethod
    def invoice(invoice_id, commit=False):

        validation = IdentityRecoveryValidator.invoice(invoice_id)

        if not validation["valid"]:
            return {
                "success": False,
                "invoice": invoice_id,
                "status": validation.get("status"),
                "reason": "Invoice is not fully recoverable",
                "validation": validation,
            }

        updated = []

        for match in validation["matches"]:

            #
            # Never write fake WHMCS identities.
            # relid must be a real WHMCS object id.
            #

            if int(match.get("relid") or 0) <= 0:
                continue

            row = frappe.get_doc(
                "Sales Invoice Item",
                match["erp_row"],
            )

            if match["type"] == "Hosting":

                row.custom_whmcs_service_id = str(
                    match["relid"]
                )

            elif match["type"] == "Domain":

                row.custom_whmcs_domain_id = str(
                    match["relid"]
                )

            elif match["type"] == "Addon":

                row.custom_whmcs_addon_id = str(
                    match["relid"]
                )

            else:
                continue

            row.db_update()

            updated.append(
                {
                    "row": row.name,
                    "type": match["type"],
                    "original_type": match["original_type"],
                    "whmcs_id": match["relid"],
                    "invoice_item_id": match["whmcs_invoice_item_id"],
                }
            )

        if commit:
            frappe.db.commit()

        return {
            "success": True,
            "invoice": invoice_id,
            "status": validation["status"],
            "updated": updated,
            "updated_count": len(updated),
            "supported_items": validation["supported_items"],
            "matched_items": validation["matched_items"],
            "unsupported_items": validation["unsupported_items"],
        }
