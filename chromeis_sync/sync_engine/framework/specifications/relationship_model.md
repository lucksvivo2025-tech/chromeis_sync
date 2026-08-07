# Chromeis Sync Engine
# WHMCS Relationship Model
Version: 1.0
Status: Investigation (Verified)

---

# Purpose

This document defines the canonical relationship model between WHMCS entities.
It is the blueprint for the Relationship Framework.

Only VERIFIED relationships are documented here.

---

# Invoice

WHMCS Table

tblinvoices

Primary Key

id

Relationships

Invoice
    ├── Invoice Items

---

# Invoice Item

WHMCS Table

tblinvoiceitems

Relationships

Invoice Item
    ├── Hosting
    ├── Domain
    ├── Addon
    ├── Upgrade
    ├── Config Option
    ├── Credit
    └── Other

Relationship Key

type

Examples

Hosting

relid -> tblhosting.id

Domain

relid -> tbldomains.id

Addon

relid -> tblhostingaddons.id

---

# Hosting Service

WHMCS Table

tblhosting

Verified Relationships

Hosting
    ├── Customer
    ├── Product
    ├── Server
    └── Domain Name

Relationship Fields

userid
packageid
server
domain

Verified Example

Invoice
    id = 8402

Invoice Item
    type = Hosting
    relid = 110

Hosting

id = 110
userid = 109
packageid = 20
server = 19
domain = innomei.com

Product

id = 20
name = Advance/ cPanel

---

# Domain

WHMCS Table

tbldomains

Verified Relationship

Invoice Item

type = Domain

relid -> tbldomains.id

Verified Example

Invoice
    id = 8402

Invoice Item

type = Domain
relid = 26

---

# Product

WHMCS Table

tblproducts

Relationships

Product
    ├── Product Group

Relationship Field

gid

Verified Example

Product

id = 20

gid = 2

---

# Product Group

WHMCS Table

tblproductgroups

---

# Server

WHMCS Table

tblservers

Relationship

Hosting.server -> tblservers.id

Important

Invoice Items NEVER point directly to tblservers.

Hosting is the bridge.

Invoice Item
    ↓
Hosting
    ↓
Server

---

# ERP Observations

Hosting Service invoice lines contain

custom_whmcs_product_id

Domain Registration invoice lines do NOT contain

custom_whmcs_product_id

This is expected because domains are represented by tbldomains,
not tblproducts.

---

# Verified Business Rules

BR-001

Invoice Item (Hosting)

relid always references tblhosting.id

BR-002

Invoice Item (Domain)

relid always references tbldomains.id

BR-003

Hosting links to Product using packageid.

BR-004

Hosting links to Server using server.

BR-005

Hosting links to Customer using userid.

BR-006

Domain Registration ERP Items are generic accounting items.
They are not WHMCS Products.
