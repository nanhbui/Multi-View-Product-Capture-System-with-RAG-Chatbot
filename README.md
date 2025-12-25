# Multi-View Product Data Capture System

**Version 1.0.0 - December 2025**

**Professional-grade, real-time multi-angle product capture with AI vision analysis and RAG-powered chatbot**

## 📊 System Summary

**Current Version:** 1.0.0 (Production-Ready)
**Total Components:** 2 Phases (Capture + RAG Chatbot)
**Core Technologies:** YOLOv8-Seg, GPT-4o Vision, LangGraph, FastAPI
**Database:** MongoDB + ChromaDB Vector Store
**API Endpoints:** 10+ REST endpoints with Swagger UI
**Documentation:** 4,000+ lines across 6 comprehensive guides

## 🆕 Latest Updates (December 2025)

### YOLOv8 Segmentation & Background Removal 🎨
- ✅ **Segmentation model** - YOLOv8n-seg.pt with instance segmentation
- ✅ **Transparent PNG output** - Background automatically removed with alpha channel
- ✅ **Real-time mask visualization** - Green overlay showing detected object
- ✅ **Separate mask files** - Binary masks saved for each capture
- ✅ **Histogram visualization** - Real-time brightness analysis on UI
- ✅ **Auto lighting detection** - Warns about dark/bright images
- ✅ **Gamma correction** - Automatic brightening for low-light captures

### Modular Architecture 📦
- ✅ **Image Processing Module** - GrabCut, SIFT, Super-Resolution, mask refinement
- ✅ **GStreamer Pipeline Module** - Tee, RTSP/HLS streaming, multi-camera support
- ✅ **Gesture Control Module** - MediaPipe hand tracking for touchless capture
- ✅ **Clean separation** - Reusable components for advanced features

### FastAPI REST API Server
- ✅ **Production-ready REST API** with 10+ endpoints
- ✅ **Auto-generated Swagger UI** at `/docs`
- ✅ **Batch processing API** - Process multiple sessions via HTTP
- ✅ **Natural language chat API** - Query products via REST
- ✅ **Health checks & monitoring** endpoints
- ✅ **Background task support** for long-running operations

### LangSmith Integration
- ✅ **Automatic tracing** of all LangChain operations
- ✅ **Debug workflows** with visual trace timeline
- ✅ **Monitor costs** - Track token usage and API calls
- ✅ **Performance metrics** - Latency, throughput, error rates
- ✅ **Team collaboration** - Share traces and annotations

### Enhanced System
- ✅ **Vector store auto-initialization** - No manual rebuilds needed
- ✅ **Graceful error handling** - Content policy refusals, malformed data
- ✅ **Three metadata format support** - Backward compatible
- ✅ **Comprehensive documentation** - 10+ guide files, 4,000+ lines

**📚 Documentation:**
- [SEGMENTATION_UPDATE.md](SEGMENTATION_UPDATE.md) - Segmentation & lighting features guide
- [phase_1/modules/README.md](phase_1/modules/README.md) - Module documentation
- [API_GUIDE.md](API_GUIDE.md) - Complete REST API documentation
- [LANGSMITH_FASTAPI_INTEGRATION.md](LANGSMITH_FASTAPI_INTEGRATION.md) - Integration guide
- [API_QUICKREF.md](API_QUICKREF.md) - Quick reference card

---

## Overview

A complete end-to-end system for automated product cataloging with computer vision, AI analysis, and natural language interaction.

## Project Overview

This system is built in two phases:

### Phase 1: Real-Time Capture & IQA ✅
- Real-time video streaming using **GStreamer** (with OpenCV fallback)
- Object detection and tracking with **YOLOv8-Seg** and ByteTrack
- **Background removal** with segmentation masks → Transparent PNG output
- **Histogram-based lighting analysis** with auto gamma correction
- Automated **Image Quality Assessment (IQA)** module
- Multi-angle capture workflow with quality control
- Metadata export for Phase 2 processing
- **Modular architecture** with advanced image processing, streaming, and gesture control
- Clean, production-ready Python codebase

### Phase 2: Vision AI & RAG Chatbot ✅
- **Vision AI**: **GPT-4o Vision Model** for automatic feature extraction from images
- **Data Processing**: **MongoDB** storage with Multi-View Verification (MVV)
- **Vector Database**: **ChromaDB** for semantic search with OpenAI embeddings
- **RAG Pipeline**: **LangGraph** state machine workflow (3-node architecture)
- **LLM Integration**: OpenAI GPT-4o/GPT-4-mini powered responses
- **Scope Control**: Topic classification to filter irrelevant queries
- **External Search**: Optional Tavily integration for web search
- **Interactive CLI**: Console-based chatbot interface

---

## Features

### Phase 1: Real-Time Capture System

- **Robust Video Streaming**: GStreamer pipeline with automatic OpenCV fallback
- **YOLOv8 Segmentation**: Instance segmentation with background removal
  - Real-time mask visualization (green overlay on detected objects)
  - Transparent PNG output with alpha channel
  - Binary mask files saved separately
- **Histogram-Based Lighting Analysis**: Real-time brightness monitoring
  - Visual histogram display in UI (top-left corner)
  - Automatic dark/bright image detection
  - Auto gamma correction for low-light conditions
  - Color-coded warnings (red=too dark, yellow=warning, green=good)
