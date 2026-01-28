#ifndef YOLO_DETECTOR_H
#define YOLO_DETECTOR_H

#include <torch/script.h>
#include <torch/torch.h>
#include <opencv2/opencv.hpp>
#include <vector>
#include <string>
#include <memory>

namespace yolo {

/**
 * Detection result structure
 */
struct Detection {
    cv::Rect bbox;          // Bounding box (x, y, width, height)
    int class_id;           // Class ID
    float confidence;       // Confidence score
    cv::Mat mask;           // Segmentation mask (if available)
    int track_id;           // Track ID (for multi-object tracking)
};

/**
 * YOLO Detector class using LibTorch
 *
 * Supports both detection and segmentation models
 */
class YOLODetector {
public:
    /**
     * Constructor
     * @param model_path Path to TorchScript model (.pt file)
     * @param device Device to run inference on ("cpu" or "cuda")
     * @param conf_threshold Confidence threshold for filtering detections
     * @param iou_threshold IOU threshold for NMS
     */
    YOLODetector(const std::string& model_path,
                 const std::string& device = "cpu",
                 float conf_threshold = 0.25,
                 float iou_threshold = 0.45);

    ~YOLODetector();

    /**
     * Run inference on an image
     * @param image Input BGR image (OpenCV Mat)
     * @return Vector of detections
     */
    std::vector<Detection> detect(const cv::Mat& image);

    /**
     * Check if model supports segmentation
     */
    bool has_segmentation() const { return is_segmentation_model_; }

    /**
     * Get input size of the model
     */
    cv::Size get_input_size() const { return input_size_; }

private:
    /**
     * Preprocess image for YOLO
     */
    torch::Tensor preprocess(const cv::Mat& image);

    /**
     * Postprocess YOLO output
     */
    std::vector<Detection> postprocess(torch::Tensor& output, const cv::Size& original_size);

    /**
     * Non-Maximum Suppression
     */
    std::vector<int> nms(const std::vector<cv::Rect>& boxes,
                         const std::vector<float>& scores,
                         float iou_threshold);

    /**
     * Calculate IOU between two boxes
     */
    float calculate_iou(const cv::Rect& box1, const cv::Rect& box2);

    // Model and device
    torch::jit::script::Module module_;
    torch::Device device_;

    // Model configuration
    cv::Size input_size_;
    float conf_threshold_;
    float iou_threshold_;
    bool is_segmentation_model_;

    // Tracking
    int next_track_id_;
    std::map<int, cv::Point2f> prev_centers_;  // Track ID -> center point
};

} // namespace yolo

#endif // YOLO_DETECTOR_H
