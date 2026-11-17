import numpy as np
import cv2

class ROIExtractor:
    """
    Extracts 4 anatomical facial Regions of Interest (ROIs):
    1. Forehead
    2. Left Cheek
    3. Right Cheek
    4. Chin
    Computes spatial RGB mean intensity per region per frame.
    """

    # Canonical MediaPipe landmark indices for ROIs
    FOREHEAD_LANDMARKS = [10, 67, 109, 297, 338, 9, 8]
    LCHEEK_LANDMARKS   = [117, 118, 100, 126, 205, 50, 123]
    RCHEEK_LANDMARKS   = [346, 347, 329, 355, 425, 280, 352]
    CHIN_LANDMARKS     = [152, 175, 199, 200, 396, 176, 148]

    def __init__(self):
        self.roi_keys = ['forehead', 'lcheek', 'rcheek', 'chin']

    def extract_from_landmarks(self, frame, landmarks_px):
        """
        Given an RGB frame and 478 landmark coordinates (x, y) in pixels,
        returns a dictionary with spatial mean RGB values for each ROI.
        """
        h, w, _ = frame.shape
        rgb_means = {}

        rois_dict = {
            'forehead': self.FOREHEAD_LANDMARKS,
            'lcheek': self.LCHEEK_LANDMARKS,
            'rcheek': self.RCHEEK_LANDMARKS,
            'chin': self.CHIN_LANDMARKS
        }

        for roi_name, indices in rois_dict.items():
            pts = np.array([landmarks_px[i] for i in indices if i < len(landmarks_px)], dtype=np.int32)
            if len(pts) < 3:
                # Fallback to zero
                rgb_means[roi_name] = np.array([0.0, 0.0, 0.0])
                continue

            # Compute bounding box with safe padding
            min_x = max(0, int(np.min(pts[:, 0])))
            max_x = min(w, int(np.max(pts[:, 0])))
            min_y = max(0, int(np.min(pts[:, 1])))
            max_y = min(h, int(np.max(pts[:, 1])))

            if max_x <= min_x or max_y <= min_y:
                rgb_means[roi_name] = np.array([0.0, 0.0, 0.0])
                continue

            patch = frame[min_y:max_y, min_x:max_x]
            # Mean RGB across the patch
            mean_rgb = np.mean(patch, axis=(0, 1))
            rgb_means[roi_name] = mean_rgb

        return rgb_means

    def extract_fallback_box(self, frame, face_box):
        """
        Fallback when dense landmarks are unavailable:
        Approximates ROIs from face bounding box [x, y, w, h].
        """
        fx, fy, fw, fh = face_box
        rois = {
            'forehead': (int(fx + fw * 0.25), int(fy + fh * 0.08), int(fw * 0.5), int(fh * 0.18)),
            'lcheek':   (int(fx + fw * 0.12), int(fy + fh * 0.45), int(fw * 0.25), int(fh * 0.2)),
            'rcheek':   (int(fx + fw * 0.63), int(fy + fh * 0.45), int(fw * 0.25), int(fh * 0.2)),
            'chin':     (int(fx + fw * 0.35), int(fy + fh * 0.76), int(fw * 0.3),  int(fh * 0.15))
        }

        h, w, _ = frame.shape
        rgb_means = {}
        for name, (rx, ry, rw, rh) in rois.items():
            rx1 = max(0, min(w, rx))
            rx2 = max(0, min(w, rx + rw))
            ry1 = max(0, min(h, ry))
            ry2 = max(0, min(h, ry + rh))

            if rx2 <= rx1 or ry2 <= ry1:
                rgb_means[name] = np.array([0.0, 0.0, 0.0])
            else:
                patch = frame[ry1:ry2, rx1:rx2]
                rgb_means[name] = np.mean(patch, axis=(0, 1))

        return rgb_means
