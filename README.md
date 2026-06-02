
**CCTV Road Anomaly Detection**
A computer vision system for detecting and segmenting road surface defects from traffic camera feeds, built on top of the Finnish Transport Infrastructure Agency's (Fintraffic/Digitraffic) public camera API.

What This Project Does
This system pulls live road camera images from Finland's national traffic camera network, runs instance segmentation inference to identify road surface defects, and stores both the camera metadata and detection results in a PostgreSQL database. The long-term goal is a production-grade pipeline that continuously monitors road conditions and surfaces anomaly data for inspection and reporting.

Current Status — In Development
The project is in active early development. The backend application layer and the ML pipeline exist and run independently. Integration between them is partially done but not yet production-ready.
**Backend Application (backend/app)**

FastAPI application with async lifespan management — the HTTP client and ML backend initialise on startup and clean up on shutdown
Shared httpx.AsyncClient with connection pooling, timeout configuration, and a base URL set from environment — used across all Fintraffic API calls
Two API routers are live:

GET /camera/{camera_id} — fetches a single camera station's metadata and image preset URLs from Digitraffic
GET /stations — fetches all camera stations in the network


Pydantic schemas for validating and parsing all Digitraffic API responses — CameraObjMain, StationObjMain, and their nested models
Structured JSON logging with separate routing for INFO/DEBUG/WARNING (stdout) and ERROR/CRITICAL (file) using a custom JSONFormatter
Settings management via pydantic-settings backed by a .env file
PostgreSQL integration via psycopg3 async — two tables: cameras (station metadata) and camera_individual (per-direction preset URLs)
A scheduled background task (APScheduler) that walks all Fintraffic stations, fetches camera metadata, and upserts records to the database — currently disabled pending stability fixes

**ML Pipeline (backend/ml/segmentation)**

SAM (Segment Anything Model, sam_b.pt) integrated via Ultralytics for instance segmentation
Dataset preparation pipeline that reads source images and their Supervisely-format JSON annotations, generates SAM segmentation masks using bounding box prompts, and writes YOLO segmentation label files (.txt) for model training
Visual debugging output — colour-coded segmentation masks composited onto source images, one colour per defect class
Dataset configuration (dataset.yaml) for YOLO training


**Training Dataset**

521 images, 520 annotation files across 6 geographies (China, Czech Republic, Norway, Japan, United States, India).

| Class | Count | Distribution |
|---|---|---|
| Longitudinal crack | 536 | 39.76% |
| Transverse crack | 299 | 22.18% |
| Alligator crack | 251 | 18.62% |
| Other corruption | 133 | 9.87% |
| Pothole | 129 | 9.57% |

---
