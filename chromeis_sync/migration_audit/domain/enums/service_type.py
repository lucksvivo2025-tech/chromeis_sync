from enum import Enum


class ServiceType(str, Enum):
    HOSTING = "HOSTING"
    DOMAIN = "DOMAIN"
    VPS = "VPS"
    DEDICATED = "DEDICATED"
    SSL = "SSL"
    EMAIL = "EMAIL"
    LICENSE = "LICENSE"
    ADDON = "ADDON"
    UNKNOWN = "UNKNOWN"
