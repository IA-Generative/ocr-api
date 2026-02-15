/**
 * OCR SDK - JavaScript client for OCR API.
 * 
 * @packageDocumentation
 */

export { SyncOCRClient } from "./client.js";
export type { OCRClientOptions } from "./client.js";

export {
  TaskModel,
  TaskStatus,
  TaskOperation,
  Health,
  OCRResult,
  Page,
  Bbox,
  Checkbox,
  Layout,
  FormEntry,
  InputForm,
  RegionOfInterest,
  ProcessResponse,
  BaseBox,
} from "./models.js";

export {
  OCRSDKError,
  OCRAPIError,
  OCRTimeoutError,
  OCRAuthenticationError,
  OCRValidationError,
} from "./exceptions.js";

export const VERSION = "0.1.0";
