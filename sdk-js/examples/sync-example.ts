/**
 * Example of using the OCR SDK with synchronous operations.
 * 
 * This example demonstrates:
 * - Health check
 * - Creating an OCR job
 * - Waiting for task completion
 * - Retrieving extracted text
 */

import { SyncOCRClient, TaskOperation, OCRAPIError, OCRTimeoutError } from "../src/index.js";

async function main() {
  // Initialize the client
  const client = new SyncOCRClient({
    baseUrl: "http://localhost:5000",
    // apiKey: "your-api-key", // Optional: Add your API key if authentication is required
  });

  try {
    // 1. Check API health
    console.log("Checking API health...");
    const health = await client.getHealth();
    console.log(`API Status: ${health.status}`);
    console.log(`API Version: ${health.version}`);
    console.log(`Uptime: ${health.up_time}`);
    console.log();

    // 2. Create an OCR job
    console.log("Creating OCR job...");
    const task = await client.createJob(
      "path/to/your/document.pdf",
      "DEFAULT",
      undefined,
      TaskOperation.DEFAULT
    );
    console.log(`Task created with ID: ${task.id}`);
    console.log(`Task status: ${task.status}`);
    console.log();

    // 3. Wait for task completion
    console.log("Waiting for task to complete...");
    const completedTask = await client.waitForTask(task.id, 2000, 300000);
    console.log(`Task completed with status: ${completedTask.status}`);
    console.log();

    // 4. Get extracted text
    console.log("Retrieving extracted text...");
    const text = await client.getTaskText(task.id);
    console.log(`Extracted text (first 200 chars): ${text.substring(0, 200)}...`);
    console.log();

    // 5. Get task details
    console.log("Getting full task details...");
    const taskDetails = await client.getTask(task.id);
    console.log(`Total pages: ${taskDetails.output?.total_pages || 0}`);
    console.log(`Model used: ${taskDetails.output?.model_name || "N/A"}`);
    console.log();

    // 6. List user tasks
    console.log("Listing recent tasks...");
    const userTasks = await client.getUserTasks(1, 5);
    console.log(`Found ${userTasks.length} recent tasks:`);
    userTasks.forEach((t) => {
      console.log(`  - Task ${t.id}: ${t.status}`);
    });

  } catch (error) {
    if (error instanceof OCRTimeoutError) {
      console.error(`Timeout error: ${error.message}`);
    } else if (error instanceof OCRAPIError) {
      console.error(`API error (${error.statusCode}): ${error.responseMessage}`);
    } else {
      console.error(`Unexpected error: ${error}`);
    }
    process.exit(1);
  }
}

// Run the example
main().catch(console.error);
