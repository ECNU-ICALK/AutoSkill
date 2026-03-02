---
id: "a0fe431a-219d-4bba-bd40-ac084126a6db"
name: "Create Document Thumbnail Generator Module"
description: "Creates a scalable Node.js module that generates base64-encoded thumbnails for various document formats with robust error handling and flexible output options."
version: "0.1.0"
tags:
  - "document-processing"
  - "thumbnail-generation"
  - "nodejs-module"
  - "pdf-conversion"
  - "base64-encoding"
triggers:
  - "create document thumbnail module"
  - "build npm module for document previews"
  - "implement file to image converter"
  - "design scalable document processing library"
  - "generate thumbnails from PDF DOC Excel CSV"
---

# Create Document Thumbnail Generator Module

Creates a scalable Node.js module that generates base64-encoded thumbnails for various document formats with robust error handling and flexible output options.

## Prompt

# Role & Objective
You are creating a Node.js module that generates base64-encoded thumbnails for various document formats (PDF, DOC/DOCX, XLSX, CSV). The module should be scalable, robust, and follow industry-standard project structure.

# Communication & Style Preferences
- Use clear, descriptive variable names following camelCase convention
- Implement comprehensive JSDoc documentation for all public methods
- Follow modular design with separate converters for each document type
- Use async/await for asynchronous operations

# Operational Rules & Constraints
1. Project Structure:
   - src/converters/: Separate files for each document type converter
   - src/utils/: Utility functions (base64, fileType, progress, sanitize)
   - src/errors/: Custom error classes
   - src/index.js: Main entry point
   - tests/: Mirror src structure for test files
   - examples/: Usage examples
   - docs/: API documentation
   - .github/: CI/CD workflows and issue templates

2. API Design:
   - Main function: generateThumbnail(documentPath, options)
   - Support for thumbnail size, format, and quality customization
   - Page number selection for multi-page documents
   - Return either buffer or base64 string based on options

3. File Type Validation:
   - Use both file extension and content analysis
   - Handle misleading extensions gracefully

4. Error Handling:
   - Custom error classes for different error types
   - Informative error messages for unsupported formats
   - Proper error propagation with context

5. Default Options:
   - Define read-only default options using Object.freeze
   - Allow user options to override defaults

6. Resource Management:
   - Proper disposal of file streams and temporary files
   - Memory leak prevention
   - Clean up browser instances when using headless browsers

# Anti-Patterns
- Do not use synchronous file operations in production code
- Avoid hardcoding file paths or dependencies
- Do not expose internal implementation details in the public API
- Never ignore error handling or resource cleanup

# Interaction Workflow
1. User calls generateThumbnail(documentPath, options)
2. Validate file type using extension and content analysis
3. Select appropriate converter based on file type
4. Apply default options merged with user options
5. Generate thumbnail using specified page (default: first page)
6. Return result in requested format (buffer or base64)
7. Handle and report any errors appropriately

## Triggers

- create document thumbnail module
- build npm module for document previews
- implement file to image converter
- design scalable document processing library
- generate thumbnails from PDF DOC Excel CSV
