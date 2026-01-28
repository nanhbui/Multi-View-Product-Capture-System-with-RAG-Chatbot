cmake_minimum_required(VERSION 3.10)
project(gst-yolo-inference VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find required packages
find_package(PkgConfig REQUIRED)

# GStreamer dependencies
pkg_check_modules(GSTREAMER REQUIRED
    gstreamer-1.0>=1.16
    gstreamer-base-1.0>=1.16
    gstreamer-video-1.0>=1.16
)

# LibTorch (PyTorch C++ API)
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

# OpenCV for image processing
find_package(OpenCV REQUIRED)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${GSTREAMER_INCLUDE_DIRS}
    ${TORCH_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
)

# Link directories
link_directories(
    ${GSTREAMER_LIBRARY_DIRS}
    ${TORCH_LIBRARY_DIRS}
)

# Source files
set(PLUGIN_SOURCES
    src/gst-yolo-inference.cpp
    src/yolo-detector.cpp
)

# Build shared library (GStreamer plugin)
add_library(gstyoloinference SHARED ${PLUGIN_SOURCES})

# Link libraries
target_link_libraries(gstyoloinference
    ${GSTREAMER_LIBRARIES}
    ${TORCH_LIBRARIES}
    ${OpenCV_LIBS}
)

# Set plugin properties
set_target_properties(gstyoloinference PROPERTIES
    PREFIX ""
    SUFFIX ".so"
)

# Installation
set(PLUGIN_INSTALL_DIR "$ENV{HOME}/.local/share/gstreamer-1.0/plugins")
install(TARGETS gstyoloinference
    LIBRARY DESTINATION ${PLUGIN_INSTALL_DIR}
)

# Print configuration summary
message(STATUS "========================================")
message(STATUS "GStreamer YOLO Inference Plugin")
message(STATUS "========================================")
message(STATUS "GStreamer version: ${GSTREAMER_VERSION}")
message(STATUS "Torch version: ${TORCH_VERSION}")
message(STATUS "OpenCV version: ${OpenCV_VERSION}")
message(STATUS "Install directory: ${PLUGIN_INSTALL_DIR}")
message(STATUS "========================================")
