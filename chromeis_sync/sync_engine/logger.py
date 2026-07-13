import frappe
from datetime import datetime


class SyncLogger:
    """
    Centralized logger for the Sync Engine.
    """

    @staticmethod
    def info(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] {timestamp} | {message}")

    @staticmethod
    def warning(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] {timestamp} | {message}")

    @staticmethod
    def error(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] {timestamp} | {message}")

        frappe.log_error(
            title="WHMCS Sync Engine",
            message=message,
        )

    @staticmethod
    def separator():
        print("=" * 70)
