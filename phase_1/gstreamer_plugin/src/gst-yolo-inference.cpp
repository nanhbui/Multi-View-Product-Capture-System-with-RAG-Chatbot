#include "gst-yolo-inference.h"
#include <gst/gst.h>
#include <gst/video/video.h>
#include <opencv2/opencv.hpp>
#include <json/json.h>

GST_DEBUG_CATEGORY_STATIC(gst_yolo_inference_debug);
#define GST_CAT_DEFAULT gst_yolo_inference_debug

// Properties
enum {
    PROP_0,
    PROP_MODEL_PATH,
    PROP_DEVICE,
    PROP_CONF_THRESHOLD,
    PROP_IOU_THRESHOLD,
    PROP_OVERLAY,
    PROP_POST_METADATA
};

// Default property values
#define DEFAULT_MODEL_PATH "yolov8n.pt"
#define DEFAULT_DEVICE "cpu"
#define DEFAULT_CONF_THRESHOLD 0.25f
#define DEFAULT_IOU_THRESHOLD 0.45f
#define DEFAULT_OVERLAY FALSE
#define DEFAULT_POST_METADATA TRUE

// Pad templates
static GstStaticPadTemplate sink_template = GST_STATIC_PAD_TEMPLATE(
    "sink",
    GST_PAD_SINK,
    GST_PAD_ALWAYS,
    GST_STATIC_CAPS("video/x-raw, format=(string)BGR")
);

static GstStaticPadTemplate src_template = GST_STATIC_PAD_TEMPLATE(
    "src",
    GST_PAD_SRC,
    GST_PAD_ALWAYS,
    GST_STATIC_CAPS("video/x-raw, format=(string)BGR")
);

// Function declarations
static void gst_yolo_inference_set_property(GObject *object, guint prop_id,
                                             const GValue *value, GParamSpec *pspec);
static void gst_yolo_inference_get_property(GObject *object, guint prop_id,
                                             GValue *value, GParamSpec *pspec);
static void gst_yolo_inference_finalize(GObject *object);

static gboolean gst_yolo_inference_start(GstBaseTransform *trans);
static gboolean gst_yolo_inference_stop(GstBaseTransform *trans);
static gboolean gst_yolo_inference_set_caps(GstBaseTransform *trans,
                                             GstCaps *incaps, GstCaps *outcaps);
static GstFlowReturn gst_yolo_inference_transform_ip(GstBaseTransform *trans,
                                                       GstBuffer *buf);

// Class initialization
#define gst_yolo_inference_parent_class parent_class
G_DEFINE_TYPE(GstYoloInference, gst_yolo_inference, GST_TYPE_BASE_TRANSFORM);

