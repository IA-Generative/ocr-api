/**
 * TypeScript models for OCR API inputs and outputs.
 * Mirrors the Python SDK models.
 */

/**
 * Task status enum.
 */
export enum TaskStatus {
  CREATED = "created",
  QUEUED = "queued",
  STARTED = "started",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
  RETRYING = "retrying",
  CANCELED = "canceled",
  TIMEOUT = "timeout",
}

/**
 * Task operation enum.
 */
export enum TaskOperation {
  OCR = "ocr",
  DEFAULT = "default",
  SAVE_TEMPLATE = "save_template",
  FORMS = "forms",
  VECTORIZE = "vectorize",
  VLM_OCR = "vlm_ocr",
  DOCLING = "docling",
}

/**
 * Base box interface.
 */
export interface BaseBox {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}

/**
 * Bounding box with text.
 */
export interface Bbox extends BaseBox {
  text: string;
}

/**
 * Checkbox interface.
 */
export interface Checkbox extends BaseBox {
  is_checked: boolean;
}

/**
 * Layout interface.
 */
export interface Layout {
  type: string;
  bbox?: Bbox | null;
}

/**
 * Region of interest interface.
 */
export interface RegionOfInterest {
  interest_zone: Bbox[];
  labels?: string | null;
}

/**
 * Input form interface.
 */
export interface InputForm {
  storage_file_path: string;
  raw_filename: string;
  content_type: string;
  ext: string;
  size: number;
  process_type: string;
  group_id?: string | null;
  interest_zone?: RegionOfInterest[];
}

/**
 * Form entry interface.
 */
export interface FormEntry {
  field_name?: string | null;
  field_value?: string | null;
}

/**
 * Page interface.
 */
export interface Page {
  page: number;
  page_url?: string | null;
  boxes: Bbox[];
  layouts: Layout[];
  checkboxes: Checkbox[];
  form_entries: FormEntry[];
}

/**
 * OCR result interface.
 */
export interface OCRResult {
  type: string;
  model_name: string;
  created_at: number;
  updated_at: number;
  version: string;
  total_pages: number;
  pages: Page[];
  extras?: Record<string, any> | null;
  text?: string;
}

/**
 * Task model interface.
 */
export interface TaskModel {
  id: string;
  user_id: string;
  group_id?: string | null;
  type: string;
  status: string;
  percentage?: number;
  input?: InputForm | null;
  output?: OCRResult | null;
  created_at: number;
  updated_at: number;
  extras?: Record<string, any> | null;
  position?: number | null;
  content_hash?: string | null;
}

/**
 * Health check interface.
 */
export interface Health {
  name: string;
  version: string;
  up_time: string;
  status: string;
  dependencies?: Health[];
}

/**
 * Process response interface.
 */
export interface ProcessResponse {
  page_content: string;
  metadata: Record<string, any>;
}
