/**
 * Simple validation test for the SDK build
 * This test ensures that all expected exports are available
 */

import {
  SyncOCRClient,
  TaskStatus,
  TaskOperation,
  OCRAPIError,
  OCRTimeoutError,
  OCRValidationError,
  VERSION,
} from "../dist/index.js";

console.log("Running SDK validation tests...\n");

let testsPassed = 0;
let testsFailed = 0;

// Test 1: Check that SyncOCRClient is a class
try {
  if (typeof SyncOCRClient === "function") {
    console.log("✓ SyncOCRClient is available");
    testsPassed++;
  } else {
    console.error("✗ SyncOCRClient is not a class/function");
    testsFailed++;
  }
} catch (error) {
  console.error("✗ Error checking SyncOCRClient:", error.message);
  testsFailed++;
}

// Test 2: Check TaskStatus enum
try {
  if (TaskStatus.COMPLETED === "completed" && TaskStatus.FAILED === "failed") {
    console.log("✓ TaskStatus enum is correct");
    testsPassed++;
  } else {
    console.error("✗ TaskStatus enum has incorrect values");
    testsFailed++;
  }
} catch (error) {
  console.error("✗ Error checking TaskStatus:", error.message);
  testsFailed++;
}

// Test 3: Check TaskOperation enum
try {
  if (TaskOperation.DEFAULT === "default" && TaskOperation.OCR === "ocr") {
    console.log("✓ TaskOperation enum is correct");
    testsPassed++;
  } else {
    console.error("✗ TaskOperation enum has incorrect values");
    testsFailed++;
  }
} catch (error) {
  console.error("✗ Error checking TaskOperation:", error.message);
  testsFailed++;
}

// Test 4: Check exceptions
try {
  const apiError = new OCRAPIError(500, "Test error");
  const timeoutError = new OCRTimeoutError("Test timeout");
  const validationError = new OCRValidationError("Test validation");
  
  if (
    apiError.statusCode === 500 &&
    apiError.name === "OCRAPIError" &&
    timeoutError.name === "OCRTimeoutError" &&
    validationError.name === "OCRValidationError"
  ) {
    console.log("✓ Exception classes work correctly");
    testsPassed++;
  } else {
    console.error("✗ Exception classes are not working correctly");
    testsFailed++;
  }
} catch (error) {
  console.error("✗ Error checking exceptions:", error.message);
  testsFailed++;
}

// Test 5: Check VERSION
try {
  if (typeof VERSION === "string" && VERSION.length > 0) {
    console.log(`✓ VERSION is defined: ${VERSION}`);
    testsPassed++;
  } else {
    console.error("✗ VERSION is not defined correctly");
    testsFailed++;
  }
} catch (error) {
  console.error("✗ Error checking VERSION:", error.message);
  testsFailed++;
}

// Test 6: Check client instantiation
try {
  const client = new SyncOCRClient({
    baseUrl: "http://localhost:5000",
    timeout: 10000,
  });
  
  if (client && typeof client.getHealth === "function") {
    console.log("✓ SyncOCRClient can be instantiated with methods");
    testsPassed++;
  } else {
    console.error("✗ SyncOCRClient instantiation failed");
    testsFailed++;
  }
} catch (error) {
  console.error("✗ Error instantiating client:", error.message);
  testsFailed++;
}

// Summary
console.log("\n" + "=".repeat(50));
console.log(`Tests passed: ${testsPassed}`);
console.log(`Tests failed: ${testsFailed}`);
console.log("=".repeat(50));

if (testsFailed > 0) {
  process.exit(1);
} else {
  console.log("\n✓ All SDK validation tests passed!");
  process.exit(0);
}
