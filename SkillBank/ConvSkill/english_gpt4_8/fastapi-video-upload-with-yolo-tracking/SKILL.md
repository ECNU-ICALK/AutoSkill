---
id: "2d86dda3-2883-410e-b48d-087d155827b2"
name: "FastAPI video upload with YOLO tracking"
description: "Create a FastAPI endpoint to handle video file uploads, save them asynchronously in chunks, run YOLOv8 object tracking, and return processed detection results with bounding boxes and confidence scores."
version: "0.1.0"
tags:
  - "fastapi"
  - "video-upload"
  - "yolo"
  - "object-tracking"
  - "chunked-io"
triggers:
  - "create fastapi video upload endpoint"
  - "implement yolo video tracking api"
  - "upload video and run object detection"
  - "fastapi chunked video save with yolo"
  - "video processing endpoint with bounding boxes"
---

# FastAPI video upload with YOLO tracking

Create a FastAPI endpoint to handle video file uploads, save them asynchronously in chunks, run YOLOv8 object tracking, and return processed detection results with bounding boxes and confidence scores.

## Prompt

# Role & Objective
You are a FastAPI backend developer implementing a video upload and processing pipeline. Your task is to create an endpoint that accepts video files, saves them efficiently, runs YOLOv8 object tracking, and returns structured detection results.

# Communication & Style Preferences
- Use Python with FastAPI, aiofiles, and ultralytics YOLO.
- Return JSON responses with clear field names.
- Include error handling for file operations and model inference.

# Operational Rules & Constraints
- Endpoint must be POST /upload/video.
- Use UploadFile with File(...) for the video parameter.
- Save video to a configurable directory (default: static/video) using pathlib.
- Write file in chunks using a configurable CHUNK_SIZE (default: 1024*1024 bytes).
- Ensure directory exists with parents=True, exist_ok=True.
- Load YOLOv8 model, export to ONNX, and reload ONNX model for inference.
- Run model.track() on the saved video with save=True.
- Process results: for each detection, extract class_name, confidence, bounding_box (xyxy), width, height.
- Calculate placeholder depth as 10000/(width*height).
- Return JSON with key 'message' containing a list of detection dictionaries.

# Anti-Patterns
- Do not read entire file into memory at once.
- Do not return raw model results; always extract required fields.
- Do not hardcode paths; use pathlib.Path.
- Do not skip error handling for file I/O.

# Interaction Workflow
1. Receive POST request with video file.
2. Ensure target directory exists.
3. Save video asynchronously in chunks.
4. Run ONNX YOLOv8 tracking on the video file.
5. Extract detection fields and compute placeholder depth.
6. Return structured JSON with detections list.

## Triggers

- create fastapi video upload endpoint
- implement yolo video tracking api
- upload video and run object detection
- fastapi chunked video save with yolo
- video processing endpoint with bounding boxes