- **Real-Time Object Tracking**: YOLOv8-Seg with ByteTrack for consistent object following across frames
- **Intelligent Quality Control**: Multi-criteria IQA including:
  - Minimum object size validation (configurable threshold)
  - Object positioning and centering checks
  - Blur detection simulation
  - Contrast analysis
- **Modular Architecture**: Three specialized modules
  - **ImageProcessor**: GrabCut, SIFT, super-resolution, mask refinement
  - **GStreamerPipeline**: Tee, RTSP/HLS streaming, multi-camera support
  - **GestureController**: MediaPipe hand tracking for touchless capture
- **User-Friendly Interface**: Live video feed with bounding boxes, tracking IDs, histogram, and on-screen status
- **Metadata Export**: Automatic JSON export with transparency info, image paths, bounding boxes, timestamps, and IQA results
- **Flexible Configuration**: Easy customization of angles, quality thresholds, camera settings, and YOLO models

### Phase 2: Vision AI & RAG Chatbot

- **GPT-4o Vision Integration**: Automatic extraction of 11 product feature categories:
  - Product type, dominant colors, material composition
  - Visible text and brand identification
  - Shape description and dimensions estimate
  - Notable features and condition assessment
- **Multi-View Verification (MVV)**: Cross-angle consistency validation with confidence scoring
- **Enhanced RAG**: Vision features automatically enrich retrieval context for accurate responses
- **LangGraph Workflow**: 3-node state machine (Classification → Retrieval → Generation)
- **MongoDB Storage**: Structured product records with embedded vision features
- **ChromaDB Vector Store**: Semantic search using OpenAI text-embedding-3-small
- **Conversational AI**: Context-aware responses with scope filtering and optional web search
- **Production-Ready Code**: PEP 8 compliant, fully type-hinted, comprehensive error handling

---

## System Requirements

### Python Environment
- **Python**: 3.10 or higher
- **Package Manager**: `uv` (Astral) - recommended for fast, reliable dependency management

### System Dependencies

#### Phase 1 Requirements (Capture System)

**Linux (Ubuntu/Debian):**
```bash
# GStreamer (optional but recommended for robust video streaming)
sudo apt-get update
sudo apt-get install -y \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-pulseaudio

# V4L2 utilities (for camera support)
sudo apt-get install -y v4l-utils

# Additional OpenCV dependencies
sudo apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0
```

**Note**: If GStreamer is not installed, the system automatically falls back to standard OpenCV video capture.

#### GstShark Performance Profiling (Optional)

**GstShark** is a powerful profiling tool for analyzing GStreamer pipeline performance. It provides detailed metrics including FPS, processing time, latency, and CPU usage per element.

**Installation (Linux - Ubuntu/Debian):**

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    gtk-doc-tools \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gcc \
    make \
    autoconf \
    automake \
    libtool \
    pkg-config

# Clone GstShark repository
cd /tmp
git clone https://github.com/RidgeRun/gst-shark.git
cd gst-shark

# Configure and install (without graphviz)
./autogen.sh --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu/ --disable-graphviz
make
sudo make install

# Verify installation
gst-inspect-1.0 | grep shark
```

**Python Dependencies for Profiling:**

```bash
# Install psutil for CPU/memory monitoring
uv pip install psutil>=5.9.0
```

**Enable Profiling in Phase 1:**

```bash
# Set environment variable to enable GstShark profiling
export ENABLE_GSTSHARK_PROFILING=true

# Run capture system with profiling
uv run python phase_1/capture_system.py
```

**Profiling Output:**

When enabled, profiling generates a `performance_summary.json` file in your capture session directory with detailed metrics:

```json
{
  "session_info": {
    "start_time": "2025-12-20 22:50:27",
    "duration_seconds": 156.32
  },
  "cpu_usage": {
    "average_percent": 518.2,
    "peak_percent": 688.5
  },
  "memory_usage": {
    "average_mb": 749.3,
    "peak_mb": 892.1
  },
  "gstreamer_metrics": {
    "fps": 28.5,
    "processing_time": {...},
    "latency": {...}
  }
}
```

**Performance Optimization:**

High CPU usage (>500%) typically indicates YOLO running on CPU instead of GPU. For GPU acceleration:

```bash
# Install CUDA-enabled PyTorch (requires NVIDIA GPU with CUDA support)
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

For complete profiling documentation, see [GSTSHARK_PROFILING_GUIDE.md](GSTSHARK_PROFILING_GUIDE.md).

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install GStreamer (optional)
brew install gstreamer \
    gst-plugins-base \
    gst-plugins-good \
    gst-plugins-bad \
    gst-plugins-ugly \
    gst-libav
```

**Windows:**
- Download and install GStreamer from: https://gstreamer.freedesktop.org/download/
- Choose the **complete** installation (not minimal)
- Add GStreamer to your system PATH

#### Phase 2 Requirements (RAG Chatbot)

**MongoDB:**
- Required for storing product records and metadata
- See [Database Setup](#database-setup-mongodb) section below

**API Keys:**
- `OPENAI_API_KEY`: Required for GPT-4o Vision, embeddings, and chatbot responses

### Hardware
- **Camera**: USB webcam or built-in camera (for Phase 1)
- **GPU**: Optional but recommended for faster YOLO inference (CUDA-capable NVIDIA GPU)
- **Internet Connection**: Required for OpenAI API calls in Phase 2

---

## Installation

### Step 1: Install `uv` (Package Manager)

`uv` is a blazing-fast Python package installer and resolver developed by Astral.

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: Install via pip
pip install uv
```

Verify installation:
```bash
uv --version
```

