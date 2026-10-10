"""
proxy_map_metrics.py

Drop-in helpers for arrange_full_segmentation_mask() (backend/ml/... file with onnx_to_img).
Paste the helpers ABOVE arrange_full_segmentation_mask(), then replace the tail of that
function with the "FINISHED BLOCK" at the bottom of this file.

Requires:  pip install "torchmetrics[detection]" pycocotools opencv-python numpy torch
"""
import cv2
import numpy as np
import torch
from torchmetrics.detection import MeanAveragePrecision

from backend.app.config import logger

# Training images are stored letterboxed (512 x 512) in PostgreSQL and the onnx model was trained on
# the same size, so BOTH the predictions and the ground truth are compared in this pixel space.
TENSOR_SIZE = 512

MAP_KEYS_TO_KEEP = ("map", "map_50", "map_75")

names = {
    0: "alligator crack",
    1: "longitudinal crack",
    2: "pothole",
    3: "transverse crack",
    4: "other corruption",
}


def parse_yolo_seg_annotation_text(annotation_text, tensor_size=TENSOR_SIZE):
    """
    YOLO-seg line on taasen tää:  class_id x1 y1 x2 y2 ... xn yn   (polygon, normalized 0-1 against the 512x512 letterboxed image)
    Returnataan lista of (class_id, polygon_in_pixels) where polygon_in_pixels has shape (n_points, 2).
    Lines that are not polygons (for example 5-value YOLO-detect lines) are skipped.
    """
    if annotation_text is None:
        return []
    print("in codeblock, parse_yolo_seg_annotation_text")
    print("type of annotation_text passed ", type(annotation_text))
    print("ann text content ", annotation_text)
    # psycopg returns bytea as bytes/memoryview, text columns as str, JSON round trip gives str
    if isinstance(annotation_text, (bytes, bytearray, memoryview)):
        annotation_text = bytes(annotation_text).decode("utf-8", errors="ignore")

    found_polygons = []
    for line in str(annotation_text).splitlines():
        parts = line.strip().split()
        if len(parts) < 7:  # class_id + at least 3 xy points
            continue
        try:
            class_id = int(float(parts[0]))
            coords = np.asarray(parts[1:], dtype=np.float32)
        except ValueError:
            logger.warning("skipping malformed annotation line: %s", line[:60])
            continue
        if len(coords) % 2 != 0:
            coords = coords[:-1]
        polygon = np.clip(coords.reshape(-1, 2), 0.0, 1.0) * tensor_size
        found_polygons.append((class_id, polygon))
    return found_polygons


def build_target_from_polygons(found_polygons, tensor_size=TENSOR_SIZE):
    """
    One stored annotation on tallennettu (= one ground truth image) -> josta tulee sitten one torchmetrics target dict.
    boxes (xyxy) are the min/max of the polygon, masks are the polygon rasterised with cv2.fillPoly.
    """
    if len(found_polygons) == 0:
        return None

    target_masks = []
    target_boxes = []
    target_labels = []
    for class_id, polygon in found_polygons:
        mask = np.zeros((tensor_size, tensor_size), dtype=np.uint8)
        cv2.fillPoly(mask, [np.round(polygon).astype(np.int32)], 1)
        x1, y1 = polygon.min(axis=0)
        x2, y2 = polygon.max(axis=0)
        target_masks.append(mask.astype(bool))
        target_boxes.append([x1, y1, x2, y2])
        target_labels.append(class_id)

    return dict(
        boxes=torch.as_tensor(np.asarray(target_boxes, dtype=np.float32)),
        masks=torch.from_numpy(np.stack(target_masks)),  # bool (N, 512, 512)
        labels=torch.as_tensor(np.asarray(target_labels, dtype=np.int64)),
    )


def _to_python_float(value):
    # torchmetrics returns -1 when there was nothing to evaluate (no preds and/or no targets)
    number = float(value)
    return None if number < 0 else round(number, 4)


def calculate_map_per_image(preds, target):
    results = {}
    for iou_type in ("bbox", "segm"):
        metric = MeanAveragePrecision(box_format="xyxy", iou_type=iou_type, class_metrics=True)
        metric.update(preds, target)
        computed = metric.compute()
        results[iou_type] = {key: _to_python_float(computed[key]) for key in MAP_KEYS_TO_KEEP}
    return results


def _mean_ignoring_none(values):
    valid = [v for v in values if v is not None]
    return round(sum(valid) / len(valid), 4) if valid else None


def calculate_proxy_map_metrics(preds, listof_proxy_camera_results, tensor_size=TENSOR_SIZE):
    per_reference_results = []
    regional_class_counts = {}

    for camera_id, distance_km, is_same_camera, annotation_rows in listof_proxy_camera_results:
        print("in codeblock, calculate_proxy_map_metrics")
        print("camera_id, distance_km, is_same_camera")
        print(camera_id, distance_km, is_same_camera)
        print("and ann_rows", type(annotation_rows))
        print("length of listof_proxy_camera_results ", len(listof_proxy_camera_results))
        print(annotation_rows)
        print("len of annotation_rows", len(annotation_rows))
        #for annotation_id,image_url_full, updated_at, annotation_text in annotation_rows:
        if annotation_rows:
            annotation_id = annotation_rows[0]
            image_url_full = annotation_rows[1]
            updated_at = annotation_rows[2]
            annotation_text = annotation_rows[3]
            print("then next for contains: annotation_id, image_url_full, updated_at, annotation_text")
            print(annotation_id, image_url_full ,updated_at)
            print("type of annotation text ", type(annotation_text))
            print("")
            if isinstance(annotation_text, list):
                annotation_text = "\n".join(annotation_text)
            found_polygons = parse_yolo_seg_annotation_text(annotation_text, tensor_size)
            if len(found_polygons) == 0:
                continue

            for class_id, _ in found_polygons:
                regional_class_counts[class_id] = regional_class_counts.get(class_id, 0) + 1

            if is_same_camera:
                target = [build_target_from_polygons(found_polygons, tensor_size)]
                per_reference_results.append({
                    "annotation_id": annotation_id,
                    "updated_at": str(updated_at),
                    **calculate_map_per_image(preds, target),
                })

    total_regional_annotations = sum(regional_class_counts.values())
    regional_class_share = {
        names.get(class_id, str(class_id)): round(count / total_regional_annotations, 4)
        for class_id, count in sorted(regional_class_counts.items())
    } if total_regional_annotations > 0 else {}

    summary = {
        "same_camera_found": len(per_reference_results) > 0,
        "reference_count": len(per_reference_results),
        "per_reference": per_reference_results,
        "regional_class_share": regional_class_share,
        "regional_annotation_count": total_regional_annotations,

    }
    for iou_type in ("bbox", "segm"):
        summary[iou_type] = {
            key: _mean_ignoring_none([r[iou_type][key] for r in per_reference_results])
            for key in MAP_KEYS_TO_KEEP
        } if per_reference_results else None
    return summary
