"""Domain exceptions for the chat application"""

from typing import Optional


class DomainException(Exception):
    """Base exception for domain layer"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIProviderException(DomainException):
    """Base exception for API provider related errors"""
    pass


class ProviderNotAvailable(APIProviderException):
    """Raised when an API provider is not available"""
    pass


class ProviderRateLimitExceeded(APIProviderException):
    """Raised when API provider rate limit is exceeded"""
    pass


class ProviderAuthenticationError(APIProviderException):
    """Raised when API provider authentication fails"""
    pass


class ProviderQuotaExceeded(APIProviderException):
    """Raised when API provider quota is exceeded"""
    pass


class ChatException(DomainException):
    """Base exception for chat related errors"""
    pass


class SessionNotFound(ChatException):
    """Raised when a chat session is not found"""
    pass


class MessageNotFound(ChatException):
    """Raised when a chat message is not found"""
    pass


class InvalidSessionId(ChatException):
    """Raised when session ID is invalid"""
    pass


class MessageValidationError(ChatException):
    """Raised when message validation fails"""
    pass


class UsageException(DomainException):
    """Base exception for usage tracking related errors"""
    pass


class UsageLimitExceeded(UsageException):
    """Raised when usage limit is exceeded"""
    pass


class InvalidUsageData(UsageException):
    """Raised when usage data is invalid"""
    pass


class RepositoryException(DomainException):
    """Base exception for repository related errors"""
    pass


class DatabaseConnectionError(RepositoryException):
    """Raised when database connection fails"""
    pass


class DataIntegrityError(RepositoryException):
    """Raised when data integrity is violated"""
    pass


class ValidationException(DomainException):
    """Base exception for validation related errors"""
    pass


class InvalidRequestData(ValidationException):
    """Raised when request data is invalid"""
    pass


class MissingRequiredField(ValidationException):
    """Raised when a required field is missing"""
    pass


class ConfigurationException(DomainException):
    """Base exception for configuration related errors"""
    pass


class InvalidConfiguration(ConfigurationException):
    """Raised when configuration is invalid"""
    pass


class ExternalServiceException(DomainException):
    """Base exception for external service related errors"""
    pass


class ServiceUnavailable(ExternalServiceException):
    """Raised when external service is unavailable"""
    pass


class ServiceTimeout(ExternalServiceException):
    """Raised when external service times out"""
    pass


class BusinessLogicException(DomainException):
    """Base exception for business logic related errors"""
    pass


class OperationNotAllowed(BusinessLogicException):
    """Raised when an operation is not allowed"""
    pass


class ResourceConflict(BusinessLogicException):
    """Raised when there is a resource conflict"""
    pass
