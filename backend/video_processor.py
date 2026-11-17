import cv2
import numpy as np
from backend.tracker import FaceTracker
from backend.roi_extractor import ROIExtractor
from backend.rppg_filter import RPPGFilter
from backend.coherence import CoherenceEngine
from backend.classifier import ForensicsClassifier

class VideoProcessor:
    """
    End-to-end forensic analysis pipeline:
    Orchestrates face tracking, ROI extraction, physiological filtering,
    coherence matrix computation, and deepfake verdict classification.
    """

    def __init__(self, fps=30.0, method='CHROM', bandpass_range=(0.7, 3.0)):
        self.fps = fps
        self.method = method
        self.tracker = FaceTracker()
        self.roi_extractor = ROIExtractor()
        self.rppg_filter = RPPGFilter(fps=fps, low_hz=bandpass_range[0], high_hz=bandpass_range[1])
        self.coherence_engine = CoherenceEngine(fps=fps)
        self.classifier = ForensicsClassifier()

    def analyze_video(self, video_path, max_frames=300):
        """
        Analyzes a video file up to max_frames (e.g. 10 seconds @ 30 FPS).
        Returns a complete forensic report dictionary.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        real_fps = cap.get(cv2.CAP_PROP_FPS)
        if real_fps > 5 and real_fps < 120:
            self.fps = real_fps
            self.rppg_filter.fps = real_fps
            self.coherence_engine.fps = real_fps

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        raw_rois = {'forehead': [], 'lcheek': [], 'rcheek': [], 'chin': []}
        frames_processed = 0

        while cap.isOpened() and frames_processed < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frames_processed += 1
            has_face, face_box, landmarks = self.tracker.detect(frame)

            if has_face:
                if len(landmarks) >= 468:
                    rgb_vals = self.roi_extractor.extract_from_landmarks(frame, landmarks)
                else:
                    rgb_vals = self.roi_extractor.extract_fallback_box(frame, face_box)

                for k in raw_rois:
                    raw_rois[k].append(rgb_vals[k])
            else:
                for k in raw_rois:
                    raw_rois[k].append(np.array([128.0, 128.0, 128.0]))

        cap.release()

        # Convert to arrays and extract rPPG signals
        filtered_signals = {}
        for k in raw_rois:
            arr = np.array(raw_rois[k], dtype=np.float32)
            if self.method == 'CHROM':
                sig = self.rppg_filter.extract_chrom(arr)
            elif self.method == 'POS':
                sig = self.rppg_filter.extract_pos(arr)
            else:
                sig = self.rppg_filter.extract_green(arr)
            filtered_signals[k] = sig

        # Frequency Domain Analysis (using Forehead as primary carrier)
        forehead_sig = filtered_signals['forehead']
        bpm, peak_freq, snr_db, freqs, fft_vals = self.rppg_filter.estimate_hr_fft(forehead_sig)

        # Spatio-Temporal Coherence Matrix
        matrix, avg_coherence = self.coherence_engine.compute_coherence_matrix(filtered_signals)

        # Temporal Window Slices (e.g., 5-second windows)
        slice_len = int(self.fps * 5)
        window_probs = []
        n_samples = len(forehead_sig)

        for start in range(0, max(1, n_samples - slice_len + 1), slice_len // 2):
            end = min(n_samples, start + slice_len)
            sub_sigs = {k: filtered_signals[k][start:end] for k in filtered_signals}
            f_vec = self.coherence_engine.extract_feature_vector(sub_sigs)
            _, prob = self.classifier.classify_window(f_vec)
            window_probs.append(prob)

        if not window_probs:
            full_f_vec = self.coherence_engine.extract_feature_vector(filtered_signals)
            _, prob = self.classifier.classify_window(full_f_vec)
            window_probs = [prob]

        # Aggregate Verdict
        verdict, confidence, slices, real_votes, total_slices = self.classifier.aggregate_temporal_voting(window_probs)

        # Format 4x4 matrix for UI table
        matrix_formatted = [
            [f"{matrix[r, c]:.2f}" for c in range(4)]
            for r in range(4)
        ]

        return {
            "status": "success",
            "video_metadata": {
                "width": width,
                "height": height,
                "fps": float(self.fps),
                "total_frames": total_frames,
                "frames_analyzed": frames_processed
            },
            "cardiac_telemetry": {
                "detected_bpm": round(bpm, 1),
                "peak_frequency_hz": round(peak_freq, 2),
                "snr_db": round(snr_db, 1)
            },
            "coherence": {
                "average_coherence": round(avg_coherence, 2),
                "matrix_4x4": matrix_formatted
            },
            "verdict": {
                "label": verdict,
                "confidence_percent": round(confidence * 100, 1),
                "real_slices": real_votes,
                "total_slices": total_slices,
                "slice_breakdown": slices
            }
        }
