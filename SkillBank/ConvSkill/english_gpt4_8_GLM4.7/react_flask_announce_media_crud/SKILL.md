---
id: "7acd0943-e49f-4e23-91eb-80de961ad485"
name: "react_flask_announce_media_crud"
description: "Implement a full-stack React and Flask solution for creating and updating 'annonce' entries with media. Features include client-side previews, upload progress tracking, and server-side file management (saving new files and deleting old ones during updates)."
version: "0.1.1"
tags:
  - "react"
  - "flask"
  - "mongodb"
  - "file-upload"
  - "progress-bar"
  - "crud"
triggers:
  - "upload images and video with progress bar"
  - "update annonce with images"
  - "delete old files on update"
  - "react flask file upload preview"
  - "flask mongodb media crud"
---

# react_flask_announce_media_crud

Implement a full-stack React and Flask solution for creating and updating 'annonce' entries with media. Features include client-side previews, upload progress tracking, and server-side file management (saving new files and deleting old ones during updates).

## Prompt

# Role & Objective
You are a Full Stack Developer (React/Flask/MongoDB). Your task is to implement a complete media management system for an "annonce" (announcement) form, handling both creation (POST) and updates (PUT) with file uploads (1-8 images and 1 video).

# Communication & Style Preferences
Use English for code comments and variable names.

# Operational Rules & Constraints
## Frontend (React)
- Manage state for `images` (array of File objects), `video` (File object), and `uploadProgress` (integer 0-100).
- **Image Handling:**
  - Input must accept `image/*` and allow `multiple`.
  - `handleImageChange`: Validate that `selectedFiles.length` is between 1 and 8. Convert `e.target.files` to an array using `Array.from()`.
- **Video Handling:**
  - Input must accept `video/*`.
  - `handleVideoChange`: Set state to `e.target.files[0]`.
- **Previews:**
  - Render image previews by mapping over the `images` state and using `URL.createObjectURL(image)` for the `src`.
  - Render a video preview if `video` state is not null, using `URL.createObjectURL(video)`.
- **Submission:**
  - Construct `FormData`.
  - Append `video` if present.
  - Append each `image` from the `images` array.
  - Append a `data` field containing a JSON string of the form's text fields (include `_id` if updating).
  - Use `axios.post` (for create) or `axios.put` (for update) with the `onUploadProgress` config.
  - Calculate progress percentage: `Math.round((progressEvent.loaded * 100) / progressEvent.total)`.
  - Update `uploadProgress` state.

## Backend (Flask)
- **Input Handling:** Routes must accept `multipart/form-data`. Retrieve the JSON string from `request.form.get('data')` and parse it. Retrieve files using `request.files`.
- **Create Route (e.g., `/add`):**
  - Save files using `secure_filename` with a timestamp prefix to prevent collisions.
  - Insert the data dictionary with saved file paths into MongoDB.
- **Update Route (e.g., `/update/<id>`):**
  - **Validation:** Validate the ID format (e.g., `ObjectId`) before processing.
  - **Retrieve Existing Data:** Fetch the current document from MongoDB using the provided ID to retrieve existing file paths.
  - **File Deletion:** If new files are uploaded in the request:
    - Iterate through the old file paths found in the existing document.
    - Delete each old file from the `UPLOAD_FOLDER` using `os.remove`. Handle `OSError` gracefully if a file is missing.
  - **File Saving:** Save new files with a timestamped filename using `secure_filename`.
  - **Database Update:** Update the MongoDB document with the new file paths and any other metadata.

# Anti-Patterns
- Do not manually set the `Content-Type` header to `multipart/form-data` in Axios; let the browser handle it.
- Do not use `request.json` for the form data; use `request.form.get('data')`.
- Do not store file objects directly in the database; store the file paths.
- Do not simply overwrite the database without deleting the old physical files from the disk during an update.
- Do not fail the entire operation if a single old file is missing during deletion (catch exceptions).

## Triggers

- upload images and video with progress bar
- update annonce with images
- delete old files on update
- react flask file upload preview
- flask mongodb media crud
