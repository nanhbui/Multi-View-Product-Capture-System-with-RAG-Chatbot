#!/bin/bash
# Build script for GStreamer YOLO Inference Plugin

set -e  # Exit on error

echo "========================================="
echo "GStreamer YOLO Inference Plugin Builder"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "CMakeLists.txt" ]; then
    echo -e "${RED}Error: CMakeLists.txt not found${NC}"
    echo "Please run this script from the gstreamer_plugin directory"
    exit 1
fi

# Step 1: Check dependencies
echo ""
echo "Step 1: Checking dependencies..."
echo "--------------------------------"

# Check for cmake
if ! command -v cmake &> /dev/null; then
    echo -e "${RED}cmake not found. Please install cmake${NC}"
    exit 1
fi
echo -e "${GREEN}✓ cmake found${NC}"

# Check for pkg-config
if ! command -v pkg-config &> /dev/null; then
    echo -e "${RED}pkg-config not found. Please install pkg-config${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pkg-config found${NC}"

# Check for GStreamer
if ! pkg-config --exists gstreamer-1.0; then
    echo -e "${RED}GStreamer development files not found${NC}"
    echo "Install with: sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev"
    exit 1
fi
GST_VERSION=$(pkg-config --modversion gstreamer-1.0)
echo -e "${GREEN}✓ GStreamer ${GST_VERSION} found${NC}"

# Check for OpenCV
if ! pkg-config --exists opencv4; then
    echo -e "${YELLOW}Warning: OpenCV 4 not found via pkg-config${NC}"
    echo "Trying opencv..."
    if ! pkg-config --exists opencv; then
        echo -e "${RED}OpenCV not found${NC}"
        echo "Install with: sudo apt-get install libopencv-dev"
        exit 1
    fi
fi
echo -e "${GREEN}✓ OpenCV found${NC}"

# Check for libtorch
if [ -z "$LIBTORCH_PATH" ]; then
    echo -e "${YELLOW}Warning: LIBTORCH_PATH not set${NC}"
    echo "Checking common locations..."

    COMMON_PATHS=(
        "$HOME/libtorch"
        "/usr/local/libtorch"
        "/opt/libtorch"
    )

    FOUND=0
    for path in "${COMMON_PATHS[@]}"; do
        if [ -d "$path" ]; then
            export LIBTORCH_PATH="$path"
            export CMAKE_PREFIX_PATH="$LIBTORCH_PATH"
            echo -e "${GREEN}✓ Found libtorch at $path${NC}"
            FOUND=1
            break
        fi
    done

    if [ $FOUND -eq 0 ]; then
        echo -e "${RED}libtorch not found${NC}"
        echo ""
        echo "Please download libtorch from:"
        echo "https://pytorch.org/get-started/locally/"
        echo ""
        echo "Then extract it and set LIBTORCH_PATH:"
        echo "export LIBTORCH_PATH=/path/to/libtorch"
        echo "export CMAKE_PREFIX_PATH=\$LIBTORCH_PATH"
        exit 1
    fi
else
    export CMAKE_PREFIX_PATH="$LIBTORCH_PATH"
    echo -e "${GREEN}✓ libtorch found at $LIBTORCH_PATH${NC}"
fi

# Check for jsoncpp
if ! pkg-config --exists jsoncpp; then
    echo -e "${RED}jsoncpp not found${NC}"
    echo "Install with: sudo apt-get install libjsoncpp-dev"
    exit 1
fi
echo -e "${GREEN}✓ jsoncpp found${NC}"

# Step 2: Create build directory
echo ""
echo "Step 2: Preparing build directory..."
echo "------------------------------------"
rm -rf build
mkdir -p build
cd build
echo -e "${GREEN}✓ Build directory created${NC}"

# Step 3: Run CMake
echo ""
echo "Step 3: Running CMake..."
echo "------------------------"
cmake .. -DCMAKE_PREFIX_PATH="$CMAKE_PREFIX_PATH"

if [ $? -ne 0 ]; then
    echo -e "${RED}CMake configuration failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ CMake configuration successful${NC}"

# Step 4: Build
echo ""
echo "Step 4: Building plugin..."
echo "----------------------------"
make -j$(nproc)

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Build successful${NC}"

# Step 5: Install
echo ""
echo "Step 5: Installing plugin..."
echo "-----------------------------"
make install

if [ $? -ne 0 ]; then
    echo -e "${RED}Installation failed${NC}"
    exit 1
fi

PLUGIN_DIR="$HOME/.local/share/gstreamer-1.0/plugins"
echo -e "${GREEN}✓ Plugin installed to ${PLUGIN_DIR}${NC}"

# Step 6: Verify installation
echo ""
echo "Step 6: Verifying installation..."
echo "----------------------------------"

# Update plugin registry
export GST_PLUGIN_PATH="$PLUGIN_DIR:$GST_PLUGIN_PATH"
gst-inspect-1.0 --gst-plugin-path="$PLUGIN_DIR" yoloinference > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Plugin registered successfully${NC}"
    echo ""
    echo "Plugin info:"
    gst-inspect-1.0 --gst-plugin-path="$PLUGIN_DIR" yoloinference | head -20
else
    echo -e "${YELLOW}Warning: Plugin verification failed${NC}"
    echo "You may need to run:"
    echo "export GST_PLUGIN_PATH=$PLUGIN_DIR:\$GST_PLUGIN_PATH"
fi

# Success message
echo ""
echo "========================================="
echo -e "${GREEN}BUILD COMPLETED SUCCESSFULLY${NC}"
echo "========================================="
echo ""
echo "To use the plugin, set:"
echo "export GST_PLUGIN_PATH=$PLUGIN_DIR:\$GST_PLUGIN_PATH"
echo ""
echo "Test with:"
echo "gst-inspect-1.0 yoloinference"
echo ""
