from chromeis_sync.sync_engine.framework.identity.entities.customer import (
    ENTITY as CUSTOMER,
)
from chromeis_sync.sync_engine.framework.identity.entities.invoice import (
    ENTITY as INVOICE,
)
from chromeis_sync.sync_engine.framework.identity.entities.service import (
    ENTITY as SERVICE,
)
from chromeis_sync.sync_engine.framework.identity.entities.domain import (
    ENTITY as DOMAIN,
)
from chromeis_sync.sync_engine.framework.identity.entities.product import (
    ENTITY as PRODUCT,
)
from chromeis_sync.sync_engine.framework.identity.entities.addon import (
    ENTITY as ADDON,
)
from chromeis_sync.sync_engine.framework.identity.entities.order import (
    ENTITY as ORDER,
)
from chromeis_sync.sync_engine.framework.identity.entities.payment import (
    ENTITY as PAYMENT,
)
from chromeis_sync.sync_engine.framework.identity.entities.promotion import (
    ENTITY as PROMOTION,
)
from chromeis_sync.sync_engine.framework.identity.entities.server import (
    ENTITY as SERVER,
)

ENTITY_REGISTRY = {
    "customer": CUSTOMER,
    "invoice": INVOICE,
    "service": SERVICE,
    "domain": DOMAIN,
    "product": PRODUCT,
    "addon": ADDON,
    "order": ORDER,
    "payment": PAYMENT,
    "promotion": PROMOTION,
    "server": SERVER,
}


def get_entity(name):
    key = str(name).lower()

    if key not in ENTITY_REGISTRY:
        raise KeyError(f"Unknown entity: {name}")

    return ENTITY_REGISTRY[key]


def list_entities():
    return sorted(ENTITY_REGISTRY.keys())
