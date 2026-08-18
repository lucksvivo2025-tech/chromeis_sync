import frappe

from chromeis_sync.level5.validators.payment_verifier import PaymentVerifier


class PaymentVerificationRunner:

    @staticmethod
    def run(payment_names=None):

        if payment_names is None:
            payment_names = frappe.db.sql("""
                SELECT name
                FROM `tabPayment Entry`
                WHERE docstatus IN (1, 2)
                ORDER BY name
            """, pluck="name")

        results = []

        for payment_name in payment_names:

            try:
                result = PaymentVerifier.verify(payment_name)

                results.append(result)

            except Exception as exc:

                results.append({
                    "erp_id": payment_name,
                    "status": "VERIFIED_WITH_EXCEPTION",
                    "differences": [str(exc)],
                })

        return results
