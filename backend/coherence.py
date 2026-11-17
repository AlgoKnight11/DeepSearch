import numpy as np
import scipy.signal

class CoherenceEngine:
    """
    Measures spatial and spectral coherence across multiple facial ROIs.
    Real human faces exhibit phase-locked cardiac pulses that rise and fall
    in biological harmony. Deepfakes exhibit scattered frequencies and phase drift.
    """

    def __init__(self, fps=30.0, roi_keys=None):
        self.fps = fps
        self.roi_keys = roi_keys or ['forehead', 'lcheek', 'rcheek', 'chin']

    def compute_coherence_matrix(self, roi_signals):
        """
        Calculates a 4x4 cross-correlation / coherence matrix between all pairs of ROIs.
        roi_signals: dict where keys are roi_names and values are 1D arrays of filtered rPPG signals.
        Returns:
            matrix (4x4 np.ndarray): Pairwise coherence coefficients [0.0 - 1.0]
            avg_coherence (float): Mean off-diagonal coherence index
        """
        n = len(self.roi_keys)
        matrix = np.eye(n, dtype=np.float32)

        for i in range(n):
            key_i = self.roi_keys[i]
            sig_i = roi_signals.get(key_i, np.zeros(10))

            for j in range(i + 1, n):
                key_j = self.roi_keys[j]
                sig_j = roi_signals.get(key_j, np.zeros(10))

                val = self._pair_coherence(sig_i, sig_j)
                matrix[i, j] = val
                matrix[j, i] = val

        # Calculate average off-diagonal coherence
        off_diagonals = []
        for i in range(n):
            for j in range(n):
                if i != j:
                    off_diagonals.append(matrix[i, j])

        avg_coherence = float(np.mean(off_diagonals)) if len(off_diagonals) > 0 else 0.0
        return matrix, avg_coherence

    def _pair_coherence(self, sig1, sig2):
        """Computes magnitude-squared coherence in the cardiac band (0.7 - 3.0 Hz)."""
        if len(sig1) < 20 or len(sig2) < 20:
            return 0.5

        # Standardize signals
        s1 = (sig1 - np.mean(sig1)) / (np.std(sig1) + 1e-6)
        s2 = (sig2 - np.mean(sig2)) / (np.std(sig2) + 1e-6)

        # Welch's Magnitude-Squared Coherence
        f, cxy = scipy.signal.coherence(s1, s2, fs=self.fps, nperseg=min(len(s1), int(self.fps * 2)))

        # Average coherence within cardiac frequency band [0.7, 3.0 Hz]
        cardiac_mask = (f >= 0.7) & (f <= 3.0)
        if np.any(cardiac_mask):
            cardiac_coherence = float(np.mean(cxy[cardiac_mask]))
        else:
            cardiac_coherence = float(np.mean(cxy))

        # Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, cardiac_coherence))

    def extract_feature_vector(self, roi_signals):
        """
        Constructs a tabular feature vector from a time window for classifier training:
        - Pairwise coherence metrics (6 unique pairs)
        - Mean and standard deviation of coherence
        - Inter-patch phase lag discrepancies
        """
        matrix, avg_coherence = self.compute_coherence_matrix(roi_signals)
        unique_pairs = []
        for i in range(len(self.roi_keys)):
            for j in range(i + 1, len(self.roi_keys)):
                unique_pairs.append(matrix[i, j])

        features = [
            *unique_pairs,                         # 6 pairwise coherence values
            avg_coherence,                         # Mean cross-ROI coherence
            float(np.std(unique_pairs)),           # Coherence variance
            float(np.min(unique_pairs)),           # Minimum pairwise coherence
            float(np.max(unique_pairs))            # Maximum pairwise coherence
        ]
        return np.array(features, dtype=np.float32)
