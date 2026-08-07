import frappe

from chromeis_sync.sync_engine.servers.server_snapshot import ServerSnapshot
from chromeis_sync.sync_engine.servers.server_builder import ServerBuilder


class ServerTransaction:

    def __init__(self, server_id):
        self.server_id = server_id

    def execute(self):

        snapshot = ServerSnapshot.create(self.server_id)

        if not snapshot:
            return None

        existing = frappe.db.get_value(
            "Server",
            {
                "whmcs_id": str(self.server_id)
            },
            "name",
        )

        if existing:
            return frappe.get_doc("Server", existing)

        server = ServerBuilder(snapshot).build()

        server.insert(ignore_permissions=True)

        frappe.db.commit()

        return server
