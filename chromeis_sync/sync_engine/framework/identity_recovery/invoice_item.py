import frappe


class InvoiceItemIdentityReport:

    @staticmethod
    def run():

        whmcs_total = frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM whmcs_mirror.tblinvoiceitems
            """
        )[0][0]

        erp_total = frappe.db.count("Sales Invoice Item")

        hosting = frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM `tabSales Invoice Item`
            WHERE IFNULL(custom_whmcs_service_id,'')!=''
            """
        )[0][0]

        domains = frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM `tabSales Invoice Item`
            WHERE IFNULL(custom_whmcs_domain_id,'')!=''
            """
        )[0][0]

        addons = frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM `tabSales Invoice Item`
            WHERE IFNULL(custom_whmcs_addon_id,'')!=''
            """
        )[0][0]

        configs = frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM `tabSales Invoice Item`
            WHERE IFNULL(custom_whmcs_config_id,'')!=''
            """
        )[0][0]

        return {
            "entity": "Invoice Item",
            "whmcs_total": whmcs_total,
            "erp_total": erp_total,
            "service_ids": hosting,
            "domain_ids": domains,
            "addon_ids": addons,
            "config_ids": configs,
        }
