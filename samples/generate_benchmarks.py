import cv2
import numpy as np
import os

os.makedirs('samples', exist_ok=True)

def generate_benchmark_videos():
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    # 1. Authentic Human Video: All face patches pulse in biological phase synchrony at 1.2 Hz (72 BPM)
    auth_path = 'samples/sample_authentic.mp4'
    out_auth = cv2.VideoWriter(auth_path, fourcc, 30.0, (640, 480))
    
    for f in range(180): # 6 seconds
        t = f / 30.0
        frame = np.full((480, 640, 3), (25, 20, 15), dtype=np.uint8)
        
        # Synchronous biological cardiac wave
        cardiac_wave = np.sin(2 * np.pi * 1.2 * t)
        
        # Base skin tone with synchronized capillary absorption (predominantly in Green & Red)
        b = int(120 + cardiac_wave * 1.5)
        g = int(145 + cardiac_wave * 4.0) # Hemoglobin absorption
        r = int(190 + cardiac_wave * 2.5)
        
        # Draw face oval
        cv2.ellipse(frame, (320, 240), (130, 170), 0, 0, 360, (b, g, r), -1)
        # Facial features
        cv2.circle(frame, (275, 210), 12, (40, 35, 30), -1)
        cv2.circle(frame, (365, 210), 12, (40, 35, 30), -1)
        cv2.ellipse(frame, (320, 320), (35, 12), 0, 0, 360, (60, 50, 80), -1)
        out_auth.write(frame)
    out_auth.release()
    print("Created authentic sample:", auth_path)

    # 2. Deepfake Video: Spatial incoherence - Forehead has donor wave (1.1 Hz), Cheeks have artifact noise (2.2 Hz), Chin has flat/clashing signal
    fake_path = 'samples/sample_deepfake.mp4'
    out_fake = cv2.VideoWriter(fake_path, fourcc, 30.0, (640, 480))
    
    for f in range(180):
        t = f / 30.0
        frame = np.full((480, 640, 3), (25, 20, 15), dtype=np.uint8)
        
        # Base face oval
        cv2.ellipse(frame, (320, 240), (130, 170), 0, 0, 360, (120, 145, 190), -1)
        
        # Disjoint, conflicting signals across face patches
        forehead_pulse = np.sin(2 * np.pi * 1.05 * t)
        lcheek_pulse = np.sin(2 * np.pi * 2.3 * t + 1.5) # Clashing frequency
        rcheek_pulse = np.sin(2 * np.pi * 1.7 * t + 3.0) # Chaotic phase
        chin_noise = (np.random.rand() - 0.5) * 6.0       # Synthesis jitter
        
        # Forehead patch (y: 110-180, x: 250-390)
        fb = int(120 + forehead_pulse * 1.5)
        fg = int(145 + forehead_pulse * 4.0)
        fr = int(190 + forehead_pulse * 2.5)
        cv2.ellipse(frame, (320, 150), (60, 35), 0, 0, 360, (fb, fg, fr), -1)
        
        # Left cheek patch
        lcb = int(120 + lcheek_pulse * 1.8)
        lcg = int(145 + lcheek_pulse * 4.5)
        lcr = int(190 + lcheek_pulse * 2.8)
        cv2.circle(frame, (260, 260), 32, (lcb, lcg, lcr), -1)

        # Right cheek patch
        rcb = int(120 + rcheek_pulse * 1.8)
        rcg = int(145 + rcheek_pulse * 4.5)
        rcr = int(190 + rcheek_pulse * 2.8)
        cv2.circle(frame, (380, 260), 32, (rcb, rcg, rcr), -1)

        # Chin patch
        cb = int(np.clip(120 + chin_noise, 0, 255))
        cg = int(np.clip(145 + chin_noise * 1.5, 0, 255))
        cr = int(np.clip(190 + chin_noise, 0, 255))
        cv2.ellipse(frame, (320, 360), (40, 25), 0, 0, 360, (cb, cg, cr), -1)

        # Facial features
        cv2.circle(frame, (275, 210), 12, (40, 35, 30), -1)
        cv2.circle(frame, (365, 210), 12, (40, 35, 30), -1)
        cv2.ellipse(frame, (320, 320), (35, 12), 0, 0, 360, (60, 50, 80), -1)

        out_fake.write(frame)
    out_fake.release()
    print("Created deepfake sample:", fake_path)

if __name__ == '__main__':
    generate_benchmark_videos()
