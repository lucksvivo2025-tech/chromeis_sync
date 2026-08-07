from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RelationshipResult:
    """
    Represents a fully resolved ERP relationship graph.

    Example:
        Invoice
            ├── Customer
            ├── Invoice Items
            ├── Payments
            ├── Credits
            └── Metadata
    """

    root_type: str
    root_document: Optional[str] = None

    customer: Optional[Any] = None

    invoice_items: List[Any] = field(default_factory=list)

    products: List[Any] = field(default_factory=list)

    groups: List[Any] = field(default_factory=list)

    services: List[Any] = field(default_factory=list)

    domains: List[Any] = field(default_factory=list)

    addons: List[Any] = field(default_factory=list)

    payments: List[Any] = field(default_factory=list)

    credits: List[Any] = field(default_factory=list)

    servers: List[Any] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    warnings: List[str] = field(default_factory=list)

    errors: List[str] = field(default_factory=list)

    @property
    def valid(self):
        return len(self.errors) == 0
