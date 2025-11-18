from ultralytics import YOLO
import cv2
import base64
import numpy as np
from ultralytics.utils.plotting import Annotator
import os
import torch
import time

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
try:
    torch.cuda.set_per_process_memory_fraction(0.6, 0)
except Exception as e:
    print(e)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'weights/best.pt')

def getYoloModel():
    """
    Load YOLO model for inference only.
    Uses FP16 on GPU for faster predictions.
    """
    model = YOLO(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    # Optional fuse (skip if triggers dataset loading)
    try:
        model.fuse()
    except Exception as e:
        print(f"[WARN] fuse() skipped: {e}")

    model.to(device)
    # Use FP16 on GPU
    if device.type == "cuda":
        try:
            model.model.half()
            print("[INFO] Model using FP16 for faster GPU inference.")
        except Exception as e:
            print(f"[WARN] FP16 failed: {e}")

    return model


def extract_digits(test_model, bigfile, conf, imgflg=False, cropped=False, y_tol=20):
    """
    Detect digits/objects from an image using YOLOv8.
    Center for ordering is computed from the diagonal midpoint of each box:
      center_x = (x_min + x_max) / 2
      center_y = (y_min + y_max) / 2
    Filters detections to the dominant horizontal row using y_tol (pixels),
    then selects the best detection per (rounded) column and orders left-to-right.

    Returns: (digits_str, optional base64 annotated image, optional base64 crop)
    """
    t0 = time.time()
    img = cv2.imread(bigfile, cv2.IMREAD_COLOR)
    if img is None:
        print(f"[ERROR] Failed to read image: {bigfile}")
        return '', '', ''

    annotator = Annotator(img) if imgflg else None
    test_model.conf = conf

    device_str = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        with torch.no_grad():
            r = test_model.predict(
                source=img,
                device=device_str,
                show_conf=True,
                save=False,
                save_crop=False,
                exist_ok=True,
                verbose=False,
                iou=.5,
                agnostic_nms=True
            )[0]

        if device_str.startswith("cuda"):
            torch.cuda.synchronize()

        boxes = r.boxes
        if boxes is None or len(boxes) == 0:
            print("[WARNING] No boxes found.")
            return '', '', ''

        # --- Apply confidence threshold filter ---
        conf_mask = boxes.conf.cpu().numpy() >= conf
        if not np.any(conf_mask):
            print(f"[INFO] No boxes >= conf {conf}")
            return '', '',

            # --- vectorized processing ----------------------------------
        xyxy = boxes.xyxy[conf_mask].cpu().numpy()   # shape (N,4): x_min, y_min, x_max, y_max
        confs = boxes.conf[conf_mask].cpu().numpy()
        clses = boxes.cls[conf_mask].cpu().numpy().astype(int)

        centers_x = (xyxy[:, 0] + xyxy[:, 2]) / 2.0
        centers_y = (xyxy[:, 1] + xyxy[:, 3]) / 2.0

        N = len(centers_x)
        if N == 0:
            return '', '', ''

        # --- group detections into horizontal rows using y_tol and pick largest row ---
        order_by_y = np.argsort(centers_y)
        groups = []
        current_group = [order_by_y[0]]
        for idx in order_by_y[1:]:
            if abs(centers_y[idx] - centers_y[current_group[-1]]) <= y_tol:
                current_group.append(idx)
            else:
                groups.append(current_group)
                current_group = [idx]
        groups.append(current_group)

        # pick the group (row) with the largest number of members
        best_row = max(groups, key=lambda g: len(g))
        row_idxs = np.array(best_row, dtype=int)

        # --- within chosen row, group by rounded x to remove duplicates in same column ---
        xs_int = np.round(centers_x).astype(int)
        xs_row = xs_int[row_idxs]
        unique_xs = np.unique(xs_row)
        keep_indices_row = []
        for ux in unique_xs:
            idxs = row_idxs[np.where(xs_row == ux)[0]]
            # pick the detection with highest confidence for this x column
            best_local = idxs[np.argmax(confs[idxs])]
            keep_indices_row.append(best_local)
        keep_indices_row = np.array(keep_indices_row, dtype=int)

        # Sort kept indices by exact diagonal center-x ascending (left-to-right)
        keep_indices_row = keep_indices_row[np.argsort(centers_x[keep_indices_row])]

        if keep_indices_row.size == 0:
            return '', '', ''

        # Selected class indices in left-to-right order
        selected = clses[keep_indices_row].astype(int)

        # safety check
        if selected.size and selected.max() >= len(test_model.names):
            print("DEBUG: selected class indices:", selected)
            print("DEBUG: available names:", test_model.names)
            raise ValueError(
                f"Class index {int(selected.max())} out of range for test_model.names (len={len(test_model.names)})."
            )

        # map to names
        digits_str = ''.join(test_model.names[c] for c in selected)

        # --- optional annotated image --------------------------------
        base64_image = ''
        if imgflg and annotator is not None:
            for idx in keep_indices_row:
                b = boxes[int(idx)]
                # Annotator.box_label expects xyxy, label; b.xyxy might be tensor shape (1,4)
                annotator.box_label(b.xyxy[0].tolist(), test_model.names[int(b.cls)])
            _, buf = cv2.imencode('.jpg', annotator.result())
            base64_image = base64.b64encode(buf).decode()

        # --- optional crop ------------------------------------------
        cb64 = ''
        if cropped:
            # compute bounding box just for the detections in the chosen row (more focused crop)
            x_min = xyxy[row_idxs, 0].min()
            y_min = xyxy[row_idxs, 1].min()
            x_max = xyxy[row_idxs, 2].max()
            y_max = xyxy[row_idxs, 3].max()
            y_min = 0 if y_min < 20 else y_min - 20

            crop = img[int(y_min):int(y_max), int(x_min):int(x_max)]
            if crop.size:
                _, buf = cv2.imencode('.jpg', crop)
                cb64 = base64.b64encode(buf).decode()

        print(f'Extraction in: {(time.time() - t0) * 1000:.2f} ms (kept {len(keep_indices_row)} boxes from row of {len(row_idxs)})')
        return digits_str, base64_image, cb64

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        print(traceback.format_exc())
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return '', '', ''

