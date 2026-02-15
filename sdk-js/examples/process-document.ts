/**
 * Example of processing a document end-to-end.
 * 
 * This example demonstrates the high-level processDocument method
 * which handles upload, waiting, and result retrieval automatically.
 */

import { SyncOCRClient, TaskOperation, ProcessResponse } from "../src/index.js";

async function main() {
  // Initialize the client
  const client = new SyncOCRClient({
    baseUrl: "http://localhost:5000",
    // apiKey: "your-api-key", // Optional: Add your API key if authentication is required
  });

  try {
    console.log("Processing document...");

    // Process document end-to-end
    const results: ProcessResponse[] = await client.processDocument(
      "path/to/your/document.pdf",
      "DEFAULT",
      TaskOperation.DEFAULT,
      2000,  // Poll every 2 seconds
      300000 // Max wait 5 minutes
    );

    console.log(`Document processed successfully!`);
    console.log(`Total pages: ${results.length}`);
    console.log();

    // Display results for each page
    results.forEach((result, index) => {
      console.log(`\n--- Page ${result.metadata.page_number} ---`);
      console.log(`Content preview: ${result.page_content.substring(0, 150)}...`);
      console.log(`Metadata:`, result.metadata);
    });

  } catch (error) {
    console.error(`Error processing document: ${error}`);
    process.exit(1);
  }
}

// Run the example
main().catch(console.error);
