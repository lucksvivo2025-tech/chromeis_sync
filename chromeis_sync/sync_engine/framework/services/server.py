from chromeis_sync.sync_engine.framework.builders.server import (
    ServerBuilder,
)

from chromeis_sync.sync_engine.framework.identity.service import (
    IdentityService,
)

from chromeis_sync.sync_engine.framework.services.server_persistence import (
    ServerPersistence,
)

from chromeis_sync.sync_engine.framework.whmcs.client import (
    WHMCSClient,
)


class ServerService:

    @classmethod
    def synchronize(cls, server_id):

        #
        # Step 1
        # Fetch WHMCS row
        #
        row = WHMCSClient.get_row(
            "tblservers",
            server_id,
        )

        if not row:
            return {
                "status": "NOT_FOUND",
                "document": None,
            }

        #
        # Step 2
        # Identity lookup
        #
        identity = IdentityService.resolve_server(server_id)

        #
        # Step 3
        # Build ERP payload
        #
        payload = ServerBuilder(row).build()

        #
        # Step 4
        # Update existing Server
        #
        if identity.found:
            doc = ServerPersistence.update(
                identity.document_name,
                payload,
            )

            return {
                "status": "UPDATED",
                "document": doc.name,
            }

        #
        # Step 5
        # Create new Server
        #
        doc = ServerPersistence.create(payload)

        return {
            "status": "CREATED",
            "document": doc.name,
        }