### Step 2: Clone/Download the Project

```bash
cd /home/nanhbui/Documents/adjustment_version
```

### Step 3: Create Virtual Environment

Using `uv` to create a virtual environment:

```bash
# Create virtual environment with Python 3.10+
uv venv --python 3.10

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### Step 4: Install Python Dependencies

Install all dependencies using `uv`:

```bash
# Install from requirements.txt
uv pip install -r requirements.txt
```

This will install 17 core dependencies:
- **Phase 1**: OpenCV, YOLOv8, PyTorch, NumPy
- **Phase 2**: OpenAI, LangChain, LangGraph, ChromaDB, PyMongo, Pydantic, Tavily

### Step 5: Setup Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys (for Phase 2)
nano .env  # or use your preferred editor
```

**Required for Phase 2:**
- `OPENAI_API_KEY`: Required for both vision feature extraction and RAG chatbot
- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/`)

For Phase 1 only, you don't need to configure API keys yet. The default settings will work.

---

## 🚀 How to Run - Complete Guide

### Option 1: CLI Mode (Original)

#### Step 1: Capture Product Images
```bash
# Activate environment
source .venv/bin/activate  # or: uv shell

# Run capture system
uv run python phase_1/capture_system.py
```

**Controls:**
- Press **S** to capture current frame
- Press **Enter** to keep image, **R** to retake
- Press **Q** to quit

**Output:** `captured_images/SESSION_ID/` with 3 images + metadata.json

#### Step 2: Process & Chat (CLI)
```bash
# Process all captured sessions + start chatbot
uv run python phase_2/run_chatbot.py --process-all
```

**Interactive chatbot:**
```
You: what products do I have?
You: describe the red product
You: quit
```

---

### Option 2: API Mode (New - FastAPI Server)

#### Step 1: Start MongoDB
```bash
sudo systemctl start mongod
sudo systemctl status mongod  # Verify it's running
```

#### Step 2: Configure Environment
Edit `.env` file:
```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here
MONGODB_URI=mongodb://localhost:27017/

# Optional - Enable LangSmith tracing
LANGCHAIN_API_KEY=lsv2_pt_your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=product-rag-chatbot
```

#### Step 3: Start FastAPI Server
```bash
# Method 1: Using startup script (recommended)
./start_api.sh

# Method 2: Using uvicorn directly
uv run uvicorn phase_2.api_server:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using Python
uv run python phase_2/api_server.py
```

**Server will be available at:**
- API Root: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Step 4: Capture Products (Still CLI)
```bash
# In another terminal
uv run python phase_1/capture_system.py
```

#### Step 5: Process via API
```bash
# Health check
curl http://localhost:8000/health

# Process all captured sessions
curl -X POST "http://localhost:8000/process/batch" \
  -H "Content-Type: application/json" \
  -d '{"process_all": true}'
```

#### Step 6: Query via API
```bash
# List products
curl "http://localhost:8000/products?limit=10"

# Chat query
curl -X POST "http://localhost:8000/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "what products do I have?"}'

# Get specific product
curl "http://localhost:8000/products/20251213_093856"
```

---

### Option 3: Python Client (Programmatic)

```python
import requests

class ProductClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def query(self, question: str):
        response = requests.post(
            f"{self.base_url}/chat/query",
            json={"query": question}
        )
        return response.json()

    def list_products(self, limit=10):
        response = requests.get(
            f"{self.base_url}/products",
            params={"limit": limit}
        )
        return response.json()

# Usage
client = ProductClient()

# Query chatbot
result = client.query("what is the red product?")
print(result["response"])

# List products
products = client.list_products(5)
print(f"Total products: {products['total_count']}")
```

---

### Quick Reference - Common Commands

#### Capture Product
```bash
uv run python phase_1/capture_system.py
```

#### Process + Chat (CLI)
```bash
uv run python phase_2/run_chatbot.py --process-all
```

#### Start API Server
```bash
./start_api.sh
```

#### Test API
```bash
# Health
curl http://localhost:8000/health

# Process
curl -X POST "http://localhost:8000/process/batch" -H "Content-Type: application/json" -d '{"process_all": true}'

# Query
curl -X POST "http://localhost:8000/chat/query" -H "Content-Type: application/json" -d '{"query": "what products?"}'
```

#### View LangSmith Traces
1. Visit https://smith.langchain.com/
2. Select your project: `product-rag-chatbot`
3. View traces in realtime

---

## 🔄 Complete End-to-End Workflow

This section provides a step-by-step guide for the complete workflow from setup to querying products.

### Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.10+ installed
- [ ] MongoDB installed and running
- [ ] Camera device connected (USB webcam or built-in)
- [ ] OpenAI API key with credits
- [ ] Virtual environment created (`uv venv`)
- [ ] Dependencies installed (`uv pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys

### Step-by-Step Workflow

#### 1. **Environment Setup** (One-time)

```bash
# Clone/navigate to project
cd /home/nanhbui/Documents/adjustment_version

# Create virtual environment
uv venv --python 3.10

# Activate environment
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY and MONGODB_URI
```

#### 2. **Start MongoDB** (Required for Phase 2)

```bash
# Linux
sudo systemctl start mongod
sudo systemctl status mongod  # Verify running

# macOS
brew services start mongodb-community

# Windows - MongoDB starts automatically as a service
```

#### 3. **Phase 1: Capture Product** (With Segmentation)

```bash
# Ensure camera is connected
ls /dev/video*  # Linux - should show /dev/video0 or similar

# Run capture system
uv run python phase_1/capture_system.py
```

