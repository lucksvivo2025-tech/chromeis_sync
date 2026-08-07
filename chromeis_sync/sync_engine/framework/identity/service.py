from chromeis_sync.sync_engine.framework.repositories.order import (
    OrderRepository,
)

from chromeis_sync.sync_engine.framework.repositories.customer import (
    CustomerRepository,
)

from chromeis_sync.sync_engine.framework.repositories.invoice import (
    InvoiceRepository,
)

from chromeis_sync.sync_engine.framework.repositories.product import (
    ProductRepository,
)

from chromeis_sync.sync_engine.framework.repositories.group import (
    GroupRepository,
)

from chromeis_sync.sync_engine.framework.repositories.payment import (
    PaymentRepository,
)

from chromeis_sync.sync_engine.framework.repositories.credit import (
    CreditRepository,
)

from chromeis_sync.sync_engine.framework.repositories.server import (
    ServerRepository,
)

from chromeis_sync.sync_engine.framework.repositories.service import (
    ServiceRepository,
)

from chromeis_sync.sync_engine.framework.repositories.domain import (
    DomainRepository,
)

from chromeis_sync.sync_engine.framework.repositories.addon import (
    AddonRepository,
)

from chromeis_sync.sync_engine.framework.repositories.invoice_item import (
    InvoiceItemRepository,
)

from chromeis_sync.sync_engine.framework.repositories.promotion import (
    PromotionRepository,
)


class IdentityService:

    @staticmethod
    def resolve_customer(user_id=None, client_id=None):
        if user_id:
            return CustomerRepository.find_by_whmcs_user_id(user_id)

        return CustomerRepository.find_by_whmcs_client_id(client_id)

    @staticmethod
    def resolve_invoice(invoice_id):
        return InvoiceRepository.find_by_whmcs_invoice_id(invoice_id)

    @staticmethod
    def resolve_product(product_id):
        return ProductRepository.find_by_whmcs_product_id(product_id)

    @staticmethod
    def resolve_group(group_id):
        return GroupRepository.find_by_whmcs_group_id(group_id)

    @staticmethod
    def resolve_payment(txn_id):
        return PaymentRepository.find_by_whmcs_txn_id(txn_id)

    @staticmethod
    def resolve_credit(credit_id):
        return CreditRepository.find_by_whmcs_credit_id(credit_id)

    @staticmethod
    def resolve_server(server_id):
        return ServerRepository.find_by_whmcs_server_id(server_id)

    @staticmethod
    def resolve_service(service_id):
        return ServiceRepository.find_by_whmcs_service_id(service_id)

    @staticmethod
    def resolve_domain(domain_id):
        return DomainRepository.find_by_whmcs_domain_id(domain_id)

    @staticmethod
    def resolve_addon(addon_id):
        return AddonRepository.find_by_whmcs_addon_id(addon_id)

    @staticmethod
    def resolve_invoice_item(service_id):
        return InvoiceItemRepository.find_by_whmcs_service_id(service_id)

    @staticmethod
    def resolve_order(order_id):
        return OrderRepository.find_by_whmcs_order_id(order_id)

    @staticmethod
    def resolve_promotion(promo_code):
        return PromotionRepository.find_by_whmcs_promo_code(promo_code)
