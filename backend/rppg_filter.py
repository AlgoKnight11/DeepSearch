import numpy as np
import scipy.signal

class RPPGFilter:
    """
    Physiological signal conditioning:
    Detrending, Butterworth bandpass filtering, CHROM/POS color transformations,
    and Fast Fourier Transform (FFT) cardiac frequency estimation.
    """

    def __init__(self, fps=30.0, low_hz=0.7, high_hz=3.0, order=4):
        self.fps = fps
        self.low_hz = low_hz
        self.high_hz = high_hz
        self.order = order

        # Precompute Butterworth SOS filter coefficients
        nyq = 0.5 * self.fps
        low = self.low_hz / nyq
        high = self.high_hz / nyq
        self.sos = scipy.signal.butter(self.order, [low, high], btype='bandpass', output='sos')

    def bandpass_filter(self, signal):
        """Applies zero-phase digital bandpass filtering."""
        if len(signal) < 18:
            return signal
        # Linear detrending first to eliminate baseline wander
        detrended = scipy.signal.detrend(signal)
        # Zero-phase SOS filter
        filtered = scipy.signal.sosfiltfilt(self.sos, detrended)
        return filtered

    def extract_chrom(self, rgb_series):
        """
        CHROM (Chrominance-based method - de Haan & Jeanne 2013).
        rgb_series: array of shape (N, 3) where columns are [R, G, B].
        """
        if len(rgb_series) < 10:
            return np.zeros(len(rgb_series))

        R = rgb_series[:, 0]
        G = rgb_series[:, 1]
        B = rgb_series[:, 2]

        # Normalization
        Rn = R / (np.mean(R) + 1e-6)
        Gn = G / (np.mean(G) + 1e-6)
        Bn = B / (np.mean(B) + 1e-6)

        # Chrominance orthogonal vectors
        Xs = 3.0 * Rn - 2.0 * Gn
        Ys = 1.5 * Rn + Gn - 1.5 * Bn

        # Bandpass filter both components
        Xf = self.bandpass_filter(Xs)
        Yf = self.bandpass_filter(Ys)

        # Standard deviation ratio
        std_X = np.std(Xf)
        std_Y = np.std(Yf)
        alpha = std_X / (std_Y + 1e-6)

        # Combine
        S = Xf - alpha * Yf
        return self.bandpass_filter(S)

    def extract_pos(self, rgb_series):
        """
        POS (Plane-Orthogonal-to-Skin - Wang et al. 2017).
        rgb_series: array of shape (N, 3) where columns are [R, G, B].
        """
        N = len(rgb_series)
        if N < 15:
            return np.zeros(N)

        # Projection matrix
        H = np.zeros(N)
        l = int(self.fps * 1.6) # window size ~1.6 sec
        if l < 6:
            l = 6

        for n in range(N - l + 1):
            m = rgb_series[n:n + l, :]
            # Temporal mean per channel in window
            mean_c = np.mean(m, axis=0) + 1e-6
            m_norm = m / mean_c

            # Plane projection
            S1 = m_norm[:, 1] - m_norm[:, 0]
            S2 = m_norm[:, 1] + m_norm[:, 0] - 2.0 * m_norm[:, 2]

            std_s1 = np.std(S1)
            std_s2 = np.std(S2)
            alpha = std_s1 / (std_s2 + 1e-6)

            h = S1 + alpha * S2
            H[n:n + l] += h - np.mean(h)

        return self.bandpass_filter(H)

    def extract_green(self, rgb_series):
        """Simple normalized green channel baseline."""
        G = rgb_series[:, 1]
        mean_g = np.mean(G) + 1e-6
        norm_g = (G - mean_g) / mean_g
        return self.bandpass_filter(norm_g)

    def estimate_hr_fft(self, signal):
        """
        Computes dominant heart rate frequency, BPM, and cardiac SNR (in dB).
        """
        N = len(signal)
        if N < 30:
            return 72.0, 1.2, 10.0, np.zeros(10), np.zeros(10)

        # Fast Fourier Transform
        freqs = np.fft.rfftfreq(N, d=1.0 / self.fps)
        fft_vals = np.abs(np.fft.rfft(signal))

        # Restrict to physiological cardiac range [0.7 Hz, 3.0 Hz]
        cardiac_mask = (freqs >= self.low_hz) & (freqs <= self.high_hz)
        if not np.any(cardiac_mask):
            return 72.0, 1.2, 10.0, freqs, fft_vals

        cardiac_freqs = freqs[cardiac_mask]
        cardiac_fft = fft_vals[cardiac_mask]

        peak_idx = np.argmax(cardiac_fft)
        peak_freq = cardiac_freqs[peak_idx]
        bpm = float(peak_freq * 60.0)

        # Estimate Signal-to-Noise Ratio (SNR) in dB
        peak_power = float(cardiac_fft[peak_idx] ** 2)
        total_cardiac_power = float(np.sum(cardiac_fft ** 2))
        noise_power = max(1e-6, total_cardiac_power - peak_power)
        snr_db = float(10.0 * np.log10((peak_power + 1e-6) / noise_power))

        return bpm, peak_freq, snr_db, freqs, fft_vals