**What happens during capture:**
- Camera feed opens with live histogram (top-left)
- Lighting analysis shows brightness warnings
- YOLOv8-Seg detects object and shows green mask overlay
- Press **S** to capture current angle
- Press **Enter** to confirm (saves as transparent PNG)
- Press **R** to retake if needed
- Repeat for 3 angles total
- Press **Q** to quit

**Output generated:**
```
captured_images/20251213_143022/
├── angle_1.png          # Transparent PNG (BGRA)
├── angle_1_mask.png     # Binary segmentation mask
├── angle_2.png
├── angle_2_mask.png
├── angle_3.png
├── angle_3_mask.png
└── metadata.json        # Session metadata
```

**Histogram & Lighting Features:**
- **Top-left histogram**: Real-time brightness distribution
- **Brightness value**: Mean brightness (0-255)
- **Warnings**:
  - "TOO DARK - Turn on light" (brightness < 80)
  - "Low light detected" (>40% dark pixels → auto gamma applied)
  - "TOO BRIGHT - Reduce light" (brightness > 180)
  - "✓ Good lighting" (optimal conditions)

**Segmentation Features:**
- **Green overlay**: Shows what will be kept in final PNG
- **Transparent output**: Background automatically removed
- **Mask file**: Binary mask saved separately for reference

#### 4. **Phase 2 Option A: CLI Mode**

```bash
# Process all sessions + start interactive chatbot
uv run python phase_2/run_chatbot.py --process-all
```

**What happens:**
```
[INFO] Found 1 unprocessed session(s)
[INFO] Processing session: 20251213_143022
[INFO] Loading 3 images (PNG with transparency)...
[INFO] Running Multi-View Verification...
[MVV] Overall Confidence: 0.91
[INFO] Calling GPT-4o Vision API...
[SUCCESS] Extracted product features
[INFO] Stored in MongoDB
[INFO] Created ChromaDB embeddings
[SUCCESS] Processing complete!

============================================================
PRODUCT RAG CHATBOT - Interactive Session
============================================================
Type your questions below. Type 'quit' to end.

You: what products do I have?
Bot: Based on the captured data, you have...

You: what color is it?
Bot: The product is primarily...

You: quit
[INFO] Goodbye!
```

#### 5. **Phase 2 Option B: API Mode**

**Terminal 1 - Start API Server:**
```bash
# Start FastAPI server
./start_api.sh

# Server starts at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

**Terminal 2 - Process & Query:**
```bash
# Health check
curl http://localhost:8000/health

# Process all sessions
curl -X POST "http://localhost:8000/process/batch" \
  -H "Content-Type: application/json" \
  -d '{"process_all": true}'

# Query chatbot
curl -X POST "http://localhost:8000/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "what products do I have?"}'

# List products
curl "http://localhost:8000/products?limit=5"

# Get specific product
curl "http://localhost:8000/products/20251213_143022"
```

**Terminal 3 - View LangSmith Traces (Optional):**
```bash
# Open browser to https://smith.langchain.com/
# Select project: product-rag-chatbot
# Watch traces appear in real-time as you query
```

#### 6. **Verify Transparent PNGs**

```bash
# Check that PNGs have alpha channel
uv run python -c "
import cv2
img = cv2.imread('captured_images/20251213_143022/angle_1.png', cv2.IMREAD_UNCHANGED)
print(f'Image shape: {img.shape}')
print(f'Has alpha: {img.shape[2] == 4}')
print(f'Alpha range: [{img[:,:,3].min()}, {img[:,:,3].max()}]')
"
```

Expected output:
```
Image shape: (720, 1280, 4)
Has alpha: True
Alpha range: [0, 255]
```

#### 7. **Test Advanced Features** (Optional)

**Test Segmentation:**
```bash
uv run python test_segmentation.py
```

**Test Image Processing Module:**
```python
from phase_1.modules.image_processing import ImageProcessor

processor = ImageProcessor()

# Apply GrabCut
mask, segmented = processor.apply_grabcut(image)

# Super-resolution
upscaled = processor.apply_super_resolution(image, scale_factor=2)

# SIFT matching
kp, desc = processor.extract_sift_features(image)
```

**Test Gesture Control (requires MediaPipe):**
```bash
# Install MediaPipe
uv pip install mediapipe

# Run demo
uv run python phase_1/modules/gesture_control.py
```

**Test GStreamer Pipeline:**
```bash
# Check GStreamer availability
gst-launch-1.0 --version

