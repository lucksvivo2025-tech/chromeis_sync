# Invoice Item Identity Recovery Specification

## Recoverable Types

| Type | ERP Field | Status |
|------|-----------|--------|
| Hosting | custom_whmcs_service_id | Supported |
| Domain | custom_whmcs_domain_id | Supported |
| Addon | custom_whmcs_addon_id | Supported |

## Conditional Types

| Type | Action |
|------|--------|
| PromoHosting | Recover using same Service ID |
| PromoDomain | Recover using same Domain ID |

## Legacy Types

type=''
relid=0

These invoice items have no WHMCS object identity.
No recovery should be attempted.

## Accounting Types

LateFee
AddFunds
Invoice
GroupDiscount

These do not represent service/domain identities.

## Investigation Required

Upgrade
Setup
Item
DomainRegister
DomainTransfer
DomainRedemptionFee
DomainAddonDNS
DomainAddonEMF
