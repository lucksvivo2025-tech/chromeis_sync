from chromeis_sync.migration_audit.infrastructure.providers.whmcs_provider import (
    WHMCSProvider,
)

from chromeis_sync.migration_audit.domain.normalizers.identity_extractor import (
    IdentityExtractor,
)


provider = WHMCSProvider()
extractor = IdentityExtractor()

invoice = provider.load_invoice(627)

print(f"Invoice: {invoice.header.invoice_id}")
print()

for item in invoice.items:
    identity = extractor.extract(item.description)

    print("-" * 60)
    print("Description :", item.description)
    print("Identity    :", identity)
