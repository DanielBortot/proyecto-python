from enum import Enum

class BaseExceptionEnum(Enum):
    DOMAIN_EXCEPTION = "DOMAIN_EXCEPTION"
    APPLICATION_EXCEPTION = "APPLICATION_EXCEPTION"
    INFRASTRUCTURE_EXCEPTION = "INFRASTRUCTURE_EXCEPTION"
    NOT_REGISTERED = "NOT_REGISTERED"