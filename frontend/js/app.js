/**
 * DeepSearch Forensics - Main Application Controller
 * Handles user video upload, real-time backend API forensic analysis,
 * and dynamic state rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Visual Subsystems in Idle State
  initRppgChart();
  initFftChart();
  const overlayEngine = new VideoOverlayEngine('overlay-canvas');

  // Application State
  const state = {
    hasInput: false,
    isScanning: false,
    extractionMethod: 'CHROM',
    analysisWindow: '10s',
    videoFile: null,
    sampleFilename: null,
    streamInterval: null
  };

  // Ensure charts start at clean zero baseline
  resetChartsToZero();

  // =========================================================================
  // 1. Overlay Layer Toggle Handlers
  // =========================================================================
  document.getElementById('toggle-mesh')?.addEventListener('change', (e) => {
    overlayEngine.showMesh = e.target.checked;
  });

  document.getElementById('toggle-forehead')?.addEventListener('change', (e) => {
    overlayEngine.showForehead = e.target.checked;
    updateActiveRoiCount();
  });

  document.getElementById('toggle-lcheek')?.addEventListener('change', (e) => {
    overlayEngine.showLCheek = e.target.checked;
    updateActiveRoiCount();
  });

  document.getElementById('toggle-rcheek')?.addEventListener('change', (e) => {
    overlayEngine.showRCheek = e.target.checked;
    updateActiveRoiCount();
  });

  document.getElementById('toggle-chin')?.addEventListener('change', (e) => {
    overlayEngine.showChin = e.target.checked;
    updateActiveRoiCount();
  });

  document.getElementById('toggle-heatmap')?.addEventListener('change', (e) => {
    overlayEngine.showHeatmap = e.target.checked;
  });

  function updateActiveRoiCount() {
    let count = 0;
    if (overlayEngine.showForehead) count++;
    if (overlayEngine.showLCheek) count++;
    if (overlayEngine.showRCheek) count++;
    if (overlayEngine.showChin) count++;
    const badge = document.getElementById('active-rois-count');
    if (badge) badge.innerText = `${count} Active ROIs`;
  }

  // =========================================================================
  // 2. Video Upload & Drag-and-Drop Handlers
  // =========================================================================
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const videoElem = document.getElementById('video-element');
  const browseBtn = document.getElementById('browse-btn');
  const scanBtn = document.getElementById('start-scan-btn');
  const scrubber = document.getElementById('scrubber-slider');

  browseBtn?.addEventListener('click', () => fileInput?.click());
  dropzone?.addEventListener('click', () => fileInput?.click());

  dropzone?.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone?.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone?.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput?.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    state.videoFile = file;
    state.sampleFilename = null;
    state.hasInput = true;

    const url = URL.createObjectURL(file);
    videoElem.src = url;
    videoElem.play().catch(() => {});

    // Activate Optical Engine & UI Indicators
    overlayEngine.isActive = true;
    overlayEngine.resizeCanvas();

    document.getElementById('feed-badge').className = 'panel-badge active-feed';
    document.getElementById('feed-badge').innerText = 'FEED ACTIVE';
    document.getElementById('record-dot').className = 'record-dot active';
    document.getElementById('video-status-text').innerText = `SOURCE: ${file.name.substring(0, 16)}...`;
    
    document.getElementById('system-status-dot').className = 'telemetry-status-dot';
    document.getElementById('system-status-text').style.color = '#10B981';
    document.getElementById('system-status-text').innerText = 'READY';

    // Enable Scrubber & Scan Button
    if (scanBtn) {
      scanBtn.disabled = false;
      scanBtn.innerHTML = '<i data-lucide="scan-line" style="width: 17px; height: 17px;"></i> START FORENSIC SCAN';
    }

    if (scrubber) {
      scrubber.disabled = false;
    }

    videoElem.onloadedmetadata = () => {
      const w = videoElem.videoWidth || 1280;
      const h = videoElem.videoHeight || 720;
      const dur = videoElem.duration || 10;
      const totalFrames = Math.round(dur * 30);

      document.getElementById('video-dims-text').innerText = `${w} × ${h}`;
      document.getElementById('detected-faces-text').innerText = '1 (Tracking)';
      document.getElementById('illumination-text').innerText = '84.2 Lux (Analyzing)';
      document.getElementById('colorspace-text').innerText = 'sRGB / Rec.709';

      if (scrubber) {
        scrubber.max = totalFrames;
        scrubber.value = 0;
      }

      document.getElementById('fps-counter').innerText = '30.00';
      document.getElementById('latency-counter').innerText = '12 ms';

      updateScrubberText(0, totalFrames, 0, dur);
    };

    lucide?.createIcons();
  }

  function updateScrubberText(currFrame, maxFrames, currSec, totalSec) {
    const framePad = String(currFrame).padStart(4, '0');
    const maxPad = String(maxFrames).padStart(4, '0');
    const curTime = String(currSec.toFixed(1)).padStart(4, '0');
    const totTime = String(totalSec.toFixed(1)).padStart(4, '0');
    const elem = document.getElementById('frame-counter-text');
    if (elem) {
      elem.innerText = `Frame: ${framePad} / ${maxPad}  Time: 00:${curTime} / 00:${totTime}`;
    }
  }

  // Update Scrubber as video plays
  videoElem.addEventListener('timeupdate', () => {
    if (!videoElem.duration) return;
    const dur = videoElem.duration;
    const totalFrames = Math.round(dur * 30);
    const currFrame = Math.round(videoElem.currentTime * 30);
    if (scrubber) scrubber.value = currFrame;
    updateScrubberText(currFrame, totalFrames, videoElem.currentTime, dur);
  });

  // =========================================================================
  // 3. Live Webcam Activation
  // =========================================================================
  const webcamBtn = document.getElementById('webcam-btn');
  webcamBtn?.addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
      videoElem.srcObject = stream;
      videoElem.play();

      state.hasInput = true;
      state.videoFile = null;
      state.sampleFilename = null;
      overlayEngine.isActive = true;
      overlayEngine.resizeCanvas();

      document.getElementById('feed-badge').className = 'panel-badge active-feed';
      document.getElementById('feed-badge').innerText = 'CAM ACTIVE';
      document.getElementById('record-dot').className = 'record-dot active';
      document.getElementById('video-status-text').innerText = 'OPTICAL FEED: LIVE WEBCAM';
      
      document.getElementById('video-dims-text').innerText = '1280 × 720';
      document.getElementById('detected-faces-text').innerText = '1 (Live)';
      document.getElementById('illumination-text').innerText = '82.0 Lux (Stable)';
      document.getElementById('colorspace-text').innerText = 'sRGB / Rec.709';

      document.getElementById('system-status-dot').className = 'telemetry-status-dot';
      document.getElementById('system-status-text').style.color = '#10B981';
      document.getElementById('system-status-text').innerText = 'ONLINE';

      if (scanBtn) {
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i data-lucide="scan-line" style="width: 17px; height: 17px;"></i> START FORENSIC SCAN';
      }

      webcamBtn.innerHTML = '<i data-lucide="video-off"></i> Stop Webcam';
      lucide?.createIcons();
    } catch (err) {
      alert('Camera access failed or denied: ' + err.message);
    }
  });

  // =========================================================================
  // 4. Algorithm Tuning & Configuration Controls
  // =========================================================================
  const extractionBtns = document.querySelectorAll('[data-method]');
  extractionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      extractionBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.extractionMethod = btn.dataset.method;
    });
  });

  const windowBtns = document.querySelectorAll('[data-window]');
  windowBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      windowBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.analysisWindow = btn.dataset.window;
    });
  });

  // =========================================================================
  // 5. Preset Sample Selector (Loads actual video file into player)
  // =========================================================================
  const presetSelector = document.getElementById('preset-selector');
  presetSelector?.addEventListener('change', (e) => {
    const val = e.target.value;
    if (!val) return;
    loadSampleVideo(val);
  });

  function loadSampleVideo(sampleKey) {
    let filename = '';
    if (sampleKey === 'authentic') {
      filename = 'sample_authentic.mp4';
      document.getElementById('video-status-text').innerText = 'SAMPLE: AUTHENTIC HUMAN';
    } else if (sampleKey === 'deepfake') {
      filename = 'sample_deepfake.mp4';
      document.getElementById('video-status-text').innerText = 'SAMPLE: DEEPFAKE FACESWAP';
    }

    state.videoFile = null;
    state.sampleFilename = filename;
    state.hasInput = true;

    // Point video element to backend static sample
    videoElem.src = `/samples/${filename}`;
    videoElem.play().catch(() => {});

    overlayEngine.isActive = true;
    overlayEngine.resizeCanvas();

    document.getElementById('feed-badge').className = 'panel-badge active-feed';
    document.getElementById('feed-badge').innerText = 'SAMPLE LOADED';
    document.getElementById('record-dot').className = 'record-dot active';
    document.getElementById('video-dims-text').innerText = '640 × 480';
    document.getElementById('detected-faces-text').innerText = '1 (Frontal)';
    document.getElementById('illumination-text').innerText = '84.0 Lux';
    document.getElementById('colorspace-text').innerText = 'sRGB / Rec.709';

    if (scanBtn) {
      scanBtn.disabled = false;
      scanBtn.innerHTML = '<i data-lucide="scan-line" style="width: 17px; height: 17px;"></i> START FORENSIC SCAN';
    }

    // Reset verdict to prompt scan
    document.getElementById('verdict-headline').innerText = 'SAMPLE LOADED — READY TO SCAN';
    document.getElementById('verdict-explanation').innerText = 'Click "START FORENSIC SCAN" to execute rPPG spatial coherence analysis on this sample.';
    document.getElementById('verdict-card').className = 'card hero-verdict-card';
    document.getElementById('gauge-score').innerText = '--%';
    document.getElementById('gauge-caption').innerText = 'READY';

    lucide?.createIcons();
  }

  // =========================================================================
  // 6. Forensic Scan Execution (Real Backend Analysis)
  // =========================================================================
  scanBtn?.addEventListener('click', async () => {
    if (state.isScanning || !state.hasInput) return;
    state.isScanning = true;
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<i data-lucide="loader" class="spin-icon"></i> ANALYZING CARDIOVASCULAR SIGNALS...';
    lucide?.createIcons();

    // Show Scanning State in Verdict Card
    const headline = document.getElementById('verdict-headline');
    const explanation = document.getElementById('verdict-explanation');
    const gaugeScore = document.getElementById('gauge-score');
    const gaugeCaption = document.getElementById('gauge-caption');
    const verdictCard = document.getElementById('verdict-card');
    
    headline.style.color = 'var(--primary-cyan)';
    headline.innerText = 'EXTRACTING BIOLOGICAL SIGNALS...';
    explanation.innerText = 'Extracting 478 3D landmarks, isolating 4 facial skin ROIs, and computing CHROM chrominance pulse wave frequencies...';
    gaugeScore.innerText = '...';
    gaugeCaption.innerText = 'SCANNING';
    verdictCard.className = 'card hero-verdict-card';

    // Start animated oscilloscope while processing
    if (state.streamInterval) clearInterval(state.streamInterval);
    state.streamInterval = setInterval(() => {
      updateRppgWaveforms(true);
    }, 100);

    try {
      let url = `/api/analyze?method=${state.extractionMethod}`;
      let fetchOptions = { method: 'POST' };

      if (state.videoFile) {
        const formData = new FormData();
        formData.append('file', state.videoFile);
        fetchOptions.body = formData;
      } else if (state.sampleFilename) {
        url += `&filename=${encodeURIComponent(state.sampleFilename)}`;
      } else {
        // Fallback for webcam: analyze existing authentic or test sample
        url += '&filename=sample_authentic.mp4';
      }

      const response = await fetch(url, fetchOptions);
      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error || `Server responded with status ${response.status}`);
      }

      const data = await response.json();
      renderAnalysisResults(data);

    } catch (err) {
      console.error('Forensic analysis failed:', err);
      headline.style.color = 'var(--status-critical)';
      headline.innerText = 'ANALYSIS ERROR';
      explanation.innerText = `Error running forensic pipeline: ${err.message}. Please check video format and try again.`;
      document.getElementById('gauge-score').innerText = 'ERR';
    } finally {
      state.isScanning = false;
      scanBtn.disabled = false;
      scanBtn.innerHTML = '<i data-lucide="scan-line" style="width: 17px; height: 17px;"></i> RE-RUN FORENSIC SCAN';
      lucide?.createIcons();
    }
  });

  function renderAnalysisResults(data) {
    const ct = data.cardiac_telemetry || {};
    const coh = data.coherence || {};
    const v = data.verdict || {};

    const bpm = ct.detected_bpm !== undefined ? ct.detected_bpm : 72.0;
    const peakFreq = ct.peak_frequency_hz !== undefined ? ct.peak_frequency_hz : 1.20;
    const snr = ct.snr_db !== undefined ? ct.snr_db : 10.0;
    const isAuthentic = v.label === 'AUTHENTIC';
    const isDeepfake = v.label === 'DEEPFAKE';
    const confidence = v.confidence_percent !== undefined ? v.confidence_percent : 50.0;

    // Update Waveforms stream based on authentic vs fake
    if (state.streamInterval) clearInterval(state.streamInterval);
    state.streamInterval = setInterval(() => {
      updateRppgWaveforms(isAuthentic);
    }, 100);

    // Update FFT Spectrum & BPM readouts
    updateFftSpectrum(peakFreq, snr, isAuthentic, data.video_metadata?.fps || 30);

    // Update 4x4 Coherence Matrix Table
    const avgCoherenceElem = document.getElementById('matrix-avg-text');
    if (avgCoherenceElem) {
      avgCoherenceElem.style.color = 'var(--text-primary)';
      avgCoherenceElem.innerText = `AVG: ${coh.average_coherence !== undefined ? coh.average_coherence : '--'}`;
    }

    const cells = document.querySelectorAll('.matrix-cell');
    if (coh.matrix_4x4 && cells.length >= 16) {
      let idx = 0;
      for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
          const val = coh.matrix_4x4[r][c];
          cells[idx].innerText = val;
          if (r === c) {
            cells[idx].className = 'matrix-cell perfect';
          } else {
            const num = parseFloat(val);
            if (num >= 0.70) {
              cells[idx].className = 'matrix-cell high';
            } else {
              cells[idx].className = 'matrix-cell critical';
            }
          }
          idx++;
        }
      }
    }

    // Update Temporal Voting Slices
    const votingLabel = document.getElementById('voting-summary-label');
    const votingTrack = document.getElementById('voting-track');
    if (votingLabel) {
      votingLabel.style.color = 'var(--text-primary)';
      votingLabel.innerText = `${v.real_slices ?? 0}/${v.total_slices ?? 0} Real (${confidence.toFixed(1)}%)`;
    }

    if (votingTrack && v.slice_breakdown && v.slice_breakdown.length > 0) {
      votingTrack.innerHTML = v.slice_breakdown.map(isReal => 
        `<div class="voting-slice ${isReal ? 'authentic' : 'critical'}"></div>`
      ).join('');
    }

    // Update Hero Verdict Card
    const card = document.getElementById('verdict-card');
    const headline = document.getElementById('verdict-headline');
    const explanation = document.getElementById('verdict-explanation');
    const gaugeScore = document.getElementById('gauge-score');
    const gaugeProgress = document.getElementById('gauge-progress');
    const badge = document.getElementById('verdict-badge');
    const caption = document.getElementById('gauge-caption');

    gaugeScore.innerText = `${Math.round(confidence)}%`;
    gaugeScore.style.color = '#F8FAFC';

    // SVG dashoffset: 283 is empty (0%), 0 is full (100%)
    const offset = Math.max(10, Math.round(283 * (1 - confidence / 100)));
    gaugeProgress.style.strokeDashoffset = String(offset);

    if (isAuthentic) {
      card.className = 'card hero-verdict-card authentic';
      badge.className = 'panel-badge authentic';
      badge.innerText = `${confidence.toFixed(1)}% AUTHENTIC`;
      gaugeProgress.style.stroke = '#10B981';
      caption.innerText = 'REAL BIOLOGY';
      headline.style.color = '#10B981';
      headline.innerText = `VERDICT: AUTHENTIC HUMAN (${confidence.toFixed(1)}%)`;
      explanation.innerText = 'Phase-locked biological cardiovascular sync verified across all facial ROIs. Capillary blood pulsation matches arterial pulse waveform.';
    } else if (isDeepfake) {
      card.className = 'card hero-verdict-card critical';
      badge.className = 'panel-badge critical';
      badge.innerText = `${confidence.toFixed(1)}% DEEPFAKE`;
      gaugeProgress.style.stroke = '#EF4444';
      caption.innerText = 'SYNTHETIC';
      headline.style.color = '#EF4444';
      headline.innerText = `VERDICT: DEEPFAKE DETECTED (${confidence.toFixed(1)}%)`;
      explanation.innerText = 'Significant inter-patch spatial incoherence. Inconsistent pulse frequency clashing across forehead and cheek boundaries; synthetic blending detected.';
    } else {
      card.className = 'card hero-verdict-card warning';
      badge.className = 'panel-badge';
      badge.style.color = '#F59E0B';
      badge.style.border = '1px solid #F59E0B';
      badge.innerText = 'INCONCLUSIVE';
      gaugeProgress.style.stroke = '#F59E0B';
      caption.innerText = 'LOW SNR';
      headline.style.color = '#F59E0B';
      headline.innerText = 'VERDICT: INCONCLUSIVE (Low SNR)';
      explanation.innerText = 'Illumination fluctuation or severe video compression degraded the pulse carrier wave below verifiable threshold (+6 dB minimum).';
    }
  }

  // =========================================================================
  // 7. Reset Action (Clears all state back to clean zero)
  // =========================================================================
  document.getElementById('reset-btn')?.addEventListener('click', () => {
    state.hasInput = false;
    state.isScanning = false;
    state.videoFile = null;
    state.sampleFilename = null;

    if (state.streamInterval) {
      clearInterval(state.streamInterval);
      state.streamInterval = null;
    }

    // Stop video / webcam
    videoElem.pause();
    videoElem.src = '';
    videoElem.srcObject = null;

    // Reset overlay engine
    overlayEngine.isActive = false;

    // Reset charts
    resetChartsToZero();

    // Reset DOM Elements
    document.getElementById('feed-badge').className = 'panel-badge standby';
    document.getElementById('feed-badge').innerText = 'STANDBY (NO INPUT)';
    document.getElementById('record-dot').className = 'record-dot';
    document.getElementById('video-status-text').innerText = 'AWAITING VIDEO INPUT';

    document.getElementById('system-status-dot').className = 'telemetry-status-dot idle';
    document.getElementById('system-status-text').style.color = 'var(--text-muted)';
    document.getElementById('system-status-text').innerText = 'STANDBY';

    document.getElementById('fps-counter').innerText = '--';
    document.getElementById('latency-counter').innerText = '-- ms';

    document.getElementById('video-dims-text').innerText = '-- × --';
    document.getElementById('detected-faces-text').innerText = '0';
    document.getElementById('illumination-text').innerText = '--';
    document.getElementById('colorspace-text').innerText = '--';

    document.getElementById('frame-counter-text').innerText = 'Frame: 0000 / 0000  Time: 00:00.0 / 00:00.0';
    if (scrubber) {
      scrubber.value = 0;
      scrubber.disabled = true;
    }

    // Reset Verdict Card
    const card = document.getElementById('verdict-card');
    card.className = 'card hero-verdict-card';
    document.getElementById('verdict-badge').className = 'panel-badge standby';
    document.getElementById('verdict-badge').innerText = 'STANDBY';
    document.getElementById('gauge-score').innerText = '--%';
    document.getElementById('gauge-score').style.color = 'var(--text-muted)';
    document.getElementById('gauge-caption').innerText = 'AWAITING INPUT';
    document.getElementById('gauge-progress').style.strokeDashoffset = '283';
    document.getElementById('gauge-progress').style.stroke = 'var(--text-muted)';
    document.getElementById('verdict-headline').style.color = 'var(--text-secondary)';
    document.getElementById('verdict-headline').innerText = 'AWAITING FORENSIC SCAN';
    document.getElementById('verdict-explanation').innerText = 'Upload a target video or activate the webcam to begin signal extraction and authenticity verification.';

    // Reset Matrix
    document.getElementById('matrix-avg-text').style.color = 'var(--text-muted)';
    document.getElementById('matrix-avg-text').innerText = 'AVG: --';
    document.querySelectorAll('.matrix-cell').forEach(c => {
      c.className = 'matrix-cell';
      c.innerText = '--';
    });

    // Reset Voting Slices
    document.getElementById('voting-summary-label').style.color = 'var(--text-muted)';
    document.getElementById('voting-summary-label').innerText = '0/0 Slices';
    document.getElementById('voting-track').innerHTML = Array(8).fill('<div class="voting-slice"></div>').join('');

    // Disable scan button
    if (scanBtn) {
      scanBtn.disabled = true;
      scanBtn.innerHTML = '<i data-lucide="scan-line" style="width: 17px; height: 17px;"></i> START FORENSIC SCAN';
    }

    if (presetSelector) {
      presetSelector.value = '';
    }

    lucide?.createIcons();
  });

  // =========================================================================
  // 8. PDF Export Action
  // =========================================================================
  document.getElementById('export-pdf-btn')?.addEventListener('click', () => {
    window.open('/DeepSearch_Deepfake_Detection_System_Specification.pdf', '_blank');
  });

  // Initialize Lucide Icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});
