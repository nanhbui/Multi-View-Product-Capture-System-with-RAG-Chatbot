#ifndef GST_YOLO_INFERENCE_H
#define GST_YOLO_INFERENCE_H

#include <gst/gst.h>
#include <gst/base/gstbasetransform.h>
#include <gst/video/video.h>
#include "yolo-detector.h"

G_BEGIN_DECLS

#define GST_TYPE_YOLO_INFERENCE (gst_yolo_inference_get_type())
#define GST_YOLO_INFERENCE(obj) \
    (G_TYPE_CHECK_INSTANCE_CAST((obj), GST_TYPE_YOLO_INFERENCE, GstYoloInference))
#define GST_YOLO_INFERENCE_CLASS(klass) \
    (G_TYPE_CHECK_CLASS_CAST((klass), GST_TYPE_YOLO_INFERENCE, GstYoloInferenceClass))
#define GST_IS_YOLO_INFERENCE(obj) \
    (G_TYPE_CHECK_INSTANCE_TYPE((obj), GST_TYPE_YOLO_INFERENCE))
#define GST_IS_YOLO_INFERENCE_CLASS(klass) \
    (G_TYPE_CHECK_CLASS_TYPE((klass), GST_TYPE_YOLO_INFERENCE))

typedef struct _GstYoloInference GstYoloInference;
typedef struct _GstYoloInferenceClass GstYoloInferenceClass;

/**
 * GstYoloInference:
 *
 * Opaque data structure.
 */
struct _GstYoloInference {
    GstBaseTransform element;

    // Properties
    gchar *model_path;
    gchar *device;
    gfloat conf_threshold;
    gfloat iou_threshold;
    gboolean overlay;
    gboolean post_metadata;

    // YOLO detector instance
    yolo::YOLODetector *detector;

    // Video info
    GstVideoInfo video_info;
};

struct _GstYoloInferenceClass {
    GstBaseTransformClass parent_class;
};

GType gst_yolo_inference_get_type(void);

G_END_DECLS

#endif // GST_YOLO_INFERENCE_H
