from chromeis_sync.sync_engine.framework.services.base import (
    BaseService,
)

from chromeis_sync.sync_engine.framework.identity.service import (
    IdentityService,
)

from chromeis_sync.sync_engine.framework.whmcs.client import (
    WHMCSClient,
)

from chromeis_sync.sync_engine.framework.builders.customer import (
    CustomerBuilder,
)

from chromeis_sync.sync_engine.framework.services.customer_persistence import (
    CustomerPersistence,
)


class CustomerService(BaseService):
    """
    End-to-end Customer synchronization.
    """

    @classmethod
    def synchronize(cls, customer_id):

        #
        # Step 1
        # Identity lookup
        #

        identity = IdentityService.resolve_customer(customer_id)

        #
        # Step 2
        # Load WHMCS customer
        #

        row = WHMCSClient.get_row(
            "tblclients",
            customer_id,
        )

        if row is None:

            return {
                "status": "WHMCS_NOT_FOUND",
                "identifier": str(customer_id),
            }

        #
        # Step 3
        # Build ERP payload
        #

        payload = CustomerBuilder(row).build()

        #
        # Step 4
        # Update existing customer
        #

        if identity.found:

            doc = CustomerPersistence.update(
                identity.document_name,
                payload,
            )

            return {
                "status": "UPDATED",
                "document": doc.name,
            }

        #
        # Step 5
        # Create new customer
        #

        doc = CustomerPersistence.create(
            payload,
        )

        return {
            "status": "CREATED",
            "document": doc.name,
        }