# Test camera
gst-launch-1.0 v4l2src device=/dev/video0 ! autovideosink
```

---

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    COMPLETE WORKFLOW                    │
└─────────────────────────────────────────────────────────┘

1. SETUP (One-time)
   ├─ Install Python 3.10+
   ├─ Install MongoDB
   ├─ Create venv: uv venv
   ├─ Install deps: uv pip install -r requirements.txt
   └─ Configure .env with API keys

2. START SERVICES
   ├─ Start MongoDB: sudo systemctl start mongod
   └─ (Optional) Start API: ./start_api.sh

3. PHASE 1: CAPTURE (YOLOv8-Seg + Histogram Analysis)
   ├─ Run: uv run python phase_1/capture_system.py
   ├─ Camera opens with histogram overlay
   ├─ Lighting warnings appear (too dark/bright)
   ├─ Auto gamma correction applied if needed
   ├─ YOLOv8-Seg detects object → green mask overlay
   ├─ Press 'S' to capture → confirms segmentation
   ├─ Press Enter to save → transparent PNG created
   ├─ Repeat for 3 angles
   └─ Output: captured_images/SESSION_ID/*.png + masks

4. PHASE 2: PROCESS (GPT-4o Vision + RAG)
   Option A - CLI Mode:
   ├─ Run: uv run python phase_2/run_chatbot.py --process-all
   ├─ Loads transparent PNGs
   ├─ Runs Multi-View Verification
   ├─ Extracts features with GPT-4o Vision
   ├─ Stores in MongoDB + ChromaDB
   └─ Starts interactive chatbot

   Option B - API Mode:
   ├─ Server running at http://localhost:8000/docs
   ├─ POST /process/batch {"process_all": true}
   ├─ POST /chat/query {"query": "..."}
   └─ GET /products

5. QUERY & ANALYZE
   ├─ Ask questions: "what products do I have?"
   ├─ View LangSmith traces (optional)
   ├─ Check transparent PNGs
   └─ Export data via API

6. ADVANCED (Optional)
   ├─ Test: python test_segmentation.py
   ├─ Gesture control: python -m modules.gesture_control
   ├─ Super-resolution: ImageProcessor module
   └─ GStreamer streaming: gstreamer_pipeline module
```

---

### Troubleshooting Workflow Issues

**Issue: "No mask detected"**
- Cause: Using detection model instead of segmentation
- Fix: Ensure `YOLO_MODEL=yolov8n-seg.pt` in `.env`
- Download: `wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n-seg.pt`

**Issue: "Image too dark"**
- Solution: Auto gamma correction applies automatically
- Check histogram shows > 40% dark pixels
- Turn on room lights for better results

**Issue: "MongoDB connection failed"**
- Fix: `sudo systemctl start mongod`
- Verify: `sudo systemctl status mongod`
- Check: Connection string in `.env`

**Issue: "OpenAI API error"**
- Fix: Verify `OPENAI_API_KEY` in `.env`
- Check: API key has credits
- Test: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

**Issue: "Camera not found"**
- Fix: `ls /dev/video*` to find device
- Change `CAMERA_ID` in capture_system.py
- Test: `ffplay /dev/video0`

---

## Running Phase 1: Capture System

### Quick Start

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Run the capture system
python capture_system.py
```

### Usage Instructions

1. **Launch the System**: Run `python capture_system.py`
2. **Position Your Product**: Place the product in view of the camera
3. **Capture Angles**:
   - The system will track the largest detected object
   - Press **'S'** to capture the current angle
   - If quality is poor, you'll be prompted to retake
   - If quality is good, the image is saved and the system moves to the next angle
4. **Complete Capture**: After all angles are captured, images and metadata are saved to `captured_images/`
5. **Exit**: Press **'Q'** at any time to quit

### Keyboard Controls

| Key | Action |
|-----|--------|
| `S` | Capture current frame (shoot) |
| `Q` | Quit application |

### On-Screen Display

- **Top Bar**: Shows current angle progress (e.g., "Capturing Angle 1/3")
- **Bounding Box**: Green rectangle around detected object
- **Tracking ID**: Shows object ID and confidence score
- **Status Messages**: Bottom bar displays quality feedback and instructions

### Output Files

After capture, you'll find in `captured_images/`:
```
session_20241206_143022_angle_1.jpg
session_20241206_143022_angle_2.jpg
session_20241206_143022_angle_3.jpg
session_20241206_143022_metadata.json  ← Important for Phase 2!
```

---

## Running Phase 2: Vision AI & RAG Chatbot

### Prerequisites

1. **MongoDB is running** (verify with `sudo systemctl status mongod`)
2. **`.env` file contains** `OPENAI_API_KEY` and `MONGODB_URI`
3. **Phase 1 completed** and metadata JSON exists
4. **Image files exist** at paths specified in metadata JSON (CRITICAL!)

### Database Setup (MongoDB)

Phase 2 requires MongoDB for storing product records, metadata, and vision features.

#### Installing MongoDB

**Ubuntu/Debian:**
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
sudo systemctl status mongod
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Verify
brew services list | grep mongodb
```

**Windows:**
- Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
- Run the installer and choose "Complete" installation
- Install as a Windows Service
- MongoDB will start automatically

#### Configure MongoDB Connection

Edit your `.env` file:
```bash
OPENAI_API_KEY=sk-your-key-here
MONGODB_URI=mongodb://localhost:27017/
```

For remote MongoDB (e.g., MongoDB Atlas):
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/product_capture
```

### Step 1: Process Captured Metadata

After running Phase 1 capture, you'll have a metadata JSON file in `captured_images/`.

Process this file to:
- Load metadata and validate images
- Run Multi-View Verification (MVV)
- **Extract features using GPT-4o Vision Model**
- Store in MongoDB and create ChromaDB embeddings

```bash
# Activate virtual environment
source .venv/bin/activate

# Process specific metadata file
python run_chatbot.py --process-metadata captured_images/session_20241206_143022_metadata.json

# Or auto-detect the latest metadata file
python run_chatbot.py
```

**What Happens During Processing:**
```
============================================================
MULTI-VIEW VERIFICATION
============================================================
[INFO] Loaded 3 angles from metadata
[INFO] Running Multi-View Verification...
[INFO] Angle 1: bbox_area=95000.0, confidence=0.92
[INFO] Angle 2: bbox_area=93500.0, confidence=0.89
[INFO] Angle 3: bbox_area=94200.0, confidence=0.91
[MVV] Overall Confidence: 0.89
[MVV] Consistency: PASSED

