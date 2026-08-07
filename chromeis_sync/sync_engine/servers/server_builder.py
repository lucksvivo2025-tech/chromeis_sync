import frappe


class ServerBuilder:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def _provider(self):
        noc = (self.snapshot.get("noc") or "").strip().lower()

        mapping = {
            "hetzner": "Hetzner",
            "aws": "AWS",
            "digitalocean": "DigitalOcean",
            "cloudcone": "Other",
            "contabo": "Other",
            "imola": "Other",
        }

        return mapping.get(noc, "Other")

    def build(self):

        server = frappe.new_doc("Server")

        server.name = self.snapshot["name"][:140]
        server.server_name = self.snapshot["name"][:140]
        server.ip_address = (self.snapshot.get("ipaddress") or "")[:140]
        server.whmcs_id = str(self.snapshot["id"])
        server.provider = self._provider()

        return server
