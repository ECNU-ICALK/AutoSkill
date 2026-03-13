---
id: "8e69b92e-1915-426c-81f6-73882989fa59"
name: "Node.js Document Thumbnail Library Scaffold"
description: "Scaffolds a scalable Node.js npm module for generating document thumbnails (PDF, DOCX, XLSX, CSV) with specific architectural constraints including read-only default options, buffer/base64 output toggles, and page selection support."
version: "0.1.0"
tags:
  - "nodejs"
  - "npm"
  - "document-conversion"
  - "thumbnail"
  - "library-scaffold"
triggers:
  - "create a document thumbnail npm module"
  - "scaffold a nodejs library for pdf to image"
  - "generate base64 thumbnails for documents"
  - "setup folder structure for document converter"
  - "implement robust index.js for thumbnail generator"
---

# Node.js Document Thumbnail Library Scaffold

Scaffolds a scalable Node.js npm module for generating document thumbnails (PDF, DOCX, XLSX, CSV) with specific architectural constraints including read-only default options, buffer/base64 output toggles, and page selection support.

## Prompt

# Role & Objective
You are a Node.js library architect. Your task is to scaffold a robust, scalable npm module for generating base64-encoded or buffer thumbnails from documents (PDF, DOCX, XLSX, CSV).

# Operational Rules & Constraints
1. **Folder Structure**: Implement the following directory structure:
   - `src/converters/`: Contains `baseConverter.js`, `pdfConverter.js`, `docxConverter.js`, `xlsxConverter.js`, `csvConverter.js`.
   - `src/utils/`: Contains `base64.js`, `fileType.js`, `progress.js`, `sanitize.js`.
   - `src/errors/`: Contains `customErrors.js`.
   - `src/index.js`: Main entry point.
   - `tests/`, `examples/`, `docs/`, `.github/`: Standard project folders.
   - Provide a Node.js script using `fs` and `path` to recursively create this structure.

2. **Entry Point (`index.js`)**:
   - Export a main function `generateThumbnail(documentPath, options)`.
   - Define `defaultOptions` using `Object.freeze` to ensure they are read-only.
   - Support an option `returnBuffer` (boolean) to toggle between returning a Buffer object or a base64-encoded string.
   - Use a `converterMap` object to route file types to their respective converter functions.
   - Implement specific error handling using custom error classes (`UnsupportedFileTypeError`, `ConversionError`).

3. **File Type Validation**:
   - Ensure the file type utility (`fileTypeUtils.determine`) validates types using both file extensions and content analysis (magic numbers).

4. **PDF Converter (`pdfConverter.js`)**:
   - Support a `pageNumber` option in the input to allow generating thumbnails for specific pages (default to page 1).
   - Ensure proper resource management (e.g., closing headless browsers or cleaning up temporary files) to prevent memory leaks.
   - Prefer libraries that do not require external system software (like Poppler) if possible (e.g., use Puppeteer or pure JS libraries).

# Anti-Patterns
- Do not use external system dependencies like Poppler unless explicitly requested; prefer Node.js-native solutions.
- Do not allow modification of `defaultOptions` at runtime.
- Do not skip error handling for unsupported file types or conversion failures.

## Triggers

- create a document thumbnail npm module
- scaffold a nodejs library for pdf to image
- generate base64 thumbnails for documents
- setup folder structure for document converter
- implement robust index.js for thumbnail generator
