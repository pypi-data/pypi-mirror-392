"""DayBetter client exceptions."""


class DayBetterError(Exception):
    """Base exception for DayBetter client."""
    
    def __init__(self, message: str) -> None:
        """Initialize the exception.
        
        Args:
            message: Error message
        """
        super().__init__(message)
        self.message = message


class AuthenticationError(DayBetterError):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize the authentication error.
        
        Args:
            message: Error message
        """
        super().__init__(message)


class APIError(DayBetterError):
    """API request failed."""
    
    def __init__(self, message: str) -> None:
        """Initialize the API error.
        
        Args:
            message: Error message
        """
        super().__init__(message)
