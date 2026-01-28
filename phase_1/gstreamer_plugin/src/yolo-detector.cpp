#include "yolo-detector.h"
#include <iostream>
#include <algorithm>

namespace yolo {

YOLODetector::YOLODetector(const std::string& model_path,
                           const std::string& device,
                           float conf_threshold,
                           float iou_threshold)
    : device_(device == "cuda" ? torch::kCUDA : torch::kCPU),
      conf_threshold_(conf_threshold),
      iou_threshold_(iou_threshold),
      is_segmentation_model_(false),
      next_track_id_(0) {

    std::cout << "[YOLO] Loading model from: " << model_path << std::endl;

    try {
        // Load the TorchScript model
        module_ = torch::jit::load(model_path);
        module_.to(device_);
        module_.eval();

        std::cout << "[YOLO] Model loaded successfully" << std::endl;

        // Detect if this is a segmentation model (contains '-seg' in path)
        is_segmentation_model_ = (model_path.find("-seg") != std::string::npos);

        // Default input size for YOLOv8 (will be adjusted if needed)
        input_size_ = cv::Size(640, 640);

        std::cout << "[YOLO] Model type: " << (is_segmentation_model_ ? "Segmentation" : "Detection") << std::endl;
        std::cout << "[YOLO] Input size: " << input_size_.width << "x" << input_size_.height << std::endl;
        std::cout << "[YOLO] Device: " << device << std::endl;

    } catch (const c10::Error& e) {
        std::cerr << "[YOLO] Error loading model: " << e.what() << std::endl;
        throw;
    }
}

YOLODetector::~YOLODetector() {
    std::cout << "[YOLO] Detector destroyed" << std::endl;
}

torch::Tensor YOLODetector::preprocess(const cv::Mat& image) {
    // Resize to model input size (letterbox)
    cv::Mat resized;
    cv::resize(image, resized, input_size_);

    // Convert BGR to RGB
    cv::Mat rgb;
    cv::cvtColor(resized, rgb, cv::COLOR_BGR2RGB);

    // Convert to float and normalize to [0, 1]
    rgb.convertTo(rgb, CV_32FC3, 1.0 / 255.0);

    // Convert to Torch tensor (HWC -> CHW)
    torch::Tensor tensor = torch::from_blob(
        rgb.data,
        {1, rgb.rows, rgb.cols, 3},
        torch::kFloat32
    ).clone();

    tensor = tensor.permute({0, 3, 1, 2});  // NHWC -> NCHW
    tensor = tensor.to(device_);

    return tensor;
}

std::vector<Detection> YOLODetector::detect(const cv::Mat& image) {
    if (image.empty()) {
        std::cerr << "[YOLO] Empty image provided" << std::endl;
        return {};
    }

    cv::Size original_size = image.size();

    // Preprocess
    torch::Tensor input_tensor = preprocess(image);

    // Inference
    std::vector<torch::jit::IValue> inputs;
    inputs.push_back(input_tensor);

    torch::Tensor output;
    {
        torch::NoGradGuard no_grad;
        output = module_.forward(inputs).toTensor();
    }

    // Postprocess
    return postprocess(output, original_size);
}

std::vector<Detection> YOLODetector::postprocess(torch::Tensor& output, const cv::Size& original_size) {
    std::vector<Detection> detections;

    // YOLOv8 output shape: [batch, num_predictions, num_classes + 4 (bbox)]
    // For segmentation: [batch, num_predictions, num_classes + 4 + mask_dim]

    output = output.to(torch::kCPU);
    auto output_accessor = output.accessor<float, 3>();

    int batch_size = output.size(0);
    int num_predictions = output.size(1);
    int prediction_size = output.size(2);

    // Parse predictions
    std::vector<cv::Rect> boxes;
    std::vector<float> scores;
    std::vector<int> class_ids;

    for (int i = 0; i < num_predictions; i++) {
        // Extract bbox and scores
        float cx = output_accessor[0][i][0];
        float cy = output_accessor[0][i][1];
        float w = output_accessor[0][i][2];
        float h = output_accessor[0][i][3];

        // Find max confidence and class
        float max_conf = 0.0f;
        int max_class_id = 0;

        for (int c = 4; c < prediction_size; c++) {
            float conf = output_accessor[0][i][c];
            if (conf > max_conf) {
                max_conf = conf;
                max_class_id = c - 4;
            }
        }

        // Filter by confidence threshold
        if (max_conf < conf_threshold_) {
            continue;
        }

        // Convert from center format to corner format
        float x1 = (cx - w / 2.0f) * original_size.width / input_size_.width;
        float y1 = (cy - h / 2.0f) * original_size.height / input_size_.height;
        float x2 = (cx + w / 2.0f) * original_size.width / input_size_.width;
        float y2 = (cy + h / 2.0f) * original_size.height / input_size_.height;

        // Clip to image boundaries
        x1 = std::max(0.0f, std::min(x1, static_cast<float>(original_size.width)));
        y1 = std::max(0.0f, std::min(y1, static_cast<float>(original_size.height)));
        x2 = std::max(0.0f, std::min(x2, static_cast<float>(original_size.width)));
        y2 = std::max(0.0f, std::min(y2, static_cast<float>(original_size.height)));

        cv::Rect box(static_cast<int>(x1), static_cast<int>(y1),
                     static_cast<int>(x2 - x1), static_cast<int>(y2 - y1));

        boxes.push_back(box);
        scores.push_back(max_conf);
        class_ids.push_back(max_class_id);
    }

    // Apply NMS
    std::vector<int> nms_indices = nms(boxes, scores, iou_threshold_);

    // Create final detections
    for (int idx : nms_indices) {
        Detection det;
        det.bbox = boxes[idx];
        det.class_id = class_ids[idx];
        det.confidence = scores[idx];
        det.track_id = next_track_id_++;  // Simple tracking (can be improved)

        // TODO: Extract segmentation mask if available
        // This requires parsing the mask coefficients from YOLO output

        detections.push_back(det);
    }

    return detections;
}

std::vector<int> YOLODetector::nms(const std::vector<cv::Rect>& boxes,
                                    const std::vector<float>& scores,
                                    float iou_threshold) {
    std::vector<int> indices(boxes.size());
    std::iota(indices.begin(), indices.end(), 0);

    // Sort by score (descending)
    std::sort(indices.begin(), indices.end(),
              [&scores](int i1, int i2) { return scores[i1] > scores[i2]; });

    std::vector<int> keep;
    std::vector<bool> suppressed(boxes.size(), false);

    for (size_t i = 0; i < indices.size(); i++) {
        int idx = indices[i];
        if (suppressed[idx]) continue;

        keep.push_back(idx);

        // Suppress overlapping boxes
        for (size_t j = i + 1; j < indices.size(); j++) {
            int idx2 = indices[j];
            if (suppressed[idx2]) continue;

            float iou = calculate_iou(boxes[idx], boxes[idx2]);
            if (iou > iou_threshold) {
                suppressed[idx2] = true;
            }
        }
    }

    return keep;
}

float YOLODetector::calculate_iou(const cv::Rect& box1, const cv::Rect& box2) {
    int x1 = std::max(box1.x, box2.x);
    int y1 = std::max(box1.y, box2.y);
    int x2 = std::min(box1.x + box1.width, box2.x + box2.width);
    int y2 = std::min(box1.y + box1.height, box2.y + box2.height);

    if (x2 < x1 || y2 < y1) return 0.0f;

    int intersection = (x2 - x1) * (y2 - y1);
    int area1 = box1.width * box1.height;
    int area2 = box2.width * box2.height;
    int union_area = area1 + area2 - intersection;

    return static_cast<float>(intersection) / static_cast<float>(union_area);
}

} // namespace yolo
