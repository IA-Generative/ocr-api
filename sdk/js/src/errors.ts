export class OCRSDKError extends Error {}

export class OCRAPIError extends OCRSDKError {
  statusCode: number
  body: string

  constructor (statusCode: number, body: string) {
    super(`API error ${statusCode}: ${body}`)
    this.name = 'OCRAPIError'
    this.statusCode = statusCode
    this.body = body
  }
}

export class OCRTimeoutError extends OCRSDKError {
  constructor (message: string) {
    super(message)
    this.name = 'OCRTimeoutError'
  }
}

export class OCRAuthenticationError extends OCRSDKError {
  constructor (message: string) {
    super(message)
    this.name = 'OCRAuthenticationError'
  }
}
