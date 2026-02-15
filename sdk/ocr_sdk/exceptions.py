"""Custom exceptions for OCR SDK."""


class OCRSDKError(Exception):
    """Base exception for OCR SDK."""

    pass


class OCRAPIError(OCRSDKError):
    """Exception raised when API returns an error."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error {status_code}: {message}")


class OCRTimeoutError(OCRSDKError):
    """Exception raised when a request times out."""

    pass


class OCRAuthenticationError(OCRSDKError):
    """Exception raised when authentication fails."""

    pass


class OCRValidationError(OCRSDKError):
    """Exception raised when validation fails."""

    pass