============================================================
VISION MODEL FEATURE EXTRACTION
============================================================
[INFO] Starting Vision Model feature extraction...
[INFO] Encoding 3 images to Base64...
[INFO] Calling GPT-4o Vision API...
[SUCCESS] Extracted product features:
  - Product Type: Wireless Headphones
  - Colors: Black, Silver, Red
  - Material: Plastic with metal accents
  - Shape: Over-ear design with adjustable headband
  - Notable Features: Cushioned ear cups, brand logo, folding mechanism
  - Brand: Sony
  - Condition: New, appears unused
[INFO] Vision features integrated into MVV result

[INFO] Stored product record in MongoDB (ID: 507f1f77bcf86cd799439011)
[INFO] Created vector embeddings in ChromaDB
[SUCCESS] Processing complete!
```

### Step 2: Interactive Chatbot

The chatbot starts automatically after processing:

```
============================================================
PRODUCT RAG CHATBOT - Interactive Session
============================================================
Product Context: Multi-angle captured products with vision analysis
Model: gpt-4o-mini
Vector Store: ChromaDB with OpenAI embeddings
Database: MongoDB

Type your questions below. Type 'quit' or 'exit' to end.
============================================================

You: What products do we have?

[NODE] Topic Classification...
[CLASSIFICATION] in_scope (confidence: 0.95)
[NODE] Retrieval and Tools...
[TOOL] Performing RAG lookup...
[RAG] Retrieved 2 documents
[NODE] Generation...

Bot: We have Sony wireless headphones in black, silver, and red colors.
     They feature an over-ear design with cushioned ear cups and a folding
     mechanism. The product is in new condition.

You: What color are they?

[NODE] Topic Classification...
[CLASSIFICATION] in_scope (confidence: 0.98)
[NODE] Retrieval and Tools...
[RAG] Retrieved 2 documents
[NODE] Generation...

Bot: The headphones are primarily black with silver and red accents.

You: Tell me about the material

[NODE] Topic Classification...
[CLASSIFICATION] in_scope (confidence: 0.96)
[NODE] Retrieval and Tools...
[RAG] Retrieved 2 documents
[NODE] Generation...

Bot: The headphones are made of plastic with metal accents, giving them
     a durable yet lightweight construction.
```

---

## Phase 2 Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 2 Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1 Metadata (JSON) → Data Processor                  │
│                                 ↓                           │
│                        Load & Validate                      │
│                                 ↓                           │
│                    Multi-View Verification                  │
│                                 ↓                           │
│                 GPT-4o Vision Extraction ✨                 │
│                                 ↓                           │
│                         MongoDB Storage                     │
│                                 ↓                           │
│                    Vector Store (ChromaDB)                  │
│                                 ↓                           │
│                  LangGraph RAG Agent                        │
│                    ↓           ↓                            │
│               Topic Class.  Retrieval                       │
│                    ↓           ↓                            │
│                  In-Scope? → Generation                     │
│                                 ↓                           │
│                        User Response                        │
└─────────────────────────────────────────────────────────────┘
```

### Vision Model Integration ✨

**NEW**: The system now includes automatic feature extraction using **OpenAI Vision Model (GPT-4o)** to analyze captured product images and extract identifying features.

#### What It Does
- Automatically analyzes the first 3 captured angles using GPT-4o
- Extracts structured product features: type, colors, materials, text, shape, dimensions, notable features, condition, and brand
- Enhances the RAG summary with visual details for more intelligent chatbot responses
- Stores features in MongoDB for retrieval and semantic search

#### Key Benefits
- **Richer Context**: Chatbot can answer questions like "What color is this product?" or "What brand is it?"
- **Automatic**: No manual annotation required
- **Comprehensive**: 11 categories of product features extracted
- **Structured**: JSON output stored in database

#### Important Note
**Image files must be present for Phase 2 processing.** The vision extraction requires actual image files at the paths specified in the Phase 1 metadata JSON file. Ensure Phase 1 capture completed successfully before running Phase 2.

For detailed information about the Vision Model integration, see [VISION_INTEGRATION.md](VISION_INTEGRATION.md).

---

### Components

#### 1. [capture_system.py](capture_system.py)
Phase 1 real-time capture system with GStreamer, YOLOv8, and IQA.

#### 2. [pydantic_models.py](pydantic_models.py)
Data validation models:
- `AngleMetadata`: Single angle capture metadata
- `VisionFeatures`: Extracted product features from GPT-4o vision analysis
- `ProductRecord`: Complete product record for database
- `MVVResult`: Multi-View Verification results with vision features
- `TopicClassificationResult`: Scope classification output
- `AgentState`: LangGraph workflow state

#### 3. [data_processor.py](data_processor.py)
Core Phase 2 processing:
- **Database Storage**: MongoDB for product records and metadata
- **Vision Feature Extraction**: Automatic analysis using GPT-4o Vision Model
- **Multi-View Verification (MVV)**: Validates consistency across angles
- **Vector Store Initialization**: Creates ChromaDB embeddings
- **Metadata Processing**: Bridges Phase 1 and Phase 2

#### 4. [chatbot_rag.py](chatbot_rag.py)
LangGraph RAG chatbot with 3-node state machine:
- **Node A - Topic Classification**: Filters out-of-scope queries
- **Node B - Retrieval & Tools**: RAG lookup + optional Tavily search
- **Node C - Generation**: Synthesizes response using OpenAI

