import frappe


class SyncConfig:
    """
    Central configuration for the WHMCS Sync Engine.
    """

    # ------------------------------------------------------------------
    # Company
    # ------------------------------------------------------------------

    COMPANY = "Chromeis Pvt Ltd"

    # ------------------------------------------------------------------
    # Sync Behaviour
    # ------------------------------------------------------------------

    BATCH_SIZE = 100

    MAX_RETRIES = 3

    ENABLE_CUSTOMER_SYNC = True
    ENABLE_SERVICE_SYNC = True
    ENABLE_INVOICE_SYNC = True
    ENABLE_PAYMENT_SYNC = True

    # ------------------------------------------------------------------
    # Scheduler
    # ------------------------------------------------------------------

    SYNC_INTERVAL_MINUTES = 5

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    LOG_LEVEL = "INFO"

    # ------------------------------------------------------------------
    # WHMCS API
    # ------------------------------------------------------------------

    @staticmethod
    def api_url():
        return frappe.conf.get("whmcs_api_url")

    @staticmethod
    def api_identifier():
        return frappe.conf.get("whmcs_api_identifier")

    @staticmethod
    def api_secret():
        return frappe.conf.get("whmcs_api_secret")

    @staticmethod
    def verify_ssl():
        return frappe.conf.get("whmcs_verify_ssl", True)
