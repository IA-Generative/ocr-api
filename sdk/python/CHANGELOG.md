# Changelog

## [0.1.4](https://github.com/IA-Generative/ocr-api/compare/v0.1.3...v0.1.4) (2026-02-17)


### Bug Fixes

* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))


### Documentation

* update Quick Start Guide with installation instructions for uv ([#233](https://github.com/IA-Generative/ocr-api/issues/233)) ([21ddae5](https://github.com/IA-Generative/ocr-api/commit/21ddae533131c184c269b5ba5f331f4963981c12))

## [0.1.3](https://github.com/IA-Generative/ocr-api/compare/v0.1.2...v0.1.3) (2026-02-16)


### Bug Fixes

* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))


### Documentation

* update Quick Start Guide with installation instructions for uv ([#233](https://github.com/IA-Generative/ocr-api/issues/233)) ([21ddae5](https://github.com/IA-Generative/ocr-api/commit/21ddae533131c184c269b5ba5f331f4963981c12))

## [0.1.2](https://github.com/IA-Generative/ocr-api/compare/v0.1.1...v0.1.2) (2026-02-16)


### Documentation

* update Quick Start Guide with installation instructions for uv ([#233](https://github.com/IA-Generative/ocr-api/issues/233)) ([21ddae5](https://github.com/IA-Generative/ocr-api/commit/21ddae533131c184c269b5ba5f331f4963981c12))

## [0.1.1](https://github.com/IA-Generative/ocr-api/compare/v0.1.0...v0.1.1) (2026-02-16)


### Documentation

* update Quick Start Guide with installation instructions for uv ([#233](https://github.com/IA-Generative/ocr-api/issues/233)) ([21ddae5](https://github.com/IA-Generative/ocr-api/commit/21ddae533131c184c269b5ba5f331f4963981c12))

## 0.1.0 (2026-02-16)


### Documentation

* update Quick Start Guide with installation instructions for uv ([#233](https://github.com/IA-Generative/ocr-api/issues/233)) ([21ddae5](https://github.com/IA-Generative/ocr-api/commit/21ddae533131c184c269b5ba5f331f4963981c12))

## [0.1.0] - 2026-02-14

### Added
- Initial release of OCR SDK
- AsyncOCRClient for asynchronous operations with httpx
- SyncOCRClient for synchronous operations with httpx
- Complete Pydantic models for all API inputs and outputs
- Custom exception classes (OCRAPIError, OCRTimeoutError, etc.)
- Context managers for automatic connection management
- Comprehensive documentation (README, QUICKSTART, USAGE_GUIDE)
- Example files demonstrating various use cases
- Validation test suite

### Features
- Health check endpoint support
- Job creation (file upload) with various options
- Task status monitoring
- Task listing with pagination
- Text extraction from completed tasks
- Process endpoint (one-step upload and wait)
- Support for authentication via API key
- Configurable timeouts
- Proper error handling and reporting

### Package
- Compatible with Python >= 3.10
- Installable via uv or pip
- Minimal dependencies: httpx, pydantic, pydantic-settings
