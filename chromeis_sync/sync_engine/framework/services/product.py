from chromeis_sync.sync_engine.framework.services.base import (
    BaseService,
)

from chromeis_sync.sync_engine.framework.identity.service import (
    IdentityService,
)

from chromeis_sync.sync_engine.framework.whmcs.client import (
    WHMCSClient,
)

from chromeis_sync.sync_engine.framework.builders.product import (
    ProductBuilder,
)

from chromeis_sync.sync_engine.framework.services.product_persistence import (
    ProductPersistence,
)


class ProductService(BaseService):
    """
    End-to-end Product synchronization.
    """

    @classmethod
    def synchronize(cls, product_id):

        #
        # Step 1
        # Identity lookup
        #

        identity = IdentityService.resolve_product(product_id)

        #
        # Step 2
        # Load WHMCS Product
        #

        row = WHMCSClient.get_row(
            "tblproducts",
            product_id,
        )

        if row is None:
            return {
                "status": "WHMCS_NOT_FOUND",
                "identifier": str(product_id),
            }

        #
        # Step 3
        # Build ERP payload
        #

        payload = ProductBuilder(row).build()

        #
        # Step 4
        # Update existing Item
        #

        if identity.found:

            doc = ProductPersistence.update(
                identity.document_name,
                payload,
            )

            return {
                "status": "UPDATED",
                "document": doc.name,
            }

        #
        # Step 5
        # Create new Item
        #

        doc = ProductPersistence.create(payload)

        return {
            "status": "CREATED",
            "document": doc.name,
        }
