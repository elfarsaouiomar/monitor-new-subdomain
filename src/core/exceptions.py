class SubdomainMonitorException(Exception):
    """Base exception for the application"""

    pass


class DomainNotFoundException(SubdomainMonitorException):
    """Raised when domain is not found"""

    pass


class DomainAlreadyExistsException(SubdomainMonitorException):
    """Raised when trying to add existing domain"""

    pass


class DNSResolutionException(SubdomainMonitorException):
    """Raised when DNS resolution fails"""

    pass


class DatabaseException(SubdomainMonitorException):
    """Raised when database operation fails"""

    pass
