from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BaseEntity:

    #
    # Friendly name
    #

    name: str

    #
    # WHMCS table
    #

    whmcs_table: str

    #
    # ERPNext DocType
    #

    erp_doctype: str

    #
    # ERP identity field
    #

    identity_field: str

    #
    # Repository class
    #

    repository: object

    #
    # Optional matching fields
    #

    match_fields: List[str] = field(default_factory=list)

    #
    # Parent entity dependencies
    #

    depends_on: List[str] = field(default_factory=list)

    #
    # WHMCS relationship mapping
    #
    # Example:
    # {
    #     "customer": "userid",
    #     "product": "packageid",
    #     "server": "server",
    # }
    #

    relationship_fields: Dict[str, str] = field(default_factory=dict)

    #
    # Optional description
    #

    description: str = ""
