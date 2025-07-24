class ServiceException(Exception):
    """Base exception for all service errors."""
    pass

class ExternalAPIException(ServiceException):
    """Exception raised when an external API call fails."""
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

class InvalidRequestException(ServiceException):
    """Exception raised for invalid requests to a service."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors

class NotFoundException(ServiceException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, message):
        super().__init__(message)
