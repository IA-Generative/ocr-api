/**
 * Custom exceptions for OCR SDK.
 */

/**
 * Base exception for OCR SDK.
 */
export class OCRSDKError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OCRSDKError";
    Object.setPrototypeOf(this, OCRSDKError.prototype);
  }
}

/**
 * Exception raised when API returns an error.
 */
export class OCRAPIError extends OCRSDKError {
  public statusCode: number;
  public responseMessage: string;

  constructor(statusCode: number, message: string) {
    super(`API error ${statusCode}: ${message}`);
    this.name = "OCRAPIError";
    this.statusCode = statusCode;
    this.responseMessage = message;
    Object.setPrototypeOf(this, OCRAPIError.prototype);
  }
}

/**
 * Exception raised when a request times out.
 */
export class OCRTimeoutError extends OCRSDKError {
  constructor(message: string) {
    super(message);
    this.name = "OCRTimeoutError";
    Object.setPrototypeOf(this, OCRTimeoutError.prototype);
  }
}

/**
 * Exception raised when authentication fails.
 */
export class OCRAuthenticationError extends OCRSDKError {
  constructor(message: string) {
    super(message);
    this.name = "OCRAuthenticationError";
    Object.setPrototypeOf(this, OCRAuthenticationError.prototype);
  }
}

/**
 * Exception raised when validation fails.
 */
export class OCRValidationError extends OCRSDKError {
  constructor(message: string) {
    super(message);
    this.name = "OCRValidationError";
    Object.setPrototypeOf(this, OCRValidationError.prototype);
  }
}