static void gst_yolo_inference_class_init(GstYoloInferenceClass *klass) {
    GObjectClass *gobject_class = G_OBJECT_CLASS(klass);
    GstElementClass *element_class = GST_ELEMENT_CLASS(klass);
    GstBaseTransformClass *transform_class = GST_BASE_TRANSFORM_CLASS(klass);

    // Set callbacks
    gobject_class->set_property = gst_yolo_inference_set_property;
    gobject_class->get_property = gst_yolo_inference_get_property;
    gobject_class->finalize = gst_yolo_inference_finalize;

    transform_class->start = GST_DEBUG_FUNCPTR(gst_yolo_inference_start);
    transform_class->stop = GST_DEBUG_FUNCPTR(gst_yolo_inference_stop);
    transform_class->set_caps = GST_DEBUG_FUNCPTR(gst_yolo_inference_set_caps);
    transform_class->transform_ip = GST_DEBUG_FUNCPTR(gst_yolo_inference_transform_ip);

    // Install properties
    g_object_class_install_property(gobject_class, PROP_MODEL_PATH,
        g_param_spec_string("model-path", "Model Path",
            "Path to YOLO TorchScript model file",
            DEFAULT_MODEL_PATH,
            (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_DEVICE,
        g_param_spec_string("device", "Device",
            "Device to run inference on (cpu or cuda)",
            DEFAULT_DEVICE,
            (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_CONF_THRESHOLD,
        g_param_spec_float("conf-threshold", "Confidence Threshold",
            "Minimum confidence for detections",
            0.0f, 1.0f, DEFAULT_CONF_THRESHOLD,
            (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_IOU_THRESHOLD,
        g_param_spec_float("iou-threshold", "IOU Threshold",
            "IOU threshold for Non-Maximum Suppression",
            0.0f, 1.0f, DEFAULT_IOU_THRESHOLD,
            (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_OVERLAY,
        g_param_spec_boolean("overlay", "Overlay",
            "Draw bounding boxes on output video",
            DEFAULT_OVERLAY,
            (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    g_object_class_install_property(gobject_class, PROP_POST_METADATA,
        g_param_spec_boolean("post-metadata", "Post Metadata",
            "Post detection metadata to bus",
            DEFAULT_POST_METADATA,
            (GParamFlags)(G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS)));

    // Set metadata
    gst_element_class_set_static_metadata(element_class,
        "YOLO Inference",
        "Filter/Effect/Video",
        "Runs YOLO object detection/segmentation on video frames using LibTorch",
        "Claude Code <noreply@anthropic.com>");

    // Add pad templates
    gst_element_class_add_static_pad_template(element_class, &src_template);
    gst_element_class_add_static_pad_template(element_class, &sink_template);
}

static void gst_yolo_inference_init(GstYoloInference *filter) {
    // Initialize properties with default values
    filter->model_path = g_strdup(DEFAULT_MODEL_PATH);
    filter->device = g_strdup(DEFAULT_DEVICE);
    filter->conf_threshold = DEFAULT_CONF_THRESHOLD;
    filter->iou_threshold = DEFAULT_IOU_THRESHOLD;
    filter->overlay = DEFAULT_OVERLAY;
    filter->post_metadata = DEFAULT_POST_METADATA;

    filter->detector = nullptr;

    gst_base_transform_set_in_place(GST_BASE_TRANSFORM(filter), TRUE);
}

static void gst_yolo_inference_set_property(GObject *object, guint prop_id,
                                             const GValue *value, GParamSpec *pspec) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(object);

    switch (prop_id) {
        case PROP_MODEL_PATH:
            g_free(filter->model_path);
            filter->model_path = g_value_dup_string(value);
            break;
        case PROP_DEVICE:
            g_free(filter->device);
            filter->device = g_value_dup_string(value);
            break;
        case PROP_CONF_THRESHOLD:
            filter->conf_threshold = g_value_get_float(value);
            break;
        case PROP_IOU_THRESHOLD:
            filter->iou_threshold = g_value_get_float(value);
            break;
        case PROP_OVERLAY:
            filter->overlay = g_value_get_boolean(value);
            break;
        case PROP_POST_METADATA:
            filter->post_metadata = g_value_get_boolean(value);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
            break;
    }
}

static void gst_yolo_inference_get_property(GObject *object, guint prop_id,
                                             GValue *value, GParamSpec *pspec) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(object);

    switch (prop_id) {
        case PROP_MODEL_PATH:
            g_value_set_string(value, filter->model_path);
            break;
        case PROP_DEVICE:
            g_value_set_string(value, filter->device);
            break;
        case PROP_CONF_THRESHOLD:
            g_value_set_float(value, filter->conf_threshold);
            break;
        case PROP_IOU_THRESHOLD:
            g_value_set_float(value, filter->iou_threshold);
            break;
        case PROP_OVERLAY:
            g_value_set_boolean(value, filter->overlay);
            break;
        case PROP_POST_METADATA:
            g_value_set_boolean(value, filter->post_metadata);
            break;
        default:
            G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
            break;
    }
}

static void gst_yolo_inference_finalize(GObject *object) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(object);

    g_free(filter->model_path);
    g_free(filter->device);

    if (filter->detector) {
        delete filter->detector;
        filter->detector = nullptr;
    }

    G_OBJECT_CLASS(parent_class)->finalize(object);
}

static gboolean gst_yolo_inference_start(GstBaseTransform *trans) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(trans);

    GST_INFO_OBJECT(filter, "Starting YOLO inference");
    GST_INFO_OBJECT(filter, "Model path: %s", filter->model_path);
    GST_INFO_OBJECT(filter, "Device: %s", filter->device);

    try {
        filter->detector = new yolo::YOLODetector(
            filter->model_path,
            filter->device,
            filter->conf_threshold,
            filter->iou_threshold
        );
        GST_INFO_OBJECT(filter, "YOLO detector initialized successfully");
        return TRUE;
    } catch (const std::exception& e) {
        GST_ERROR_OBJECT(filter, "Failed to initialize YOLO detector: %s", e.what());
        return FALSE;
    }
}

static gboolean gst_yolo_inference_stop(GstBaseTransform *trans) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(trans);

    GST_INFO_OBJECT(filter, "Stopping YOLO inference");

    if (filter->detector) {
        delete filter->detector;
        filter->detector = nullptr;
    }

    return TRUE;
}

static gboolean gst_yolo_inference_set_caps(GstBaseTransform *trans,
                                             GstCaps *incaps, GstCaps *outcaps) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(trans);

    if (!gst_video_info_from_caps(&filter->video_info, incaps)) {
        GST_ERROR_OBJECT(filter, "Failed to parse caps");
        return FALSE;
    }

    GST_INFO_OBJECT(filter, "Video format: %dx%d",
                    filter->video_info.width, filter->video_info.height);

    return TRUE;
}

static GstFlowReturn gst_yolo_inference_transform_ip(GstBaseTransform *trans,
                                                       GstBuffer *buf) {
    GstYoloInference *filter = GST_YOLO_INFERENCE(trans);

    if (!filter->detector) {
        GST_ERROR_OBJECT(filter, "Detector not initialized");
        return GST_FLOW_ERROR;
    }

    // Map buffer
    GstMapInfo map;
    if (!gst_buffer_map(buf, &map, GST_MAP_READWRITE)) {
        GST_ERROR_OBJECT(filter, "Failed to map buffer");
        return GST_FLOW_ERROR;
    }

    // Convert to OpenCV Mat
    cv::Mat frame(filter->video_info.height, filter->video_info.width,
                  CV_8UC3, map.data, filter->video_info.stride[0]);

    // Run inference
    std::vector<yolo::Detection> detections = filter->detector->detect(frame);

    GST_DEBUG_OBJECT(filter, "Detected %zu objects", detections.size());

    // Draw overlay if requested
    if (filter->overlay) {
        for (const auto& det : detections) {
            cv::rectangle(frame, det.bbox, cv::Scalar(0, 255, 0), 2);

            std::string label = "Conf: " + std::to_string(det.confidence);
            cv::putText(frame, label,
                        cv::Point(det.bbox.x, det.bbox.y - 5),
                        cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 255, 0), 2);
        }
    }

    // Post metadata to bus if requested
    if (filter->post_metadata && !detections.empty()) {
        Json::Value root;
        root["timestamp"] = (Json::Value::UInt64)GST_BUFFER_PTS(buf);
        root["num_detections"] = (Json::Value::UInt)detections.size();

        Json::Value detections_array(Json::arrayValue);
        for (const auto& det : detections) {
            Json::Value det_obj;
            det_obj["bbox"]["x"] = det.bbox.x;
            det_obj["bbox"]["y"] = det.bbox.y;
            det_obj["bbox"]["width"] = det.bbox.width;
            det_obj["bbox"]["height"] = det.bbox.height;
            det_obj["confidence"] = det.confidence;
            det_obj["class_id"] = det.class_id;
            det_obj["track_id"] = det.track_id;
            detections_array.append(det_obj);
        }
        root["detections"] = detections_array;

        Json::StreamWriterBuilder writer;
        std::string json_str = Json::writeString(writer, root);

        // Post message to bus
        GstStructure *s = gst_structure_new("yolo-inference",
            "metadata", G_TYPE_STRING, json_str.c_str(),
            NULL);
        GstMessage *msg = gst_message_new_application(GST_OBJECT(filter), s);
        gst_element_post_message(GST_ELEMENT(filter), msg);
    }

    gst_buffer_unmap(buf, &map);

    return GST_FLOW_OK;
}

// Plugin initialization
static gboolean plugin_init(GstPlugin *plugin) {
    GST_DEBUG_CATEGORY_INIT(gst_yolo_inference_debug, "yoloinference", 0,
                             "YOLO Inference Plugin");

    return gst_element_register(plugin, "yoloinference", GST_RANK_NONE,
                                GST_TYPE_YOLO_INFERENCE);
}

#define PACKAGE "yoloinference"
#define VERSION "1.0.0"
#define GST_LICENSE "LGPL"
#define GST_PACKAGE_NAME "GStreamer YOLO Inference Plugin"
#define GST_PACKAGE_ORIGIN "https://github.com/anthropics/claude-code"

GST_PLUGIN_DEFINE(
    GST_VERSION_MAJOR,
    GST_VERSION_MINOR,
    yoloinference,
    "YOLO object detection and segmentation using LibTorch",
    plugin_init,
    VERSION,
    GST_LICENSE,
    GST_PACKAGE_NAME,
    GST_PACKAGE_ORIGIN
)
