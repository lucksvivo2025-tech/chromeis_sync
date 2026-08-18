from chromeis_sync.whmcs_sync import WHMCSClient


class Level5WHMCSClient:
    """
    Read-only WHMCS API client for Level 5 verification.

    WHMCS remains authoritative.
    This client never writes to WHMCS.
    """

    def __init__(self):
        self.client = WHMCSClient()

    def get_invoice(self, invoice_id):
        data = self.client.request(
            "GetInvoice",
            invoiceid=str(invoice_id),
        )

        return data

    def get_client(self, client_id):
        data = self.client.request(
            "GetClientsDetails",
            clientid=str(client_id),
        )

        return data

    def get_transaction(self, transaction_id):
        data = self.client.request(
            "GetTransactions",
            transid=str(transaction_id),
        )

        return data

    def get_products(self, product_id=None):
        kwargs = {}

        if product_id is not None:
            kwargs["pid"] = str(product_id)

        data = self.client.request(
            "GetProducts",
            **kwargs,
        )

        return data.get("products", {})

    def get_orders(self, order_id=None):
        kwargs = {}

        if order_id is not None:
            kwargs["id"] = str(order_id)

        data = self.client.request(
            "GetOrders",
            **kwargs,
        )

        return data.get("orders", {})

    def get_services(self, service_id=None):
        kwargs = {}

        if service_id is not None:
            kwargs["serviceid"] = str(service_id)

        data = self.client.request(
            "GetClientsProducts",
            **kwargs,
        )

        return data.get("products", {})

    def get_domains(self, domain_id=None):
        kwargs = {}

        if domain_id is not None:
            kwargs["domainid"] = str(domain_id)

        data = self.client.request(
            "GetClientsDomains",
            **kwargs,
        )

        return data.get("domains", {})

    def get_credits(self, client_id):
        data = self.client.request(
            "GetCredits",
            clientid=str(client_id),
        )

        return data
