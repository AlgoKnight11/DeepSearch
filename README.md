# DeepSearch: Biological rPPG Deepfake Recognition

DeepSearch is an AI-powered video forensics system that detects deepfakes by reading involuntary human cardiovascular physiology (Remote Photoplethysmography — rPPG) across multiple facial regions.

While modern generative models (Diffusion, GANs, FaceSwappers) eliminate pixel-level visual artifacts, they fail to synthesize phase-locked, biologically coherent pulse waves across anatomical facial regions. DeepSearch captures cross-ROI spatial coherence to separate authentic human physiology from synthetic video.

---

## 📸 User Interface (Cyber Security Forensics Dashboard)

Built with **HTML5, CSS3, and JavaScript** (Chart.js + Canvas API):
- **Panel 1 (Video Input & ROIs):** Drag-and-drop video upload, live webcam streaming, and a high-framerate `<canvas>` drawing the 3D Face Mesh and color-coded ROI boxes (`Forehead`, `Left Cheek`, `Right Cheek`, `Chin`).
- **Panel 2 (Physiological Signal Workbench):** Real-time multi-trace rPPG blood volume pulse waveforms synchronized with an FFT Power Spectral Density chart (dominant BPM and SNR meters).
- **Panel 3 (Forensic Verdict):** 94% circular probability gauge, 4×4 spatial cross-correlation matrix (`AVG: 0.93`), 5-second slice temporal voting timeline, and one-click PDF forensic certificate export.

---

## 🚀 Quick Start

### 1. Launch the Application
Run the one-click launcher:
```bash
python start_app.py
```
This automatically starts the FastAPI server and opens `http://127.0.0.1:8000` in your default browser.

---

## 🛠️ System Architecture & Modules

```
DeepSearch- Deepfake Recognition/
├── frontend/
│   ├── index.html              # 3-Panel Forensic Command Center
│   ├── css/
│   │   └── styles.css          # Dark Cybersecurity UI theme, glowing states & layout
│   └── js/
│       ├── app.js              # State manager, event listeners, and presets
│       ├── video_overlay.js    # Canvas rendering for Face Mesh & ROI polygons
│       └── charts.js           # Chart.js configs for rPPG waves & FFT spectrum
│
├── backend/
│   ├── server.py               # FastAPI application, static file serving & WebSockets
│   ├── tracker.py              # MediaPipe 478 3D landmarks + OpenCV fallback
│   ├── roi_extractor.py        # Spatial averaging for Forehead, Cheeks, and Chin
│   ├── rppg_filter.py          # Detrending, Butterworth bandpass (0.7-3.0 Hz), CHROM & POS
│   ├── coherence.py            # Pairwise Magnitude-Squared Coherence & Cross-Correlation
│   ├── classifier.py           # Window-based SVM / Random Forest & Temporal Voting
│   └── video_processor.py      # End-to-end video analysis orchestrator
│
├── samples/                    # Test clips and forensic video samples
├── start_app.py                # Single-command launcher
└── DeepSearch_Deepfake_Detection_System_Specification.pdf
```

---

## 🔬 Core Algorithms
1. **Remote Photoplethysmography (rPPG):** Measures micro-fluctuations in facial skin light reflectance caused by arterial blood pulsation.
2. **Chrominance-Based Signal Extraction (CHROM & POS):** Removes specular reflections, motion drift, and illumination noise by projecting RGB temporal channels onto skin-orthogonal planes.
3. **Multi-Patch Spatial Coherence:** Real human faces pulse in phase-locked biological synchrony across all 4 facial regions. Synthetic media exhibits spatial incoherence or erratic frequency clashing.
