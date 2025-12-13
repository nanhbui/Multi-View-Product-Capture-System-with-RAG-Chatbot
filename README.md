# Multi-View Product Data Capture System

A professional-grade, real-time multi-angle product capture system with integrated object tracking, image quality assessment, automated vision-based feature extraction, and intelligent RAG-powered chatbot.

## Project Overview

This system is built in two phases:

### Phase 1: Real-Time Capture & IQA ✅
- Real-time video streaming using **GStreamer** (with OpenCV fallback)
- Object detection and tracking with **YOLOv8** and ByteTrack
- Automated **Image Quality Assessment (IQA)** module
- Multi-angle capture workflow with quality control
- Metadata export for Phase 2 processing
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
- **Real-Time Object Tracking**: YOLOv8 with ByteTrack for consistent object following across frames
- **Intelligent Quality Control**: Multi-criteria IQA including:
  - Minimum object size validation (configurable threshold)
  - Object positioning and centering checks
  - Blur detection simulation
  - Contrast analysis
- **User-Friendly Interface**: Live video feed with bounding boxes, tracking IDs, and on-screen status
- **Metadata Export**: Automatic JSON export with image paths, bounding boxes, timestamps, and IQA results
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
├── capture_system.py          # Phase 1: Real-time capture system
├── data_processor.py          # Phase 2: MongoDB, MVV, Vision extraction
├── chatbot_rag.py            # Phase 2: LangGraph RAG agent
├── pydantic_models.py        # Data validation models
├── run_chatbot.py            # Interactive CLI runner
├── test_system.py            # End-to-end testing
├── requirements.txt          # 17 Python dependencies
├── .env.example              # Environment variable template
├── .env                      # Your API keys (create this)
├── README.md                 # This file
├── VISION_INTEGRATION.md     # Vision Model integration guide
├── captured_images/          # Output directory (auto-created)
│   ├── session_*_angle_1.jpg
│   ├── session_*_angle_2.jpg
│   ├── session_*_angle_3.jpg
│   └── session_*_metadata.json
└── .venv/                    # Virtual environment (created by uv)
```

---

## Configuration

### Phase 1 Configuration

You can customize the capture system by editing [capture_system.py](capture_system.py):

```python
# In the main() function
TOTAL_ANGLES = 3          # Number of angles to capture
MIN_BBOX_AREA = 10000     # Minimum object size (pixels²)
CAMERA_ID = 0             # Camera device ID
OUTPUT_DIR = "captured_images"  # Output directory
MODEL_NAME = "yolov8n.pt" # YOLO model (n=nano, s=small, m=medium)
```

### YOLO Model Options

| Model | Speed | Accuracy | Size |
|-------|-------|----------|------|
| `yolov8n.pt` | Fastest | Good | 6 MB |
| `yolov8s.pt` | Fast | Better | 22 MB |
| `yolov8m.pt` | Medium | Best | 52 MB |

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
