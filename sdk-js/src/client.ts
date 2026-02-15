/**
 * Synchronous client for OCR API.
 */

import axios, { AxiosInstance, AxiosResponse } from "axios";
import * as fs from "fs";
import * as path from "path";
import FormData from "form-data";
import {
  Health,
  TaskModel,
  TaskOperation,
  TaskStatus,
  ProcessResponse,
} from "./models.js";
import {
  OCRAPIError,
  OCRTimeoutError,
  OCRValidationError,
} from "./exceptions.js";

/**
 * Options for the OCR client.
 */
export interface OCRClientOptions {
  /** Base URL of the OCR API */
  baseUrl: string;
  /** Optional API key for authentication */
  apiKey?: string;
  /** Default timeout for requests in milliseconds */
  timeout?: number;
}

/**
 * Synchronous client for OCR API.
 *
 * @example
 * ```typescript
 * const client = new SyncOCRClient({ baseUrl: "http://localhost:5000" });
 * const health = await client.getHealth();
 * const task = await client.createJob("path/to/file.pdf");
 * const result = await client.waitForTask(task.id);
 * ```
 */
export class SyncOCRClient {
  private client: AxiosInstance;
  private baseUrl: string;
  private timeout: number;

  /**
   * Initialize the sync OCR client.
   *
   * @param options - Client configuration options
   */
  constructor(options: OCRClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.timeout = options.timeout || 30000;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (options.apiKey) {
      headers["Authorization"] = `Bearer ${options.apiKey}`;
    }

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout,
      headers,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
          throw new OCRTimeoutError(
            `Request timed out: ${error.message}`
          );
        }

        if (error.response) {
          throw new OCRAPIError(
            error.response.status,
            error.response.data?.message ||
              error.response.data?.detail ||
              error.response.statusText ||
              "Unknown error"
          );
        }

        throw error;
      }
    );
  }

  /**
   * Get health status of the API.
   *
   * @returns Health object with API status
   */
  async getHealth(): Promise<Health> {
    const response = await this.client.get<Health>("/api/health");
    return response.data;
  }

  /**
   * Create a new OCR job.
   *
   * @param filePath - Path to the file to process
   * @param groupId - Group ID for the task (default: "DEFAULT")
   * @param interestZone - Optional JSON string defining regions of interest
   * @param taskOperation - Type of operation to perform
   * @returns TaskModel with job details
   */
  async createJob(
    filePath: string,
    groupId: string = "DEFAULT",
    interestZone?: string,
    taskOperation: TaskOperation = TaskOperation.DEFAULT
  ): Promise<TaskModel> {
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      throw new OCRValidationError(`File not found: ${filePath}`);
    }

    // Create form data
    const formData = new FormData();
    formData.append("file", fs.createReadStream(filePath), {
      filename: path.basename(filePath),
    });
    formData.append("group_id", groupId);
    formData.append("task_operation", taskOperation);

    if (interestZone) {
      formData.append("interest_zone", interestZone);
    }

    const response = await this.client.post<TaskModel>(
      "/api/jobs/",
      formData,
      {
        headers: {
          ...formData.getHeaders(),
        },
      }
    );

    return response.data;
  }

  /**
   * Get task details by ID.
   *
   * @param taskId - Task ID
   * @returns TaskModel with task details
   */
  async getTask(taskId: string): Promise<TaskModel> {
    const response = await this.client.get<TaskModel>(
      `/api/tasks/${taskId}`
    );
    return response.data;
  }

  /**
   * Get tasks for the authenticated user.
   *
   * @param page - Page number (1-indexed)
   * @param pageSize - Number of tasks per page
   * @returns List of TaskModel objects
   */
  async getUserTasks(
    page: number = 1,
    pageSize: number = 10
  ): Promise<TaskModel[]> {
    const response = await this.client.get<TaskModel[]>("/api/tasks/user/", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * Wait for a task to complete.
   *
   * @param taskId - Task ID
   * @param pollInterval - Time between status checks in milliseconds
   * @param maxWaitTime - Maximum time to wait in milliseconds
   * @returns Completed TaskModel
   * @throws OCRTimeoutError if task doesn't complete within maxWaitTime
   * @throws OCRAPIError if task fails
   */
  async waitForTask(
    taskId: string,
    pollInterval: number = 2000,
    maxWaitTime: number = 300000
  ): Promise<TaskModel> {
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitTime) {
      const task = await this.getTask(taskId);

      if (task.status === TaskStatus.COMPLETED) {
        return task;
      } else if (task.status === TaskStatus.FAILED) {
        const error =
          task.extras?.error || "Unknown error";
        throw new OCRAPIError(500, `Task failed: ${error}`);
      }

      // Wait before next poll
      await new Promise((resolve) => setTimeout(resolve, pollInterval));
    }

    throw new OCRTimeoutError(
      `Task ${taskId} did not complete within ${maxWaitTime / 1000}s`
    );
  }

  /**
   * Get extracted text from a completed task.
   *
   * @param taskId - Task ID
   * @returns Extracted text or empty string
   */
  async getTaskText(taskId: string): Promise<string> {
    const task = await this.getTask(taskId);
    return task.output?.text || "";
  }

  /**
   * Process a document end-to-end (upload + wait + retrieve).
   *
   * @param filePath - Path to the file to process
   * @param groupId - Group ID for the task
   * @param taskOperation - Type of operation to perform
   * @param pollInterval - Time between status checks in milliseconds
   * @param maxWaitTime - Maximum time to wait in milliseconds
   * @returns Array of ProcessResponse objects
   */
  async processDocument(
    filePath: string,
    groupId: string = "DEFAULT",
    taskOperation: TaskOperation = TaskOperation.DEFAULT,
    pollInterval: number = 2000,
    maxWaitTime: number = 300000
  ): Promise<ProcessResponse[]> {
    // Create job
    const task = await this.createJob(filePath, groupId, undefined, taskOperation);

    // Wait for completion
    const completedTask = await this.waitForTask(
      task.id,
      pollInterval,
      maxWaitTime
    );

    // Extract results
    const results: ProcessResponse[] = [];

    if (completedTask.output && completedTask.output.pages) {
      for (const page of completedTask.output.pages) {
        const pageText = page.boxes.map((box) => box.text).join(" ");
        results.push({
          page_content: pageText,
          metadata: {
            page_number: page.page,
            task_id: completedTask.id,
            file_name: path.basename(filePath),
          },
        });
      }
    }

    return results;
  }
}