#### 5. [run_chatbot.py](run_chatbot.py)
Interactive CLI runner:
- Initializes MongoDB and ChromaDB vector store
- Processes pending metadata files
- Starts the chatbot interface

#### 6. [test_system.py](test_system.py)
End-to-end testing suite for Phase 2 components.

---

## Project Structure

```
adjustment_version/
├── phase_1/                   # Phase 1: Real-time capture system
│   ├── capture_system.py     # Main capture system with YOLOv8-Seg
│   └── modules/              # Advanced feature modules
│       ├── __init__.py
│       ├── image_processing.py     # GrabCut, SIFT, SuperRes
│       ├── gstreamer_pipeline.py   # Tee, RTSP, HLS streaming
│       ├── gesture_control.py      # MediaPipe hand tracking
│       └── README.md               # Module documentation
│
├── phase_2/                   # Phase 2: Vision AI & RAG chatbot
│   ├── api_server.py         # FastAPI REST API server
│   ├── chatbot_rag.py        # LangGraph RAG agent
│   ├── data_processor.py     # MongoDB, MVV, Vision extraction
│   ├── pydantic_models.py    # Data validation models
│   └── run_chatbot.py        # Interactive CLI runner
│
├── test/                      # Testing & validation
│   └── test_system.py        # End-to-end testing
│
├── test_segmentation.py      # Segmentation feature tests
├── start_api.sh              # FastAPI server startup script
├── requirements.txt          # Python dependencies
├── pyproject.toml            # uv project configuration
├── uv.lock                   # Dependency lock file
│
├── .env.example              # Environment variable template
├── .env                      # Your API keys (create this)
│
├── README.md                 # This file
├── SEGMENTATION_UPDATE.md    # Segmentation integration guide
├── LANGSMITH_FASTAPI_INTEGRATION.md  # LangSmith & FastAPI guide
├── API_GUIDE.md              # Complete REST API documentation
├── API_QUICKREF.md           # Quick reference card
│
├── captured_images/          # Output directory (auto-created)
│   └── SESSION_ID/
│       ├── angle_1.png       # Transparent PNG (BGRA)
│       ├── angle_1_mask.png  # Binary segmentation mask
│       ├── angle_2.png
│       ├── angle_2_mask.png
│       ├── angle_3.png
│       ├── angle_3_mask.png
│       └── metadata.json     # Session metadata
│
└── .venv/                    # Virtual environment (created by uv)
```

---

## Configuration

### Phase 1 Configuration

You can customize the capture system by editing [phase_1/capture_system.py](phase_1/capture_system.py) or via `.env` file:

**Via .env file (Recommended):**
```bash
# YOLO model configuration
YOLO_MODEL=yolov8n-seg.pt      # Segmentation model for background removal
TOTAL_ANGLES=3                  # Number of angles to capture
MIN_BBOX_AREA=10000            # Minimum object size (pixels²)
CAMERA_ID=0                     # Camera device ID
OUTPUT_DIR=captured_images      # Output directory

# Performance profiling (optional)
ENABLE_GSTSHARK_PROFILING=false  # Set to 'true' to enable GstShark profiling
```

**Via Code:**
```python
# In main() function
TOTAL_ANGLES = 3                # Number of angles to capture
MIN_BBOX_AREA = 10000          # Minimum object size (pixels²)
CAMERA_ID = 0                   # Camera device ID
OUTPUT_DIR = "captured_images"  # Output directory
MODEL_NAME = "yolov8n-seg.pt"  # YOLO segmentation model
```

### YOLO Model Options

| Model | Type | Speed | Accuracy | Size | Features |
|-------|------|-------|----------|------|----------|
| `yolov8n.pt` | Detection | Fastest | Good | 6 MB | Bounding boxes only |
| `yolov8n-seg.pt` | **Segmentation** | **Fast** | **Good** | **6.7 MB** | **Masks + transparent PNG** ✨ |
| `yolov8s-seg.pt` | Segmentation | Medium | Better | 23 MB | Better mask quality |
| `yolov8m-seg.pt` | Segmentation | Slower | Best | 54 MB | Highest accuracy |

**Recommended:** `yolov8n-seg.pt` for best balance of speed and mask quality with background removal.

### Phase 2 Configuration

Edit `.env` file:

```bash
# OpenAI API (Required)
OPENAI_API_KEY=sk-your-key-here

# MongoDB (Required)
MONGODB_URI=mongodb://localhost:27017/

# Tavily Search (Optional - for web search)
TAVILY_API_KEY=tvly-your-key-here
```

---

## Troubleshooting

### Phase 1 Issues

#### Camera Not Detected

```bash
# Linux: Check available cameras
v4l2-ctl --list-devices

# Test camera
ffplay /dev/video0
```

If you have multiple cameras, change `CAMERA_ID` in the configuration.

#### GStreamer Errors

If GStreamer fails to initialize, the system automatically falls back to standard OpenCV capture. For better performance:

1. Verify GStreamer installation:
   ```bash
   gst-inspect-1.0 --version
   ```

2. Check GStreamer plugins:
   ```bash
   gst-inspect-1.0 v4l2src
   ```

#### YOLO Model Download Issues

The first run will download the YOLOv8 model (~6 MB for nano). If download fails:

```bash
# Manually download and place in project directory
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

#### CUDA/GPU Issues

For GPU acceleration (optional):

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, YOLO will use CPU (slower but functional)
```

### Phase 2 Issues

