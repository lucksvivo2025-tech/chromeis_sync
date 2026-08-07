import traceback

import frappe


class InvoiceInserter:

    @staticmethod
    def insert(invoice):

        print("=" * 60)
        print("BEFORE INSERT")
        print("POSTING :", invoice.posting_date)
        print("DUE     :", invoice.due_date)
        print("=" * 60)

        try:

            invoice.insert(
                ignore_permissions=True,
            )

            return invoice

        except Exception:

            print("=" * 60)
            print("AFTER FAILURE")
            print("POSTING :", invoice.posting_date)
            print("DUE     :", invoice.due_date)
            print("=" * 60)

            traceback.print_exc()

            raise