#### MongoDB Connection Failed

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB if not running
sudo systemctl start mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

#### OpenAI API Errors

```
[ERROR] Vision API call failed: Incorrect API key provided
```

**Solution**: Verify `OPENAI_API_KEY` in `.env` file is correct and has credits.

#### Image Not Found Warnings

```
[WARNING] Image not found: /path/to/image.jpg, skipping...
```

**Solution**: Ensure Phase 1 completed successfully and image files exist at the paths specified in the metadata JSON.

#### ChromaDB Errors

```
[ERROR] Failed to initialize ChromaDB
```

**Solution**: Ensure `OPENAI_API_KEY` is set (required for OpenAI embeddings).

### General Issues

#### Import Errors

Ensure virtual environment is activated:
```bash
which python  # Should point to .venv/bin/python
```

Reinstall dependencies:
```bash
uv pip install --force-reinstall -r requirements.txt
```

#### Permission Errors (Linux)

Add your user to the video group:
```bash
sudo usermod -a -G video $USER
# Log out and log back in
```

---

## Performance Tips

### Optimize for Speed (Phase 1)
1. Use `yolov8n.pt` (nano) for fastest inference
2. Lower camera resolution: `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)`
3. Reduce FPS: `cap.set(cv2.CAP_PROP_FPS, 15)`

### Optimize for Accuracy (Phase 1)
1. Use `yolov8m.pt` (medium) for better detection
2. Increase camera resolution: `640x480` or higher
3. Ensure good lighting conditions
4. Use a plain background for products

### GPU Acceleration (Phase 1)
```bash
# Install CUDA-enabled PyTorch (if you have NVIDIA GPU)
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Reduce API Costs (Phase 2)
1. Use `gpt-4o-mini` instead of `gpt-4o` for chatbot responses
2. Reduce vision analysis detail: Change `detail: "low"` in vision extraction
3. Analyze fewer images: Modify to use 2 angles instead of 3
4. Cache vision features: Features are stored in MongoDB, no need to re-extract

---

## Testing

Run the end-to-end test suite:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
python test_system.py
```

This tests:
- MongoDB connection
- Metadata processing
- Vector store initialization
- Chatbot initialization
- In-scope and out-of-scope queries

---

## API Keys

### OpenAI API Key (Required for Phase 2)
1. Visit: https://platform.openai.com/api-keys
2. Create an account and generate an API key
3. Add to `.env` file: `OPENAI_API_KEY=sk-...`

**Cost Estimate:**
- Vision extraction: ~$0.03-0.10 per session (3 images)
- Embeddings: ~$0.0001 per session
- Chatbot: ~$0.001-0.01 per query (depending on model)

### Tavily API Key (Optional for Web Search)
1. Visit: https://tavily.com/
2. Sign up and get API key
3. Add to `.env` file: `TAVILY_API_KEY=tvly-...`

---

## Code Quality

This codebase follows industry best practices:

- **PEP 8 Compliant**: All code follows Python style guidelines
- **Type Hints**: Full type annotations for better IDE support
- **Comprehensive Documentation**: Detailed docstrings for all classes and methods
- **Error Handling**: Graceful error handling with informative messages
- **Modular Design**: Clean separation of concerns
- **Resource Management**: Proper cleanup of camera and window resources

### Running Code Quality Tools

```bash
# Format code
uv pip install black
black *.py

# Type checking
uv pip install mypy
mypy *.py

# Linting
uv pip install flake8
flake8 *.py
```

---

## Development Roadmap

### Phase 1 ✅ (Completed)
- [x] GStreamer video streaming integration
- [x] YOLOv8 object detection and tracking
- [x] IQA module with multi-criteria validation
- [x] Multi-angle capture workflow
- [x] User interface with live feedback
- [x] Metadata export to JSON

### Phase 2 ✅ (Completed)
- [x] MongoDB database integration
- [x] Multi-View Verification (MVV)
- [x] GPT-4o Vision Model integration
- [x] LangGraph RAG chatbot with 3-node workflow
- [x] ChromaDB vector store
- [x] OpenAI embeddings and LLM responses
- [x] Topic classification and scope control
- [x] Interactive CLI interface

### Future Enhancements (Planned)
- [ ] Advanced blur detection (Laplacian variance, FFT)
- [ ] Lighting quality assessment
- [ ] Auto-exposure and white balance adjustment
- [ ] Multiple object tracking
- [ ] Web UI (FastAPI + Streamlit)
- [ ] 3D reconstruction from multi-angle captures
- [ ] Batch processing for multiple products
- [ ] Export to Excel/CSV reports
- [ ] Product comparison features

---

## Contributing

This is a professional codebase designed for production use. When contributing:

1. Maintain PEP 8 compliance
2. Add comprehensive docstrings
3. Include type hints
4. Write unit tests for new features
5. Update README for any new functionality

---

## License

This project is for educational and commercial use. Please ensure compliance with:
- YOLOv8 license (AGPL-3.0)
- OpenCV license (Apache 2.0)
- OpenAI API terms of service
- MongoDB Community License

---

## Acknowledgments

- **Ultralytics**: YOLOv8 object detection framework
- **OpenCV**: Computer vision library
- **Astral**: uv package manager
- **ByteTrack**: Multi-object tracking algorithm
- **LangChain**: LLM application framework
- **OpenAI**: GPT-4o Vision and language models

---

## Support

For questions, issues, or contributions, please open an issue on the project repository.

**Built with ❤️ for Computer Vision and AI Systems**
